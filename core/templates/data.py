"""Data containers for runtime values."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterator, List, Optional


@dataclass
class TableData:
    """
    Runtime data for a table.

    Contains actual values to populate a table template.
    """

    rows: List[Dict[str, Any]] = field(default_factory=list)
    computed_values: Dict[str, Callable[[Dict], Any]] = field(default_factory=dict)
    section_data: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_row(self, row: Dict[str, Any]) -> None:
        """Add a data row."""
        self.rows.append(row)

    def add_rows(self, rows: List[Dict[str, Any]]) -> None:
        """Add multiple data rows."""
        self.rows.extend(rows)

    def add_section_data(self, section_key: str, rows: List[Dict[str, Any]]) -> None:
        """Add data for a specific section."""
        self.section_data[section_key] = rows

    def get_section_data(self, section_key: str) -> List[Dict[str, Any]]:
        """Get data for a specific section."""
        return self.section_data.get(section_key, [])

    def add_computed_column(self, key: str, func: Callable[[Dict], Any]) -> None:
        """Add a computed column function."""
        self.computed_values[key] = func

    def compute_value(self, key: str, row: Dict[str, Any]) -> Any:
        """Compute value for a row using registered function."""
        if key in self.computed_values:
            return self.computed_values[key](row)
        return row.get(key)

    @property
    def row_count(self) -> int:
        """Number of data rows."""
        return len(self.rows)

    @property
    def is_empty(self) -> bool:
        """Check if data is empty."""
        return len(self.rows) == 0 and len(self.section_data) == 0

    def iter_rows(self) -> Iterator[Dict[str, Any]]:
        """Iterate over all rows."""
        return iter(self.rows)

    @classmethod
    def from_list(cls, rows: List[Dict[str, Any]]) -> TableData:
        """Create TableData from list of dictionaries."""
        return cls(rows=rows)

    @classmethod
    def from_dataframe(cls, df: Any) -> TableData:
        """
        Create TableData from pandas DataFrame.

        Args:
            df: pandas DataFrame

        Returns:
            TableData instance
        """
        try:
            rows = df.to_dict('records')
            return cls(rows=rows)
        except AttributeError:
            raise ValueError("Input must be a pandas DataFrame")


@dataclass
class SheetData:
    """
    Runtime data for a sheet.

    Contains data for all tables in a sheet.
    """

    table_data: Dict[str, TableData] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_table_data(self, table_name: str, data: TableData) -> None:
        """Add data for a table."""
        self.table_data[table_name] = data

    def get_table_data(self, table_name: str) -> Optional[TableData]:
        """Get data for a table."""
        return self.table_data.get(table_name)

    @property
    def table_count(self) -> int:
        """Number of tables with data."""
        return len(self.table_data)

    @property
    def is_empty(self) -> bool:
        """Check if all tables are empty."""
        return all(data.is_empty for data in self.table_data.values())


@dataclass
class SpreadsheetData:
    """
    Runtime data for a complete spreadsheet.

    Contains data for all sheets.
    """

    sheet_data: Dict[str, SheetData] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_sheet_data(self, sheet_name: str, data: SheetData) -> None:
        """Add data for a sheet."""
        self.sheet_data[sheet_name] = data

    def get_sheet_data(self, sheet_name: str) -> Optional[SheetData]:
        """Get data for a sheet."""
        return self.sheet_data.get(sheet_name)

    @property
    def sheet_count(self) -> int:
        """Number of sheets with data."""
        return len(self.sheet_data)

    @classmethod
    def create_simple(
        cls,
        sheet_name: str,
        table_name: str,
        rows: List[Dict[str, Any]],
    ) -> SpreadsheetData:
        """
        Create simple spreadsheet data with one sheet and one table.

        Args:
            sheet_name: Name of the sheet
            table_name: Name of the table
            rows: Data rows

        Returns:
            SpreadsheetData instance
        """
        table_data = TableData.from_list(rows)
        sheet_data = SheetData()
        sheet_data.add_table_data(table_name, table_data)

        spreadsheet_data = cls()
        spreadsheet_data.add_sheet_data(sheet_name, sheet_data)

        return spreadsheet_data
