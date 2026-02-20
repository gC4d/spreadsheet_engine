"""Conditional formatting system."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .cell_style import CellStyle, Color


class RuleType(str, Enum):
    """Types of conditional formatting rules."""

    CELL_VALUE = "cellValue"
    FORMULA = "formula"
    COLOR_SCALE = "colorScale"
    DATA_BAR = "dataBar"
    ICON_SET = "iconSet"
    TOP_10 = "top10"
    DUPLICATE_VALUES = "duplicateValues"
    UNIQUE_VALUES = "uniqueValues"
    CONTAINS_TEXT = "containsText"
    NOT_CONTAINS_TEXT = "notContainsText"
    BEGINS_WITH = "beginsWith"
    ENDS_WITH = "endsWith"
    CONTAINS_BLANKS = "containsBlanks"
    NOT_CONTAINS_BLANKS = "notContainsBlanks"
    CONTAINS_ERRORS = "containsErrors"
    NOT_CONTAINS_ERRORS = "notContainsErrors"
    TIME_PERIOD = "timePeriod"
    ABOVE_AVERAGE = "aboveAverage"
    BELOW_AVERAGE = "belowAverage"


class CellValueOperator(str, Enum):
    """Operators for cell value conditional rules."""

    EQUAL = "equal"
    NOT_EQUAL = "notEqual"
    GREATER_THAN = "greaterThan"
    GREATER_THAN_OR_EQUAL = "greaterThanOrEqual"
    LESS_THAN = "lessThan"
    LESS_THAN_OR_EQUAL = "lessThanOrEqual"
    BETWEEN = "between"
    NOT_BETWEEN = "notBetween"


@dataclass(frozen=True)
class ColorScale:
    """Color scale configuration for conditional formatting."""

    min_color: Color
    mid_color: Optional[Color] = None
    max_color: Optional[Color] = None
    min_value: Optional[float] = None
    mid_value: Optional[float] = None
    max_value: Optional[float] = None


@dataclass(frozen=True)
class DataBar:
    """Data bar configuration for conditional formatting."""

    color: Color
    show_value: bool = True
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class IconSetType(str, Enum):
    """Icon set types for conditional formatting."""

    THREE_ARROWS = "3Arrows"
    THREE_ARROWS_GRAY = "3ArrowsGray"
    THREE_FLAGS = "3Flags"
    THREE_TRAFFIC_LIGHTS = "3TrafficLights"
    THREE_SIGNS = "3Signs"
    THREE_SYMBOLS = "3Symbols"
    FOUR_ARROWS = "4Arrows"
    FOUR_ARROWS_GRAY = "4ArrowsGray"
    FOUR_RED_TO_BLACK = "4RedToBlack"
    FOUR_RATING = "4Rating"
    FOUR_TRAFFIC_LIGHTS = "4TrafficLights"
    FIVE_ARROWS = "5Arrows"
    FIVE_ARROWS_GRAY = "5ArrowsGray"
    FIVE_RATING = "5Rating"
    FIVE_QUARTERS = "5Quarters"


@dataclass(frozen=True)
class IconSet:
    """Icon set configuration for conditional formatting."""

    icon_set_type: IconSetType
    show_value: bool = True
    reverse: bool = False


@dataclass(frozen=True)
class ConditionalRule:
    """
    Conditional formatting rule.

    Defines a condition and the style to apply when the condition is met.
    """

    rule_type: RuleType
    style: Optional[CellStyle] = None
    priority: int = 1
    stop_if_true: bool = False
    formula: Optional[str] = None
    operator: Optional[CellValueOperator] = None
    value: Optional[str] = None
    value2: Optional[str] = None
    text: Optional[str] = None
    color_scale: Optional[ColorScale] = None
    data_bar: Optional[DataBar] = None
    icon_set: Optional[IconSet] = None

    def __post_init__(self) -> None:
        if self.priority < 1:
            raise ValueError(f"Priority must be >= 1, got {self.priority}")

        if self.rule_type == RuleType.CELL_VALUE and self.operator is None:
            raise ValueError("Cell value rules require an operator")

        if self.rule_type == RuleType.FORMULA and not self.formula:
            raise ValueError("Formula rules require a formula")

        if self.rule_type == RuleType.COLOR_SCALE and self.color_scale is None:
            raise ValueError("Color scale rules require color_scale configuration")

        if self.rule_type == RuleType.DATA_BAR and self.data_bar is None:
            raise ValueError("Data bar rules require data_bar configuration")

        if self.rule_type == RuleType.ICON_SET and self.icon_set is None:
            raise ValueError("Icon set rules require icon_set configuration")

    @classmethod
    def cell_is_negative(cls, style: CellStyle, priority: int = 1) -> ConditionalRule:
        """Create rule for negative cell values."""
        return cls(
            rule_type=RuleType.CELL_VALUE,
            operator=CellValueOperator.LESS_THAN,
            value="0",
            style=style,
            priority=priority,
        )

    @classmethod
    def cell_is_positive(cls, style: CellStyle, priority: int = 1) -> ConditionalRule:
        """Create rule for positive cell values."""
        return cls(
            rule_type=RuleType.CELL_VALUE,
            operator=CellValueOperator.GREATER_THAN,
            value="0",
            style=style,
            priority=priority,
        )

    @classmethod
    def cell_is_zero(cls, style: CellStyle, priority: int = 1) -> ConditionalRule:
        """Create rule for zero cell values."""
        return cls(
            rule_type=RuleType.CELL_VALUE,
            operator=CellValueOperator.EQUAL,
            value="0",
            style=style,
            priority=priority,
        )

    @classmethod
    def alternate_rows(cls, style: CellStyle, priority: int = 1) -> ConditionalRule:
        """Create rule for alternating row colors."""
        return cls(
            rule_type=RuleType.FORMULA,
            formula="=MOD(ROW(),2)=0",
            style=style,
            priority=priority,
        )

    @classmethod
    def red_green_scale(cls, priority: int = 1) -> ConditionalRule:
        """Create red-to-green color scale."""
        return cls(
            rule_type=RuleType.COLOR_SCALE,
            color_scale=ColorScale(
                min_color=Color("FF0000"),
                mid_color=Color("FFFF00"),
                max_color=Color("00FF00"),
            ),
            priority=priority,
        )
