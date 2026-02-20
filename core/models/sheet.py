"""Sheet abstraction for organizing tables and cells."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..styles.conditional import ConditionalRule
from .cell import Cell
from .position import CellPosition, CellRange
from .table import Table


@dataclass
class Sheet:
    """
    Represents a single worksheet in a spreadsheet.

    A sheet contains:
    - Tables (structured data)
    - Individual cells (for custom layouts)
    - Conditional formatting rules
    - Freeze panes configuration
    """

    name: str
    tables: List[Table] = field(default_factory=list)
    cells: Dict[CellPosition, Cell] = field(default_factory=dict)
    conditional_rules: List[tuple[CellRange, ConditionalRule]] = field(
        default_factory=list
    )
    freeze_panes: Optional[CellPosition] = None
    column_widths: Dict[int, float] = field(default_factory=dict)
    row_heights: Dict[int, float] = field(default_factory=dict)
    default_column_width: Optional[float] = None
    default_row_height: Optional[float] = None

    def __post_init__(self) -> None:
        if len(self.name) > 31:
            raise ValueError(f"Sheet name must be <= 31 characters, got {len(self.name)}")

        invalid_chars = ["\\", "/", "*", "?", ":", "[", "]"]
        for char in invalid_chars:
            if char in self.name:
                raise ValueError(
                    f"Sheet name cannot contain: {', '.join(invalid_chars)}"
                )

    def add_table(self, table: Table) -> None:
        """Add a table to the sheet."""
        self.tables.append(table)

    def set_cell(self, position: CellPosition, cell: Cell) -> None:
        """Set a cell at a specific position."""
        self.cells[position] = cell

    def get_cell(self, position: CellPosition) -> Optional[Cell]:
        """Get cell at position, or None if not set."""
        return self.cells.get(position)

    def add_conditional_rule(self, range: CellRange, rule: ConditionalRule) -> None:
        """Add a conditional formatting rule for a range."""
        self.conditional_rules.append((range, rule))

    def set_column_width(self, column: int, width: float) -> None:
        """Set width for a specific column."""
        if width <= 0:
            raise ValueError(f"Column width must be > 0, got {width}")
        self.column_widths[column] = width

    def set_row_height(self, row: int, height: float) -> None:
        """Set height for a specific row."""
        if height <= 0:
            raise ValueError(f"Row height must be > 0, got {height}")
        self.row_heights[row] = height

    def set_freeze_panes(self, position: CellPosition) -> None:
        """
        Set freeze panes at position.

        Args:
            position: Position where panes freeze (rows above and columns left are frozen)
        """
        self.freeze_panes = position

    @classmethod
    def create_simple(
        cls,
        name: str,
        data: List[List[any]],
        headers: Optional[List[str]] = None,
        title: Optional[str] = None,
    ) -> Sheet:
        """
        Create a simple sheet with one table.

        Args:
            name: Sheet name
            data: Row data
            headers: Optional headers
            title: Optional title

        Returns:
            Sheet instance
        """
        table = Table.from_rows(rows=data, headers=headers, title=title)
        return cls(name=name, tables=[table])

    def __repr__(self) -> str:
        return f"Sheet(name='{self.name}', tables={len(self.tables)}, cells={len(self.cells)})"
