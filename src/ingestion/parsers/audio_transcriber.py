"""
Production-grade audio transcription using OpenAI Whisper.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

class WhisperModel(str, Enum):
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    LARGE_V2 = "large-v2"
    LARGE_V3 = "large-v3"


class ComputeDevice(str, Enum):
    CPU = "cpu"
    CUDA = "cuda"
    AUTO = "auto"   # picks CUDA if available, else CPU


@dataclass
class TranscribeConfig:
    """Runtime configuration for the transcriber."""
    model: WhisperModel = WhisperModel.BASE
    device: ComputeDevice = ComputeDevice.AUTO
    language: Optional[str] = None          # ISO 639-1 e.g. "en"; None = auto-detect
    task: str = "transcribe"                # "transcribe" | "translate" (→ English)
    # Decoding
    temperature: float = 0.0               # 0 = greedy; >0 enables sampling
    beam_size: int = 5
    best_of: int = 5                        # candidates when temperature > 0
    # Output
    word_timestamps: bool = False           # per-word start/end times
    verbose: bool = False                   # Whisper internal progress logging
    # Pre-processing
    fp16: bool = True                       # half-precision on GPU; auto-disabled on CPU
    condition_on_previous_text: bool = True


@dataclass
class WordTimestamp:
    word: str
    start: float    # seconds
    end: float
    probability: float


@dataclass
class Segment:
    id: int
    text: str
    start: float    # seconds
    end: float
    avg_log_prob: float
    no_speech_prob: float
    words: list[WordTimestamp] = field(default_factory=list)

    @property
    def duration(self) -> float:
        return self.end - self.start


@dataclass
class TranscribeResult:
    """Structured output of a single transcription run."""
    text: str                           # full concatenated transcript
    language: str                       # detected or forced language
    segments: list[Segment]
    # Convenience
    duration_s: float                   # total audio duration in seconds
    word_count: int
    # Meta
    model_used: str
    source_path: str
    processing_time_ms: float
    real_time_factor: float             # processing_time / audio_duration
    warnings: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return bool(self.text.strip())

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "language": self.language,
            "duration_s": self.duration_s,
            "word_count": self.word_count,
            "segments": [
                {
                    "id": s.id,
                    "text": s.text,
                    "start": s.start,
                    "end": s.end,
                    "avg_log_prob": s.avg_log_prob,
                    "no_speech_prob": s.no_speech_prob,
                    "words": [
                        {
                            "word": w.word,
                            "start": w.start,
                            "end": w.end,
                            "probability": w.probability,
                        }
                        for w in s.words
                    ],
                }
                for s in self.segments
            ],
            "model_used": self.model_used,
            "source_path": self.source_path,
            "processing_time_ms": self.processing_time_ms,
            "real_time_factor": self.real_time_factor,
            "warnings": self.warnings,
            "success": self.success,
        }

    def to_srt(self) -> str:
        """Export transcript as SRT subtitle format."""
        lines = []
        for seg in self.segments:
            lines.append(str(seg.id + 1))
            lines.append(f"{_fmt_srt_time(seg.start)} --> {_fmt_srt_time(seg.end)}")
            lines.append(seg.text.strip())
            lines.append("")
        return "\n".join(lines)

    def to_vtt(self) -> str:
        """Export transcript as WebVTT subtitle format."""
        lines = ["WEBVTT", ""]
        for seg in self.segments:
            lines.append(f"{_fmt_vtt_time(seg.start)} --> {_fmt_vtt_time(seg.end)}")
            lines.append(seg.text.strip())
            lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core transcriber
# ---------------------------------------------------------------------------

class AudioTranscriber:
    """
    Production-ready audio transcriber built on OpenAI Whisper.

    Features
    --------
    - All Whisper model sizes (tiny → large-v3) with auto device selection.
    - Language auto-detection or forced language input.
    - Translation mode (any language → English).
    - Per-segment metadata: timestamps, avg log-prob, no-speech probability.
    - Optional word-level timestamps.
    - SRT and WebVTT subtitle export.
    - Lazy model loading — model is loaded on first transcription call or
      explicitly via `.load_model()`.
    - Safe result type; never raises on bad input.

    Usage
    -----
    >>> t = AudioTranscriber()
    >>> result = t.transcribe("interview.mp3")
    >>> print(result.text)
    >>> print(result.to_srt())

    >>> cfg = TranscribeConfig(model=WhisperModel.LARGE_V3, language="fr",
    ...                        word_timestamps=True)
    >>> t = AudioTranscriber(config=cfg)
    >>> result = t.transcribe("lecture.wav")
    >>> for seg in result.segments:
    ...     print(f"[{seg.start:.1f}s] {seg.text}")
    """

    _SUPPORTED_EXTENSIONS = {
        ".mp3", ".mp4", ".wav", ".flac", ".ogg", ".m4a",
        ".aac", ".wma", ".opus", ".webm", ".mkv", ".avi",
    }

    def __init__(self, config: Optional[TranscribeConfig] = None) -> None:
        self.config = config or TranscribeConfig()
        self._model = None  # lazy-loaded

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_model(self) -> None:
        """
        Explicitly pre-load the Whisper model into memory.
        Called automatically on first `.transcribe()` if not called manually.
        """
        if self._model is not None:
            return
        try:
            import whisper
        except ImportError:
            raise RuntimeError(
                "openai-whisper is not installed. Run: pip install openai-whisper"
            )

        device = self._resolve_device()
        logger.info("Loading Whisper model '%s' on %s …", self.config.model.value, device)
        self._model = whisper.load_model(self.config.model.value, device=device)
        logger.info("Model loaded.")

    def transcribe(self, audio_path: str | Path) -> TranscribeResult:
        """
        Transcribe the audio file at *audio_path*.

        Parameters
        ----------
        audio_path:
            Path to a supported audio/video file.

        Returns
        -------
        TranscribeResult
            Always returns a TranscribeResult; check `.success` for whether
            meaningful text was produced.
        """
        path = Path(audio_path)
        start = time.perf_counter()
        warnings: list[str] = []

        self._validate_path(path, warnings)
        if not path.exists():
            return self._empty_result(str(path), start, warnings)

        try:
            self.load_model()
        except RuntimeError as exc:
            warnings.append(str(exc))
            return self._empty_result(str(path), start, warnings)

        cfg = self.config
        decode_options: dict = {
            "task": cfg.task,
            "beam_size": cfg.beam_size,
            "best_of": cfg.best_of,
            "temperature": cfg.temperature,
            "word_timestamps": cfg.word_timestamps,
            "verbose": cfg.verbose,
            "condition_on_previous_text": cfg.condition_on_previous_text,
            "fp16": cfg.fp16 and self._resolve_device() == "cuda",
        }
        if cfg.language:
            decode_options["language"] = cfg.language

        try:
            raw = self._model.transcribe(str(path), **decode_options)
        except Exception as exc:
            logger.error("Whisper transcription failed for %s: %s", path, exc)
            warnings.append(f"Transcription error: {exc}")
            return self._empty_result(str(path), start, warnings)

        elapsed_ms = (time.perf_counter() - start) * 1000

        segments = self._parse_segments(raw.get("segments", []))
        full_text: str = raw.get("text", "").strip()
        language: str = raw.get("language", cfg.language or "unknown")
        duration_s = segments[-1].end if segments else 0.0
        rtf = (elapsed_ms / 1000) / duration_s if duration_s > 0 else 0.0

        if not full_text:
            warnings.append(
                "Transcript is empty — audio may be silent, corrupt, or "
                "in a language Whisper could not detect."
            )

        logger.debug(
            "Transcribed %s: lang=%s words=%d duration=%.1fs rtf=%.2f",
            path, language, len(full_text.split()), duration_s, rtf,
        )

        return TranscribeResult(
            text=full_text,
            language=language,
            segments=segments,
            duration_s=round(duration_s, 3),
            word_count=len(full_text.split()),
            model_used=self.config.model.value,
            source_path=str(path),
            processing_time_ms=round(elapsed_ms, 2),
            real_time_factor=round(rtf, 3),
            warnings=warnings,
        )

    def transcribe_batch(self, audio_paths: list[str | Path]) -> list[TranscribeResult]:
        """Transcribe multiple files, reusing the loaded model."""
        self.load_model()
        return [self.transcribe(p) for p in audio_paths]

    # ------------------------------------------------------------------
    # Segment parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_segments(raw_segments: list[dict]) -> list[Segment]:
        segments = []
        for seg in raw_segments:
            words = []
            for w in seg.get("words", []):
                words.append(WordTimestamp(
                    word=w.get("word", ""),
                    start=w.get("start", 0.0),
                    end=w.get("end", 0.0),
                    probability=w.get("probability", 0.0),
                ))
            segments.append(Segment(
                id=seg.get("id", 0),
                text=seg.get("text", ""),
                start=seg.get("start", 0.0),
                end=seg.get("end", 0.0),
                avg_log_prob=seg.get("avg_logprob", 0.0),
                no_speech_prob=seg.get("no_speech_prob", 0.0),
                words=words,
            ))
        return segments

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _resolve_device(self) -> str:
        if self.config.device == ComputeDevice.AUTO:
            try:
                import torch
                return "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                return "cpu"
        return self.config.device.value

    def _validate_path(self, path: Path, warnings: list[str]) -> None:
        if not path.exists():
            warnings.append(f"File not found: {path}")
            return
        if path.suffix.lower() not in self._SUPPORTED_EXTENSIONS:
            warnings.append(
                f"Extension '{path.suffix}' may not be supported. "
                f"Supported: {', '.join(sorted(self._SUPPORTED_EXTENSIONS))}"
            )

    def _empty_result(
        self, source: str, start: float, warnings: list[str]
    ) -> TranscribeResult:
        return TranscribeResult(
            text="",
            language="unknown",
            segments=[],
            duration_s=0.0,
            word_count=0,
            model_used=self.config.model.value,
            source_path=source,
            processing_time_ms=round((time.perf_counter() - start) * 1000, 2),
            real_time_factor=0.0,
            warnings=warnings,
        )


# ---------------------------------------------------------------------------
# Subtitle helpers
# ---------------------------------------------------------------------------

def _fmt_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def _fmt_vtt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02}:{m:02}:{s:02}.{ms:03}"