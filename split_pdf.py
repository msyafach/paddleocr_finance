"""split_pdf.py
A command-line utility for splitting a PDF into individual single-page files.

This script relies on the *PyMuPDF* library. Install it (managed by ``uv``) with:

    uv add pymupdf

Usage
-----
From the terminal:

    uv run split_pdf.py --input path/to/file.pdf --output-dir out/dir

The script will create ``out/dir`` (if it does not exist) and write one
PDF per page named ``<original_name>_page_<n>.pdf``.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import List

import fitz  # PyMuPDF

LOGGER = logging.getLogger(__name__)


def split_pdf(source_path: Path, output_dir: Path) -> List[Path]:
    """Split *source_path* into single-page PDFs inside *output_dir* using PyMuPDF."""

    if not source_path.exists():
        raise FileNotFoundError(f"Input file not found: {source_path}")

    if source_path.suffix.lower() != ".pdf":
        raise ValueError("Input file must have a .pdf extension")

    reader = fitz.open(source_path)  # type: ignore[arg-type]
    if reader.page_count == 0:
        raise ValueError("The PDF contains no pages to split")

    output_dir.mkdir(parents=True, exist_ok=True)
    generated_files: List[Path] = []

    for page_number in range(reader.page_count):
        new_doc = fitz.open()
        new_doc.insert_pdf(reader, from_page=page_number, to_page=page_number)
        output_file = output_dir / f"{source_path.stem}_page_{page_number + 1}.pdf"
        new_doc.save(output_file)
        new_doc.close()
        generated_files.append(output_file)
        LOGGER.debug("Wrote %s", output_file)

    reader.close()
    return generated_files


def _parse_arguments(argv: List[str]) -> argparse.Namespace:  # noqa: D401
    """Configure and parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="split_pdf",
        description="Split a PDF into individual pages.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        required=True,
        help="Path to the PDF file to split.",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=Path("pages"),
        help="Directory to store the resulting single-page PDFs.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose (debug) logging output.",
    )
    return parser.parse_args(argv)


def main() -> None:  # noqa: D401
    """Entry-point for command-line execution."""

    args = _parse_arguments(sys.argv[1:])
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s | %(message)s",
    )

    try:
        generated = split_pdf(args.input, args.output_dir)
    except (FileNotFoundError, ValueError) as exc:
        LOGGER.error("%s", exc)
        sys.exit(1)

    LOGGER.info("Successfully created %d files in %s", len(generated), args.output_dir)


if __name__ == "__main__":
    main()
