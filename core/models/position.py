"""Cell positioning and range abstractions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class CellPosition:
    """Represents a cell position in a spreadsheet (1-indexed)."""

    row: int
    column: int

    def __post_init__(self) -> None:
        if self.row < 1:
            raise ValueError(f"Row must be >= 1, got {self.row}")
        if self.column < 1:
            raise ValueError(f"Column must be >= 1, got {self.column}")

    @classmethod
    def from_a1(cls, reference: str) -> CellPosition:
        """
        Create position from A1 notation (e.g., 'B5').

        Args:
            reference: Cell reference in A1 notation (e.g., 'A1', 'AB123')

        Returns:
            CellPosition instance

        Raises:
            ValueError: If reference is invalid
        """
        reference = reference.strip().upper()
        if not reference:
            raise ValueError("Cell reference cannot be empty")

        column_part = ""
        row_part = ""

        for char in reference:
            if char.isalpha():
                column_part += char
            elif char.isdigit():
                row_part += char
            else:
                raise ValueError(f"Invalid character in cell reference: {char}")

        if not column_part or not row_part:
            raise ValueError(f"Invalid cell reference: {reference}")

        column = cls._column_letters_to_index(column_part)
        row = int(row_part)

        return cls(row=row, column=column)

    def to_a1(self) -> str:
        """
        Convert position to A1 notation.

        Returns:
            A1 notation string (e.g., 'B5')
        """
        return f"{self._column_index_to_letters(self.column)}{self.row}"

    @staticmethod
    def _column_letters_to_index(letters: str) -> int:
        """Convert column letters to 1-indexed column number."""
        result = 0
        for char in letters:
            result = result * 26 + (ord(char) - ord("A") + 1)
        return result

    @staticmethod
    def _column_index_to_letters(index: int) -> str:
        """Convert 1-indexed column number to letters."""
        if index < 1:
            raise ValueError(f"Column index must be >= 1, got {index}")

        letters = ""
        while index > 0:
            index -= 1
            letters = chr(ord("A") + (index % 26)) + letters
            index //= 26
        return letters

    def offset(self, rows: int = 0, columns: int = 0) -> CellPosition:
        """
        Create new position offset from this one.

        Args:
            rows: Number of rows to offset (can be negative)
            columns: Number of columns to offset (can be negative)

        Returns:
            New CellPosition
        """
        return CellPosition(row=self.row + rows, column=self.column + columns)


@dataclass(frozen=True)
class CellRange:
    """Represents a range of cells in a spreadsheet."""

    start: CellPosition
    end: CellPosition

    def __post_init__(self) -> None:
        if self.start.row > self.end.row:
            raise ValueError(
                f"Start row ({self.start.row}) must be <= end row ({self.end.row})"
            )
        if self.start.column > self.end.column:
            raise ValueError(
                f"Start column ({self.start.column}) must be <= end column ({self.end.column})"
            )

    @classmethod
    def from_a1(cls, reference: str) -> CellRange:
        """
        Create range from A1 notation (e.g., 'A1:B10').

        Args:
            reference: Range reference in A1 notation

        Returns:
            CellRange instance

        Raises:
            ValueError: If reference is invalid
        """
        if ":" not in reference:
            pos = CellPosition.from_a1(reference)
            return cls(start=pos, end=pos)

        parts = reference.split(":")
        if len(parts) != 2:
            raise ValueError(f"Invalid range reference: {reference}")

        start = CellPosition.from_a1(parts[0])
        end = CellPosition.from_a1(parts[1])

        return cls(start=start, end=end)

    def to_a1(self) -> str:
        """
        Convert range to A1 notation.

        Returns:
            A1 notation string (e.g., 'A1:B10')
        """
        if self.start == self.end:
            return self.start.to_a1()
        return f"{self.start.to_a1()}:{self.end.to_a1()}"

    def contains(self, position: CellPosition) -> bool:
        """Check if position is within this range."""
        return (
            self.start.row <= position.row <= self.end.row
            and self.start.column <= position.column <= self.end.column
        )

    def iter_positions(self) -> Iterator[CellPosition]:
        """Iterate over all positions in this range."""
        for row in range(self.start.row, self.end.row + 1):
            for col in range(self.start.column, self.end.column + 1):
                yield CellPosition(row=row, column=col)

    @property
    def row_count(self) -> int:
        """Number of rows in this range."""
        return self.end.row - self.start.row + 1

    @property
    def column_count(self) -> int:
        """Number of columns in this range."""
        return self.end.column - self.start.column + 1

    @property
    def cell_count(self) -> int:
        """Total number of cells in this range."""
        return self.row_count * self.column_count
