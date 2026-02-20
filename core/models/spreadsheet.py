"""Spreadsheet (workbook) abstraction."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .sheet import Sheet


@dataclass
class Spreadsheet:
    """
    Represents a complete spreadsheet workbook.

    A spreadsheet contains multiple sheets and metadata.
    """

    sheets: List[Sheet] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)
    active_sheet: Optional[str] = None

    def add_sheet(self, sheet: Sheet) -> None:
        """
        Add a sheet to the spreadsheet.

        Args:
            sheet: Sheet to add

        Raises:
            ValueError: If sheet name already exists
        """
        if self.get_sheet(sheet.name) is not None:
            raise ValueError(f"Sheet with name '{sheet.name}' already exists")
        self.sheets.append(sheet)

        if self.active_sheet is None:
            self.active_sheet = sheet.name

    def get_sheet(self, name: str) -> Optional[Sheet]:
        """Get sheet by name."""
        for sheet in self.sheets:
            if sheet.name == name:
                return sheet
        return None

    def remove_sheet(self, name: str) -> None:
        """
        Remove sheet by name.

        Args:
            name: Sheet name

        Raises:
            ValueError: If sheet doesn't exist
        """
        sheet = self.get_sheet(name)
        if sheet is None:
            raise ValueError(f"Sheet '{name}' not found")
        self.sheets.remove(sheet)

        if self.active_sheet == name:
            self.active_sheet = self.sheets[0].name if self.sheets else None

    @property
    def sheet_count(self) -> int:
        """Number of sheets in the spreadsheet."""
        return len(self.sheets)

    @property
    def sheet_names(self) -> List[str]:
        """List of all sheet names."""
        return [sheet.name for sheet in self.sheets]

    def __repr__(self) -> str:
        return f"Spreadsheet(sheets={self.sheet_count})"
