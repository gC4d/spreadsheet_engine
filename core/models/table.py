"""Table abstraction for structured data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .cell import Cell
from .position import CellPosition


@dataclass
class Table:
    """
    Represents a table of cells with rows and columns.

    A table is a 2D grid of cells with optional headers.
    It provides the core data structure for rendering tabular data.
    """

    cells: List[List[Cell]] = field(default_factory=list)
    headers: Optional[List[Cell]] = None
    title: Optional[Cell] = None
    start_position: CellPosition = field(default_factory=lambda: CellPosition(1, 1))

    def __post_init__(self) -> None:
        if self.cells:
            row_lengths = [len(row) for row in self.cells]
            if len(set(row_lengths)) > 1:
                raise ValueError(
                    f"All rows must have the same length. Found: {row_lengths}"
                )

    @classmethod
    def from_data(
        cls,
        data: List[Dict[str, Any]],
        columns: List[str],
        headers: Optional[List[str]] = None,
        title: Optional[str] = None,
        start_position: Optional[CellPosition] = None,
    ) -> Table:
        """
        Create table from list of dictionaries.

        Args:
            data: List of row dictionaries
            columns: Column keys to extract from data
            headers: Optional header labels (defaults to column keys)
            title: Optional table title
            start_position: Starting position for the table

        Returns:
            Table instance
        """
        if headers is None:
            headers = columns

        header_cells = [Cell.text(h, style=None) for h in headers]

        cells = []
        for row_data in data:
            row_cells = []
            for col in columns:
                value = row_data.get(col)
                row_cells.append(Cell(value=value))
            cells.append(row_cells)

        title_cell = Cell.text(title) if title else None

        return cls(
            cells=cells,
            headers=header_cells,
            title=title_cell,
            start_position=start_position or CellPosition(1, 1),
        )

    @classmethod
    def from_rows(
        cls,
        rows: List[List[Any]],
        headers: Optional[List[str]] = None,
        title: Optional[str] = None,
        start_position: Optional[CellPosition] = None,
    ) -> Table:
        """
        Create table from list of row lists.

        Args:
            rows: List of row lists
            headers: Optional header labels
            title: Optional table title
            start_position: Starting position for the table

        Returns:
            Table instance
        """
        cells = [[Cell(value=val) for val in row] for row in rows]

        header_cells = None
        if headers:
            header_cells = [Cell.text(h) for h in headers]

        title_cell = Cell.text(title) if title else None

        return cls(
            cells=cells,
            headers=header_cells,
            title=title_cell,
            start_position=start_position or CellPosition(1, 1),
        )

    def add_row(self, row: List[Cell]) -> None:
        """
        Add a row to the table.

        Args:
            row: List of cells

        Raises:
            ValueError: If row length doesn't match existing rows
        """
        if self.cells and len(row) != self.column_count:
            raise ValueError(
                f"Row must have {self.column_count} cells, got {len(row)}"
            )
        self.cells.append(row)

    def add_column(self, column: List[Cell], header: Optional[Cell] = None) -> None:
        """
        Add a column to the table.

        Args:
            column: List of cells for the column
            header: Optional header cell

        Raises:
            ValueError: If column length doesn't match existing rows
        """
        if self.cells and len(column) != self.row_count:
            raise ValueError(
                f"Column must have {self.row_count} cells, got {len(column)}"
            )

        if not self.cells:
            self.cells = [[cell] for cell in column]
        else:
            for i, cell in enumerate(column):
                self.cells[i].append(cell)

        if header and self.headers:
            self.headers.append(header)

    def get_cell(self, row: int, column: int) -> Cell:
        """
        Get cell at position (0-indexed within table).

        Args:
            row: Row index (0-indexed)
            column: Column index (0-indexed)

        Returns:
            Cell at position

        Raises:
            IndexError: If position is out of bounds
        """
        return self.cells[row][column]

    def set_cell(self, row: int, column: int, cell: Cell) -> None:
        """
        Set cell at position (0-indexed within table).

        Args:
            row: Row index (0-indexed)
            column: Column index (0-indexed)
            cell: Cell to set

        Raises:
            IndexError: If position is out of bounds
        """
        self.cells[row][column] = cell

    @property
    def row_count(self) -> int:
        """Number of data rows (excluding headers)."""
        return len(self.cells)

    @property
    def column_count(self) -> int:
        """Number of columns."""
        if not self.cells:
            return len(self.headers) if self.headers else 0
        return len(self.cells[0])

    @property
    def has_headers(self) -> bool:
        """Check if table has headers."""
        return self.headers is not None and len(self.headers) > 0

    @property
    def has_title(self) -> bool:
        """Check if table has a title."""
        return self.title is not None

    def iter_rows(self) -> List[List[Cell]]:
        """Iterate over all rows."""
        return self.cells

    def iter_columns(self) -> List[List[Cell]]:
        """Iterate over all columns."""
        if not self.cells:
            return []

        return [
            [self.cells[row][col] for row in range(self.row_count)]
            for col in range(self.column_count)
        ]

    def apply_style_to_column(self, column: int, style: Any) -> None:
        """
        Apply style to all cells in a column.

        Args:
            column: Column index (0-indexed)
            style: CellStyle to apply
        """
        for row in self.cells:
            if column < len(row):
                row[column] = row[column].merge_style(style)

    def apply_style_to_row(self, row: int, style: Any) -> None:
        """
        Apply style to all cells in a row.

        Args:
            row: Row index (0-indexed)
            style: CellStyle to apply
        """
        if row < len(self.cells):
            self.cells[row] = [cell.merge_style(style) for cell in self.cells[row]]

    def __repr__(self) -> str:
        return f"Table(rows={self.row_count}, columns={self.column_count}, has_headers={self.has_headers})"
