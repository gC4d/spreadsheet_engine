"""Template and data merging logic."""

from __future__ import annotations

from typing import Dict, List

from ..models.cell import Cell
from ..models.sheet import Sheet
from ..models.spreadsheet import Spreadsheet
from ..models.table import Table
from ..models.position import CellPosition
from ..styles.cell_style import CellStyle
from .data import SheetData, SpreadsheetData, TableData
from .template import (
    ColumnDefinition,
    SheetTemplate,
    SpreadsheetTemplate,
    TableTemplate,
)


class TemplateMerger:
    """
    Merges templates with data to produce concrete spreadsheet models.

    This is the core logic that combines layout definitions with runtime data.
    """

    @staticmethod
    def merge_spreadsheet(
        template: SpreadsheetTemplate,
        data: SpreadsheetData,
    ) -> Spreadsheet:
        """
        Merge spreadsheet template with data.

        Args:
            template: Spreadsheet template
            data: Spreadsheet data

        Returns:
            Concrete Spreadsheet instance
        """
        spreadsheet = Spreadsheet(
            metadata=template.metadata.copy(),
            active_sheet=template.active_sheet,
        )

        for sheet_template in template.sheets:
            sheet_data = data.get_sheet_data(sheet_template.name)
            if sheet_data is None:
                sheet_data = SheetData()

            sheet = TemplateMerger.merge_sheet(sheet_template, sheet_data)
            spreadsheet.add_sheet(sheet)

        return spreadsheet

    @staticmethod
    def merge_sheet(template: SheetTemplate, data: SheetData) -> Sheet:
        """
        Merge sheet template with data.

        Args:
            template: Sheet template
            data: Sheet data

        Returns:
            Concrete Sheet instance
        """
        sheet = Sheet(
            name=template.name,
            freeze_panes=template.freeze_panes,
            default_column_width=template.default_column_width,
            default_row_height=template.default_row_height,
        )

        current_row = 1
        for table_template in template.tables:
            table_data = data.get_table_data(table_template.name)
            if table_data is None:
                table_data = TableData()

            table_template_with_position = TableTemplate(
                name=table_template.name,
                columns=table_template.columns,
                sections=table_template.sections,
                title=table_template.title,
                title_style=table_template.title_style,
                header_style=table_template.header_style,
                default_style=table_template.default_style,
                conditional_rules=table_template.conditional_rules,
                start_position=CellPosition(current_row, 1),
                freeze_headers=table_template.freeze_headers,
                show_grid=table_template.show_grid,
                alternate_row_colors=table_template.alternate_row_colors,
                alternate_row_style=table_template.alternate_row_style,
            )

            table = TemplateMerger.merge_table(table_template_with_position, table_data)
            sheet.add_table(table)

            rows_used = 0
            if table.has_title:
                rows_used += 1
            if table.has_headers:
                rows_used += 1
            rows_used += table.row_count

            current_row += rows_used + 2

            for col_idx, col_def in enumerate(table_template.visible_columns, start=1):
                if col_def.width:
                    sheet.set_column_width(col_idx, col_def.width)

        return sheet

    @staticmethod
    def merge_table(template: TableTemplate, data: TableData) -> Table:
        """
        Merge table template with data.

        Args:
            template: Table template
            data: Table data

        Returns:
            Concrete Table instance
        """
        title_cell = None
        if template.title:
            title_cell = Cell.text(template.title, style=template.title_style)

        header_cells = TemplateMerger._create_header_cells(template)

        data_cells = TemplateMerger._create_data_cells(template, data)

        table = Table(
            cells=data_cells,
            headers=header_cells,
            title=title_cell,
            start_position=template.start_position,
        )

        if template.alternate_row_colors and template.alternate_row_style:
            for i in range(0, table.row_count, 2):
                table.apply_style_to_row(i, template.alternate_row_style)

        return table

    @staticmethod
    def _create_header_cells(template: TableTemplate) -> List[Cell]:
        """Create header cells from template."""
        header_cells = []

        for col_def in template.visible_columns:
            style = col_def.header_style or template.header_style or CellStyle.header()
            header_cell = Cell.text(col_def.label, style=style)
            header_cells.append(header_cell)

        return header_cells

    @staticmethod
    def _create_data_cells(
        template: TableTemplate,
        data: TableData,
    ) -> List[List[Cell]]:
        """Create data cells from template and data."""
        if data.is_empty:
            return []

        cells = []

        if template.sections:
            for section in template.sections:
                section_rows = data.get_section_data(section.key)
                if not section_rows:
                    continue

                section_cells = TemplateMerger._create_section_cells(
                    template, section_rows, section.key
                )
                cells.extend(section_cells)

                if section.formula_template or section.is_total:
                    total_row = TemplateMerger._create_total_row(
                        template, section, len(cells)
                    )
                    cells.append(total_row)
        else:
            for row_data in data.iter_rows():
                row_cells = TemplateMerger._create_row_cells(template, row_data)
                cells.append(row_cells)

        return cells

    @staticmethod
    def _create_section_cells(
        template: TableTemplate,
        section_rows: List[Dict],
        section_key: str,
    ) -> List[List[Cell]]:
        """Create cells for a section."""
        cells = []
        for row_data in section_rows:
            row_cells = TemplateMerger._create_row_cells(template, row_data)
            cells.append(row_cells)
        return cells

    @staticmethod
    def _create_row_cells(
        template: TableTemplate,
        row_data: Dict,
    ) -> List[Cell]:
        """Create cells for a single data row."""
        row_cells = []

        for col_def in template.visible_columns:
            cell = TemplateMerger._create_cell_from_column(col_def, row_data, template)
            row_cells.append(cell)

        return row_cells

    @staticmethod
    def _create_cell_from_column(
        col_def: ColumnDefinition,
        row_data: Dict,
        template: TableTemplate,
    ) -> Cell:
        """Create a cell from column definition and row data."""
        if col_def.computed:
            value = col_def.computed(row_data)
        else:
            value = row_data.get(col_def.key)

        if col_def.formula_template:
            formula = col_def.formula_template
            cell = Cell.formula_cell(
                formula=formula,
                cached_value=value,
                number_format=col_def.number_format,
                style=col_def.style or template.default_style,
            )
        else:
            cell = Cell(
                value=value,
                number_format=col_def.number_format,
                style=col_def.style or template.default_style,
            )

        return cell

    @staticmethod
    def _create_total_row(
        template: TableTemplate,
        section,
        current_row_count: int,
    ) -> List[Cell]:
        """Create a total row for a section."""
        row_cells = []

        for idx, col_def in enumerate(template.visible_columns):
            if idx == 0:
                cell = Cell.text(
                    section.label,
                    style=section.style or CellStyle.header(),
                )
            elif section.formula_template:
                formula = section.formula_template
                cell = Cell.formula_cell(
                    formula=formula,
                    number_format=col_def.number_format,
                    style=section.style or CellStyle.header(),
                )
            else:
                cell = Cell.blank()

            row_cells.append(cell)

        return row_cells
