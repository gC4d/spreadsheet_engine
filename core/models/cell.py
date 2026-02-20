"""Cell abstraction with value, formula, and style support."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from ..styles.cell_style import CellStyle
from ..styles.number_format import NumberFormat


class CellDataType(str, Enum):
    """Data type of a cell value."""

    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TIME = "time"
    FORMULA = "formula"
    ERROR = "error"
    BLANK = "blank"


@dataclass
class Cell:
    """
    Represents a single spreadsheet cell.

    A cell can contain:
    - A value (any Python type)
    - A formula (Excel formula string)
    - A style (CellStyle instance)
    - A number format (NumberFormat or custom string)
    - A data type hint

    The cell is the fundamental unit of data in the spreadsheet engine.
    """

    value: Any = None
    formula: Optional[str] = None
    style: Optional[CellStyle] = None
    number_format: Optional[str] = None
    data_type: Optional[CellDataType] = None
    comment: Optional[str] = None
    hyperlink: Optional[str] = None

    def __post_init__(self) -> None:
        if self.data_type is None:
            self.data_type = self._infer_data_type()

        if self.formula and not self.formula.startswith("="):
            self.formula = f"={self.formula}"

    def _infer_data_type(self) -> CellDataType:
        """Infer data type from value and formula."""
        if self.formula:
            return CellDataType.FORMULA

        if self.value is None or self.value == "":
            return CellDataType.BLANK

        if isinstance(self.value, bool):
            return CellDataType.BOOLEAN

        if isinstance(self.value, (int, float)):
            return CellDataType.NUMBER

        if isinstance(self.value, str):
            return CellDataType.STRING

        return CellDataType.STRING

    @classmethod
    def blank(cls) -> Cell:
        """Create a blank cell."""
        return cls(value=None, data_type=CellDataType.BLANK)

    @classmethod
    def text(cls, value: str, style: Optional[CellStyle] = None) -> Cell:
        """Create a text cell."""
        return cls(value=value, data_type=CellDataType.STRING, style=style)

    @classmethod
    def number(
        cls,
        value: float | int,
        number_format: Optional[str] = None,
        style: Optional[CellStyle] = None,
    ) -> Cell:
        """Create a number cell."""
        return cls(
            value=value,
            data_type=CellDataType.NUMBER,
            number_format=number_format,
            style=style,
        )

    @classmethod
    def currency(
        cls,
        value: float | int,
        currency_code: str = "BRL",
        style: Optional[CellStyle] = None,
    ) -> Cell:
        """Create a currency cell."""
        return cls(
            value=value,
            data_type=CellDataType.NUMBER,
            number_format=NumberFormat.currency(currency_code),
            style=style or CellStyle.currency(),
        )

    @classmethod
    def percentage(
        cls,
        value: float,
        decimals: int = 2,
        style: Optional[CellStyle] = None,
    ) -> Cell:
        """Create a percentage cell."""
        format_map = {
            0: NumberFormat.PERCENTAGE.value,
            1: NumberFormat.PERCENTAGE_1.value,
            2: NumberFormat.PERCENTAGE_2.value,
        }
        return cls(
            value=value,
            data_type=CellDataType.NUMBER,
            number_format=format_map.get(decimals, NumberFormat.PERCENTAGE_2.value),
            style=style or CellStyle.percentage(),
        )

    @classmethod
    def formula_cell(
        cls,
        formula: str,
        cached_value: Any = None,
        number_format: Optional[str] = None,
        style: Optional[CellStyle] = None,
    ) -> Cell:
        """Create a formula cell."""
        return cls(
            value=cached_value,
            formula=formula,
            data_type=CellDataType.FORMULA,
            number_format=number_format,
            style=style,
        )

    @classmethod
    def date(
        cls,
        value: Any,
        date_format: str = NumberFormat.DATE_BR.value,
        style: Optional[CellStyle] = None,
    ) -> Cell:
        """Create a date cell."""
        return cls(
            value=value,
            data_type=CellDataType.DATE,
            number_format=date_format,
            style=style,
        )

    @classmethod
    def datetime(
        cls,
        value: Any,
        datetime_format: str = NumberFormat.DATETIME_BR.value,
        style: Optional[CellStyle] = None,
    ) -> Cell:
        """Create a datetime cell."""
        return cls(
            value=value,
            data_type=CellDataType.DATETIME,
            number_format=datetime_format,
            style=style,
        )

    def with_style(self, style: CellStyle) -> Cell:
        """Create a new cell with the given style."""
        return Cell(
            value=self.value,
            formula=self.formula,
            style=style,
            number_format=self.number_format,
            data_type=self.data_type,
            comment=self.comment,
            hyperlink=self.hyperlink,
        )

    def with_number_format(self, number_format: str) -> Cell:
        """Create a new cell with the given number format."""
        return Cell(
            value=self.value,
            formula=self.formula,
            style=self.style,
            number_format=number_format,
            data_type=self.data_type,
            comment=self.comment,
            hyperlink=self.hyperlink,
        )

    def merge_style(self, style: Optional[CellStyle]) -> Cell:
        """Create a new cell with merged style."""
        if style is None:
            return self

        merged_style = self.style.merge(style) if self.style else style
        return self.with_style(merged_style)

    @property
    def is_blank(self) -> bool:
        """Check if cell is blank."""
        return self.data_type == CellDataType.BLANK

    @property
    def is_formula(self) -> bool:
        """Check if cell contains a formula."""
        return self.data_type == CellDataType.FORMULA or self.formula is not None

    @property
    def display_value(self) -> Any:
        """Get the value to display (formula result or value)."""
        return self.value

    def __repr__(self) -> str:
        if self.formula:
            return f"Cell(formula='{self.formula}', value={self.value})"
        return f"Cell(value={self.value})"
