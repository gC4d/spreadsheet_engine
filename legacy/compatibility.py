"""Backward compatibility bridge to old SpreadsheetBuilder API."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..adapters.registry import SpreadsheetFormat
from ..core.models.position import CellPosition
from ..core.styles.cell_style import (
    Alignment,
    CellStyle,
    Color,
    Fill,
    Font,
    HorizontalAlignment,
    PatternFill,
    VerticalAlignment,
)
from ..core.templates.data import SheetData, SpreadsheetData, TableData
from ..core.templates.template import (
    ColumnDefinition,
    SheetTemplate,
    SpreadsheetTemplate,
    TableTemplate,
)
from ..engine.renderer import SpreadsheetRenderer


class LegacySpreadsheetBuilder:
    """
    Backward compatibility wrapper for old SpreadsheetBuilder API.

    This class provides the same interface as the old builder but uses
    the new engine internally.

    Usage:
        # Old code continues to work:
        schema = {
            "filename": "report.xlsx",
            "sheets": [...]
        }
        builder = LegacySpreadsheetBuilder(schema)
        builder.save("output.xlsx")
    """

    def __init__(
        self,
        schema: Union[Dict[str, Any], str],
        format: Optional[str] = None,
    ) -> None:
        """
        Initialize builder with old-style schema.

        Args:
            schema: Old-style schema dictionary or JSON string
            format: Output format (xlsx, csv)
        """
        if isinstance(schema, str):
            import json
            schema = json.loads(schema)

        self.schema = schema
        self.format = SpreadsheetFormat(format.lower()) if format else SpreadsheetFormat.XLSX
        self.template: Optional[SpreadsheetTemplate] = None
        self.data: Optional[SpreadsheetData] = None

        self._convert_schema()

    def _convert_schema(self) -> None:
        """Convert old schema to new template + data."""
        sheets_templates = []
        sheets_data = {}

        for old_sheet in self.schema.get("sheets", []):
            sheet_template, sheet_data = self._convert_sheet(old_sheet)
            sheets_templates.append(sheet_template)
            sheets_data[old_sheet["name"]] = sheet_data

        self.template = SpreadsheetTemplate(sheets=sheets_templates)

        spreadsheet_data = SpreadsheetData()
        for sheet_name, sheet_data in sheets_data.items():
            spreadsheet_data.add_sheet_data(sheet_name, sheet_data)

        self.data = spreadsheet_data

    def _convert_sheet(self, old_sheet: Dict) -> tuple[SheetTemplate, SheetData]:
        """Convert old sheet schema to template + data."""
        tables_templates = []
        sheet_data = SheetData()

        for old_table in old_sheet.get("tables", []):
            table_template, table_data = self._convert_table(old_table)
            tables_templates.append(table_template)
            sheet_data.add_table_data(table_template.name, table_data)

        freeze_panes = old_sheet.get("freeze_panes")
        freeze_position = None
        if freeze_panes:
            if isinstance(freeze_panes, str):
                freeze_position = CellPosition.from_a1(freeze_panes)
            elif isinstance(freeze_panes, dict):
                rows = freeze_panes.get("rows", 0)
                cols = freeze_panes.get("columns", 0)
                freeze_position = CellPosition(rows + 1, cols + 1)

        sheet_template = SheetTemplate(
            name=old_sheet["name"],
            tables=tables_templates,
            freeze_panes=freeze_position,
        )

        return sheet_template, sheet_data

    def _convert_table(self, old_table: Dict) -> tuple[TableTemplate, TableData]:
        """Convert old table schema to template + data."""
        headers = old_table.get("headers", [])
        columns = []

        for idx, header in enumerate(headers):
            if isinstance(header, str):
                col = ColumnDefinition(
                    key=f"col_{idx}",
                    label=header,
                )
            else:
                col = ColumnDefinition(
                    key=f"col_{idx}",
                    label=header.get("text", f"Column {idx}"),
                    header_style=self._convert_header_style(header.get("style")),
                )
            columns.append(col)

        start_row = old_table.get("start_row", 1)
        start_col = old_table.get("start_column", 1)

        table_template = TableTemplate(
            name=f"table_{id(old_table)}",
            columns=columns,
            title=old_table.get("title"),
            start_position=CellPosition(start_row, start_col),
        )

        data_rows = old_table.get("data", [])
        table_data = TableData()

        for row in data_rows:
            row_dict = {f"col_{idx}": val for idx, val in enumerate(row)}
            table_data.add_row(row_dict)

        return table_template, table_data

    def _convert_header_style(self, old_style: Optional[Dict]) -> Optional[CellStyle]:
        """Convert old header style to new CellStyle."""
        if not old_style:
            return None

        font = None
        if any(k in old_style for k in ["bold", "italic", "font_size", "font_color"]):
            font = Font(
                bold=old_style.get("bold", False),
                italic=old_style.get("italic", False),
                size=old_style.get("font_size"),
                color=Color(old_style["font_color"]) if old_style.get("font_color") else None,
            )

        fill = None
        if old_style.get("background_color"):
            fill = Fill(
                pattern=PatternFill.SOLID,
                foreground_color=Color(old_style["background_color"]),
            )

        alignment = None
        if old_style.get("horizontal_alignment") or old_style.get("vertical_alignment"):
            h_align = old_style.get("horizontal_alignment")
            v_align = old_style.get("vertical_alignment")

            alignment = Alignment(
                horizontal=HorizontalAlignment(h_align) if h_align else None,
                vertical=VerticalAlignment(v_align) if v_align else None,
            )

        return CellStyle(font=font, fill=fill, alignment=alignment)

    def build(self) -> Any:
        """Build the spreadsheet (for compatibility)."""
        return None

    def save(self, output_path: Union[str, Path]) -> Path:
        """
        Save spreadsheet to file.

        Args:
            output_path: Output file path

        Returns:
            Path to saved file
        """
        renderer = SpreadsheetRenderer(format=self.format)
        return renderer.render(self.template, self.data, output=output_path)

    def to_bytes(self) -> bytes:
        """
        Generate spreadsheet as bytes.

        Returns:
            Spreadsheet bytes
        """
        renderer = SpreadsheetRenderer(format=self.format)
        return renderer.render(self.template, self.data)


def migrate_to_new_api(old_schema: Dict[str, Any]) -> tuple[SpreadsheetTemplate, SpreadsheetData]:
    """
    Helper function to migrate old schema to new template + data.

    Args:
        old_schema: Old-style schema dictionary

    Returns:
        Tuple of (template, data) for new API

    Example:
        old_schema = {...}
        template, data = migrate_to_new_api(old_schema)
        renderer = SpreadsheetRenderer()
        renderer.render(template, data, "output.xlsx")
    """
    builder = LegacySpreadsheetBuilder(old_schema)
    return builder.template, builder.data
