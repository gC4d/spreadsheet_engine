"""Base adapter protocol for all spreadsheet formats."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any, Protocol

from ..core.models.spreadsheet import Spreadsheet


class SpreadsheetAdapter(Protocol):
    """
    Protocol that all spreadsheet adapters must implement.

    Adapters translate the format-agnostic core models into
    format-specific representations (XLSX, CSV, PDF, etc.).
    """

    def render(self, spreadsheet: Spreadsheet, autofit: bool = True) -> Any:
        """
        Render spreadsheet to format-specific workbook object.

        Args:
            spreadsheet: Spreadsheet model to render
            autofit: Whether to auto-fit column widths

        Returns:
            Format-specific workbook object
        """
        ...

    def to_bytes(self, workbook: Any) -> bytes:
        """
        Convert workbook to bytes.

        Args:
            workbook: Format-specific workbook object

        Returns:
            Bytes representation
        """
        ...

    def to_file(self, workbook: Any, path: Path) -> None:
        """
        Save workbook to file.

        Args:
            workbook: Format-specific workbook object
            path: Output file path
        """
        ...

    def to_stream(self, workbook: Any, stream: BytesIO) -> None:
        """
        Write workbook to stream.

        Args:
            workbook: Format-specific workbook object
            stream: Output stream
        """
        ...
