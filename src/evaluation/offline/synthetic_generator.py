"""Synthetic dataset generator"""

from typing import List, Dict, Any
import random


class SyntheticGenerator:
    """Generate synthetic test cases from docs"""

    async def generate(
        self,
        documents: List[str],
        num_samples: int = 100,
    ) -> List[Dict[str, Any]]:
        """Generate synthetic questions"""

        if not documents:
            return []

        samples = []

        question_templates = [
            "What is the main purpose of {topic}?",
            "Summarize the key points about {topic}.",
            "How does {topic} work?",
            "What are the benefits of {topic}?",
            "Explain {topic} in detail.",
            "What are the important concepts related to {topic}?",
            "What problem does {topic} solve?",
        ]

        for idx in range(num_samples):
            doc = documents[idx % len(documents)]

            text = str(doc).strip()
            if not text:
                continue

            words = text.split()
            topic = " ".join(words[: min(5, len(words))])

            question = random.choice(question_templates).format(
                topic=topic
            )

            samples.append(
                {
                    "id": idx + 1,
                    "question": question,
                    "context": text,
                    "ground_truth": text[:500],
                    "metadata": {
                        "source_document": idx % len(documents),
                        "synthetic": True,
                    },
                }
            )

        return samples