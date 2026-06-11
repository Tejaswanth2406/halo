"""
src/ingestion/parsers/pdf_parser.py

Responsibility: Extract raw page text from a PDF file.
"""

import pdfplumber
from dataclasses import dataclass


@dataclass
class ParsedPage:
    page_number: int
    text: str


class PDFParser:

    def parse(self, file_path: str) -> list[ParsedPage]:
        """
        Extract text from every page of a PDF.

        Returns a list of ParsedPage objects, one per page.
        Skips blank pages silently.
        """
        results = []

        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text() or ""
                    text = text.strip()
                    if text:
                        results.append(ParsedPage(page_number=i, text=text))
        except Exception as e:
            print(f"[PDFParser] Failed to parse {file_path}: {e}")

        return results