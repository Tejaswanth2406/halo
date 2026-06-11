"""
Production-grade OCR extraction from images and scanned documents.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

class OCRLanguage(str, Enum):
    ENGLISH = "eng"
    SPANISH = "spa"
    FRENCH = "fra"
    GERMAN = "deu"
    CHINESE_SIMPLIFIED = "chi_sim"
    ARABIC = "ara"


class OCRMode(int, Enum):
    """Tesseract Page Segmentation Mode (PSM)."""
    AUTO = 3          # Fully automatic page segmentation (default)
    SINGLE_BLOCK = 6  # Assume a single uniform block of text
    SINGLE_LINE = 7   # Treat the image as a single text line
    SINGLE_WORD = 8   # Treat the image as a single word
    SPARSE_TEXT = 11  # Find as much text as possible in no particular order


@dataclass
class OCRConfig:
    """Runtime configuration for the OCR engine."""
    language: OCRLanguage = OCRLanguage.ENGLISH
    mode: OCRMode = OCRMode.AUTO
    # Pre-processing toggles
    enhance_contrast: bool = True
    denoise: bool = True
    deskew: bool = False          # requires scikit-image; opt-in
    upscale_threshold: int = 1500 # upscale if shorter side < this many pixels
    # Tesseract extras (passed verbatim via --psm / -l flags)
    extra_config: str = ""


@dataclass
class OCRResult:
    """Return value of a single extraction call."""
    text: str
    confidence: float            # 0–100, mean word confidence (-1 if unavailable)
    source_path: str
    processing_time_ms: float
    warnings: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return bool(self.text)


# ---------------------------------------------------------------------------
# Core engine
# ---------------------------------------------------------------------------

class ImageOCR:
    """
    Production-ready OCR engine wrapping Tesseract via pytesseract.

    Features
    --------
    - Configurable language, page-segmentation mode, and pre-processing.
    - Automatic contrast enhancement and denoising.
    - Optional upscaling for low-resolution inputs.
    - Per-call confidence scoring (mean word confidence).
    - Structured OCRResult return type instead of bare strings.
    - Full logging and warning capture.

    Usage
    -----
    >>> ocr = ImageOCR()
    >>> result = ocr.extract("scan.png")
    >>> print(result.text, result.confidence)

    >>> cfg = OCRConfig(language=OCRLanguage.FRENCH, enhance_contrast=False)
    >>> ocr = ImageOCR(config=cfg)
    >>> result = ocr.extract("document.tiff")
    """

    _SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".gif", ".webp"}

    def __init__(self, config: Optional[OCRConfig] = None) -> None:
        self.config = config or OCRConfig()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract(self, image_path: str | Path) -> OCRResult:
        """
        Extract text from *image_path*.

        Parameters
        ----------
        image_path:
            Absolute or relative path to an image file.

        Returns
        -------
        OCRResult
            Always returns an OCRResult; check `.success` or `.text` for
            whether extraction produced output.
        """
        path = Path(image_path)
        warnings: list[str] = []
        start = time.perf_counter()

        # --- Validation ---
        self._validate_path(path, warnings)

        # --- Load ---
        try:
            image = Image.open(path).convert("RGB")
        except Exception as exc:
            logger.error("Failed to open image %s: %s", path, exc)
            return self._empty_result(str(path), start, warnings, str(exc))

        # --- Pre-processing ---
        image = self._preprocess(image, warnings)

        # --- OCR ---
        try:
            tess_config = self._build_tess_config()
            lang = self.config.language.value

            raw_text: str = pytesseract.image_to_string(
                image, lang=lang, config=tess_config
            )
            confidence = self._get_confidence(image, lang, tess_config)
        except pytesseract.TesseractNotFoundError:
            msg = "Tesseract not found. Install it and ensure it's on PATH."
            logger.error(msg)
            return self._empty_result(str(path), start, warnings, msg)
        except Exception as exc:
            logger.error("Tesseract failed on %s: %s", path, exc)
            return self._empty_result(str(path), start, warnings, str(exc))

        elapsed = (time.perf_counter() - start) * 1000
        text = raw_text.strip()

        if not text:
            warnings.append("OCR produced no text — check image quality or language setting.")

        logger.debug(
            "OCR complete: path=%s chars=%d confidence=%.1f ms=%.0f",
            path, len(text), confidence, elapsed,
        )

        return OCRResult(
            text=text,
            confidence=confidence,
            source_path=str(path),
            processing_time_ms=elapsed,
            warnings=warnings,
        )

    def extract_batch(self, image_paths: list[str | Path]) -> list[OCRResult]:
        """Extract text from multiple images, returning one result per path."""
        return [self.extract(p) for p in image_paths]

    # ------------------------------------------------------------------
    # Pre-processing helpers
    # ------------------------------------------------------------------

    def _preprocess(self, image: Image.Image, warnings: list[str]) -> Image.Image:
        cfg = self.config

        # Upscale tiny images
        min_side = min(image.width, image.height)
        if min_side < cfg.upscale_threshold:
            scale = cfg.upscale_threshold / min_side
            new_size = (int(image.width * scale), int(image.height * scale))
            image = image.resize(new_size, Image.LANCZOS)
            warnings.append(
                f"Image upscaled {scale:.1f}× to {new_size} for better OCR accuracy."
            )

        # Convert to grayscale for filter operations
        gray = image.convert("L")

        if cfg.denoise:
            gray = gray.filter(ImageFilter.MedianFilter(size=3))

        if cfg.enhance_contrast:
            gray = ImageEnhance.Contrast(gray).enhance(2.0)
            gray = ImageEnhance.Sharpness(gray).enhance(1.5)

        if cfg.deskew:
            gray = self._deskew(gray, warnings)

        return gray

    @staticmethod
    def _deskew(image: Image.Image, warnings: list[str]) -> Image.Image:
        try:
            import numpy as np
            from skimage.transform import rotate
            from skimage.feature import canny
            from skimage.transform import hough_line, hough_line_peaks

            arr = np.array(image)
            edges = canny(arr, sigma=2)
            h, angles, dists = hough_line(edges)
            _, peak_angles, _ = hough_line_peaks(h, angles, dists, num_peaks=20)

            if len(peak_angles) == 0:
                return image

            dominant = np.rad2deg(np.median(peak_angles))
            skew = dominant - 90 if dominant > 45 else dominant

            if abs(skew) > 0.5:
                rotated = rotate(arr, angle=skew, resize=True, cval=255)
                return Image.fromarray((rotated * 255).astype(np.uint8))
        except ImportError:
            warnings.append("scikit-image not installed; skipping deskew.")
        except Exception as exc:
            warnings.append(f"Deskew failed ({exc}); skipping.")

        return image

    # ------------------------------------------------------------------
    # Confidence scoring
    # ------------------------------------------------------------------

    @staticmethod
    def _get_confidence(
        image: Image.Image, lang: str, tess_config: str
    ) -> float:
        try:
            data = pytesseract.image_to_data(
                image, lang=lang, config=tess_config,
                output_type=pytesseract.Output.DICT,
            )
            confs = [c for c in data["conf"] if isinstance(c, (int, float)) and c >= 0]
            return round(sum(confs) / len(confs), 1) if confs else -1.0
        except Exception:
            return -1.0

    # ------------------------------------------------------------------
    # Misc helpers
    # ------------------------------------------------------------------

    def _build_tess_config(self) -> str:
        parts = [f"--psm {self.config.mode.value}"]
        if self.config.extra_config:
            parts.append(self.config.extra_config)
        return " ".join(parts)

    def _validate_path(self, path: Path, warnings: list[str]) -> None:
        if not path.exists():
            warnings.append(f"File not found: {path}")
            return
        if path.suffix.lower() not in self._SUPPORTED_EXTENSIONS:
            warnings.append(
                f"Extension '{path.suffix}' may not be supported. "
                f"Supported: {', '.join(sorted(self._SUPPORTED_EXTENSIONS))}"
            )

    @staticmethod
    def _empty_result(
        source: str, start: float, warnings: list[str], error_msg: str
    ) -> OCRResult:
        warnings.append(f"Extraction error: {error_msg}")
        return OCRResult(
            text="",
            confidence=-1.0,
            source_path=source,
            processing_time_ms=(time.perf_counter() - start) * 1000,
            warnings=warnings,
        )