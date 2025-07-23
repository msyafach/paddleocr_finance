"""combine_pdf.py
Merge multiple PDF files into a single output document using PyMuPDF (fitz).

This script can be invoked from the command line:

    uv run combine_pdf.py output.pdf input1.pdf input2.pdf  # basic usage

It also supports passing directories (optionally recursive) and includes
flags for overwriting an existing output file and verbose logging.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import List

import fitz  # PyMuPDF

LOGGER = logging.getLogger(__name__)


def collect_pdfs(paths: List[Path], recursive: bool = False) -> List[Path]:
    """Collect PDF files from a list of paths.

    Args:
        paths: A list of file or directory paths provided by the user.
        recursive: If *True*, traverse directories recursively to locate PDFs.

    Returns:
        A **sorted** list of absolute ``Path`` objects pointing to PDF files.

    Raises:
        FileNotFoundError: If any provided *file* path does not exist.
    """
    pdf_files: list[Path] = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"Path not found: {path}")

        if path.is_dir():
            pattern = "**/*.pdf" if recursive else "*.pdf"
            pdf_files.extend(sorted(path.glob(pattern)))
            continue

        if path.suffix.lower() == ".pdf":
            pdf_files.append(path)
        else:
            LOGGER.warning("Skipping non-PDF file: %s", path)

    # Remove duplicates while preserving order
    seen: set[Path] = set()
    unique_pdfs: list[Path] = []
    for pdf in pdf_files:
        if pdf not in seen:
            seen.add(pdf)
            unique_pdfs.append(pdf.resolve())

    # Finally, sort using a natural key so that page_10 comes *after* page_9.
    def _natural_key(path: Path) -> List[int | str]:
        """Return a key for natural sorting based on the filename.

        Splits the filename into digit and non-digit parts to ensure that
        numeric page suffixes (e.g. ``_page_10``) are sorted correctly.
        """
        parts: list[str] = re.split(r"(\d+)", path.stem)
        processed: list[int | str] = [int(part) if part.isdigit() else part.lower() for part in parts]
        return processed

    return sorted(unique_pdfs, key=_natural_key)


def merge_pdfs(input_paths: List[Path], output_path: Path, overwrite: bool = False) -> None:
    """Merge multiple PDFs into a single document.

    Args:
        input_paths: Ordered list of PDF files to merge.
        output_path: Destination file for the combined PDF.
        overwrite: If *True*, replace *output_path* if it exists.

    Raises:
        ValueError: If *input_paths* is empty.
        FileExistsError: If *output_path* already exists and *overwrite* is *False*.
    """
    if not input_paths:
        raise ValueError("No PDF files were provided for merging.")

    if output_path.exists() and not overwrite:
        raise FileExistsError(
            f"Output file '{output_path}' already exists. Use --overwrite to replace it."
        )

    LOGGER.info("Merging %d PDFs into %s", len(input_paths), output_path)

    output_pdf = fitz.open()
    try:
        for pdf_file in input_paths:
            LOGGER.debug("Processing %s", pdf_file)
            with fitz.open(pdf_file) as src:
                output_pdf.insert_pdf(src)
        output_pdf.save(output_path)
        LOGGER.info("Successfully saved merged PDF to %s", output_path)
    finally:
        output_pdf.close()


def parse_arguments(argv: List[str] | None = None) -> argparse.Namespace:  # noqa: D401
    """Build and parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="combine_pdf",
        description="Combine multiple PDF files into one output PDF using PyMuPDF.",
    )
    parser.add_argument(
        "output",
        type=Path,
        help="Path to the combined output PDF file.",
    )
    parser.add_argument(
        "inputs",
        type=Path,
        nargs="+",
        help="Input PDF files and/or directories containing PDF files.",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively search provided directories for PDF files.",
    )
    parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help="Overwrite the output file if it already exists.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase output verbosity (e.g., -v, -vv).",
    )
    return parser.parse_args(argv)


def _configure_logging(verbosity_level: int) -> None:
    """Configure the *logging* module based on requested verbosity."""
    log_level = logging.WARNING  # default
    if verbosity_level == 1:
        log_level = logging.INFO
    elif verbosity_level >= 2:
        log_level = logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s",
    )


def main(argv: List[str] | None = None) -> None:  # noqa: D401
    """Entry point for *combine_pdf.py* when executed as a script."""
    args = parse_arguments(argv)
    _configure_logging(args.verbose)

    try:
        pdf_files = collect_pdfs(args.inputs, recursive=args.recursive)
        merge_pdfs(pdf_files, args.output, overwrite=args.overwrite)
    except Exception as exc:  # pylint: disable=broad-except
        LOGGER.error("Error: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
