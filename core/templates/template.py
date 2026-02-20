"""Template definitions for layout structure."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from ..models.position import CellPosition
from ..styles.cell_style import CellStyle
from ..styles.conditional import ConditionalRule


@dataclass
class ColumnDefinition:
    """
    Defines a column in a table template.

    Specifies column layout, styling, and formatting without data.
    """

    key: str
    label: str
    width: Optional[float] = None
    style: Optional[CellStyle] = None
    header_style: Optional[CellStyle] = None
    number_format: Optional[str] = None
    formula_template: Optional[str] = None
    computed: Optional[Callable[[Dict], any]] = None
    hidden: bool = False

    def __post_init__(self) -> None:
        if not self.key:
            raise ValueError("Column key cannot be empty")
        if not self.label:
            raise ValueError("Column label cannot be empty")
        if self.width is not None and self.width <= 0:
            raise ValueError(f"Column width must be > 0, got {self.width}")


@dataclass
class SectionDefinition:
    """
    Defines a section within a table (e.g., revenue, expenses, totals).

    Sections group rows and can have their own styling and formulas.
    """

    key: str
    label: str
    style: Optional[CellStyle] = None
    formula_template: Optional[str] = None
    is_total: bool = False
    indent_level: int = 0

    def __post_init__(self) -> None:
        if not self.key:
            raise ValueError("Section key cannot be empty")
        if self.indent_level < 0:
            raise ValueError(f"Indent level must be >= 0, got {self.indent_level}")


@dataclass
class TableTemplate:
    """
    Template for a table structure.

    Defines columns, sections, styling, and conditional rules without data.
    """

    name: str
    columns: List[ColumnDefinition]
    sections: Optional[List[SectionDefinition]] = None
    title: Optional[str] = None
    title_style: Optional[CellStyle] = None
    header_style: Optional[CellStyle] = None
    default_style: Optional[CellStyle] = None
    conditional_rules: List[ConditionalRule] = field(default_factory=list)
    start_position: CellPosition = field(default_factory=lambda: CellPosition(1, 1))
    freeze_headers: bool = True
    show_grid: bool = True
    alternate_row_colors: bool = False
    alternate_row_style: Optional[CellStyle] = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Table name cannot be empty")
        if not self.columns:
            raise ValueError("Table must have at least one column")

        column_keys = [col.key for col in self.columns]
        if len(column_keys) != len(set(column_keys)):
            raise ValueError("Column keys must be unique")

    def get_column(self, key: str) -> Optional[ColumnDefinition]:
        """Get column definition by key."""
        for col in self.columns:
            if col.key == key:
                return col
        return None

    def get_section(self, key: str) -> Optional[SectionDefinition]:
        """Get section definition by key."""
        if not self.sections:
            return None
        for section in self.sections:
            if section.key == key:
                return section
        return None

    @property
    def visible_columns(self) -> List[ColumnDefinition]:
        """Get only visible columns."""
        return [col for col in self.columns if not col.hidden]

    @property
    def column_count(self) -> int:
        """Number of visible columns."""
        return len(self.visible_columns)


@dataclass
class SheetTemplate:
    """
    Template for a sheet structure.

    Defines multiple tables and sheet-level configuration.
    """

    name: str
    tables: List[TableTemplate]
    freeze_panes: Optional[CellPosition] = None
    default_column_width: Optional[float] = None
    default_row_height: Optional[float] = None
    show_gridlines: bool = True
    show_headers: bool = True
    zoom_scale: int = 100

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Sheet name cannot be empty")
        if len(self.name) > 31:
            raise ValueError(f"Sheet name must be <= 31 characters, got {len(self.name)}")
        if not self.tables:
            raise ValueError("Sheet must have at least one table")
        if self.zoom_scale < 10 or self.zoom_scale > 400:
            raise ValueError(f"Zoom scale must be between 10 and 400, got {self.zoom_scale}")

    def get_table(self, name: str) -> Optional[TableTemplate]:
        """Get table template by name."""
        for table in self.tables:
            if table.name == name:
                return table
        return None


@dataclass
class SpreadsheetTemplate:
    """
    Template for a complete spreadsheet.

    Defines structure for all sheets without data.
    """

    sheets: List[SheetTemplate]
    metadata: Dict[str, any] = field(default_factory=dict)
    active_sheet: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.sheets:
            raise ValueError("Spreadsheet must have at least one sheet")

        sheet_names = [sheet.name for sheet in self.sheets]
        if len(sheet_names) != len(set(sheet_names)):
            raise ValueError("Sheet names must be unique")

        if self.active_sheet is None:
            self.active_sheet = self.sheets[0].name

    def get_sheet(self, name: str) -> Optional[SheetTemplate]:
        """Get sheet template by name."""
        for sheet in self.sheets:
            if sheet.name == name:
                return sheet
        return None

    @property
    def sheet_count(self) -> int:
        """Number of sheets."""
        return len(self.sheets)

    @property
    def sheet_names(self) -> List[str]:
        """List of sheet names."""
        return [sheet.name for sheet in self.sheets]
