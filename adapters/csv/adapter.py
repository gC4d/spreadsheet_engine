"""CSV adapter implementation."""

from __future__ import annotations

import csv
from io import BytesIO, StringIO
from pathlib import Path
from typing import Any

from ...core.models.spreadsheet import Spreadsheet


class CSVAdapter:
    """
    CSV adapter.

    Limitations:
    - Only first sheet is exported
    - No styling or formatting
    - No formulas (only values)
    - No merged cells
    """

    def render(self, spreadsheet: Spreadsheet, autofit: bool = True) -> StringIO:
        """Render spreadsheet to CSV (first sheet only)."""
        if not spreadsheet.sheets:
            return StringIO()

        sheet = spreadsheet.sheets[0]

        buffer = StringIO()
        writer = csv.writer(buffer)

        for table in sheet.tables:
            if table.has_title and table.title:
                writer.writerow([f"# {table.title.value}"])

            if table.has_headers:
                header_row = [cell.value for cell in table.headers]
                writer.writerow(header_row)

            for row_cells in table.iter_rows():
                data_row = [cell.display_value for cell in row_cells]
                writer.writerow(data_row)

            writer.writerow([])

        buffer.seek(0)
        return buffer

    def to_bytes(self, workbook: StringIO) -> bytes:
        """Convert CSV to bytes."""
        return workbook.getvalue().encode('utf-8')

    def to_file(self, workbook: StringIO, path: Path) -> None:
        """Save CSV to file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(workbook.getvalue(), encoding='utf-8')

    def to_stream(self, workbook: StringIO, stream: BytesIO) -> None:
        """Write CSV to stream."""
        stream.write(workbook.getvalue().encode('utf-8'))
        stream.seek(0)
