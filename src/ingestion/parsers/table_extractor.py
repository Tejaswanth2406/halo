"""
Table extraction from PDFs using Camelot
"""

from typing import List, Dict, Any
import camelot


class TableExtractor:
    """Extract and structure tables from PDF documents."""

    def extract_tables(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract all tables from a PDF.

        Args:
            file_path: Path to PDF file

        Returns:
            List of extracted tables
        """

        extracted_tables = []

        try:
            # Try lattice mode first (works best for bordered tables)
            tables = camelot.read_pdf(
                file_path,
                pages="all",
                flavor="lattice"
            )

            # Fallback to stream mode if no tables found
            if len(tables) == 0:
                tables = camelot.read_pdf(
                    file_path,
                    pages="all",
                    flavor="stream"
                )

            for table in tables:
                df = table.df

                # Skip empty tables
                if df.empty:
                    continue

                extracted_tables.append(
                    {
                        "page": table.page,
                        "headers": df.iloc[0].tolist(),
                        "rows": df.iloc[1:].values.tolist(),
                        "shape": df.shape,
                    }
                )

        except Exception as e:
            print(f"Table extraction failed: {e}")

        return extracted_tables