"""Complete cell styling system."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Color:
    """Represents a color in various formats."""

    def __init__(self, value: str) -> None:
        """
        Initialize color from hex string or color name.

        Args:
            value: Hex color (e.g., 'FF0000', '#FF0000') or name (e.g., 'red')

        Raises:
            ValueError: If color format is invalid
        """
        self.value = self._normalize_color(value)

    @staticmethod
    def _normalize_color(value: str) -> str:
        """Normalize color to uppercase hex without '#'."""
        value = value.strip().upper()
        if value.startswith("#"):
            value = value[1:]

        if len(value) == 6 and all(c in "0123456789ABCDEF" for c in value):
            return value

        color_map = {
            "BLACK": "000000",
            "WHITE": "FFFFFF",
            "RED": "FF0000",
            "GREEN": "00FF00",
            "BLUE": "0000FF",
            "YELLOW": "FFFF00",
            "CYAN": "00FFFF",
            "MAGENTA": "FF00FF",
            "GRAY": "808080",
            "GREY": "808080",
            "ORANGE": "FFA500",
            "PURPLE": "800080",
            "BROWN": "A52A2A",
            "PINK": "FFC0CB",
        }

        if value in color_map:
            return color_map[value]

        raise ValueError(f"Invalid color format: {value}")

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"Color('{self.value}')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Color):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


class HorizontalAlignment(str, Enum):
    """Horizontal alignment options."""

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"
    DISTRIBUTED = "distributed"


class VerticalAlignment(str, Enum):
    """Vertical alignment options."""

    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"
    JUSTIFY = "justify"
    DISTRIBUTED = "distributed"


@dataclass(frozen=True)
class Alignment:
    """Cell alignment configuration."""

    horizontal: Optional[HorizontalAlignment] = None
    vertical: Optional[VerticalAlignment] = None
    wrap_text: bool = False
    shrink_to_fit: bool = False
    indent: int = 0
    text_rotation: int = 0

    def __post_init__(self) -> None:
        if self.indent < 0:
            raise ValueError(f"Indent must be >= 0, got {self.indent}")
        if not -90 <= self.text_rotation <= 90:
            raise ValueError(
                f"Text rotation must be between -90 and 90, got {self.text_rotation}"
            )


class BorderStyle(str, Enum):
    """Border style options."""

    NONE = "none"
    THIN = "thin"
    MEDIUM = "medium"
    THICK = "thick"
    DOUBLE = "double"
    DOTTED = "dotted"
    DASHED = "dashed"
    DASH_DOT = "dashDot"
    DASH_DOT_DOT = "dashDotDot"


@dataclass(frozen=True)
class Border:
    """Border configuration for a cell."""

    left: Optional[BorderStyle] = None
    right: Optional[BorderStyle] = None
    top: Optional[BorderStyle] = None
    bottom: Optional[BorderStyle] = None
    color: Optional[Color] = None

    @classmethod
    def all_sides(cls, style: BorderStyle, color: Optional[Color] = None) -> Border:
        """Create border with same style on all sides."""
        return cls(left=style, right=style, top=style, bottom=style, color=color)


class UnderlineStyle(str, Enum):
    """Underline style options."""

    NONE = "none"
    SINGLE = "single"
    DOUBLE = "double"


@dataclass(frozen=True)
class Font:
    """Font configuration."""

    family: Optional[str] = None
    size: Optional[int] = None
    bold: bool = False
    italic: bool = False
    underline: UnderlineStyle = UnderlineStyle.NONE
    strikethrough: bool = False
    color: Optional[Color] = None

    def __post_init__(self) -> None:
        if self.size is not None and self.size < 1:
            raise ValueError(f"Font size must be >= 1, got {self.size}")


class PatternFill(str, Enum):
    """Fill pattern options."""

    NONE = "none"
    SOLID = "solid"
    GRAY125 = "gray125"
    GRAY0625 = "gray0625"
    DARK_GRAY = "darkGray"
    LIGHT_GRAY = "lightGray"
    DARK_HORIZONTAL = "darkHorizontal"
    DARK_VERTICAL = "darkVertical"
    DARK_DOWN = "darkDown"
    DARK_UP = "darkUp"
    DARK_GRID = "darkGrid"
    DARK_TRELLIS = "darkTrellis"
    LIGHT_HORIZONTAL = "lightHorizontal"
    LIGHT_VERTICAL = "lightVertical"
    LIGHT_DOWN = "lightDown"
    LIGHT_UP = "lightUp"
    LIGHT_GRID = "lightGrid"
    LIGHT_TRELLIS = "lightTrellis"


@dataclass(frozen=True)
class Fill:
    """Fill configuration for cell background."""

    pattern: PatternFill = PatternFill.SOLID
    foreground_color: Optional[Color] = None
    background_color: Optional[Color] = None


@dataclass(frozen=True)
class CellStyle:
    """
    Complete cell style definition.

    This is the core style abstraction used throughout the engine.
    Adapters translate this to format-specific styling.
    """

    font: Optional[Font] = None
    fill: Optional[Fill] = None
    border: Optional[Border] = None
    alignment: Optional[Alignment] = None
    number_format: Optional[str] = None

    @classmethod
    def default(cls) -> CellStyle:
        """Create default cell style."""
        return cls()

    @classmethod
    def header(cls) -> CellStyle:
        """Create standard header style."""
        return cls(
            font=Font(bold=True, size=11),
            fill=Fill(
                pattern=PatternFill.SOLID,
                foreground_color=Color("D3D3D3"),
            ),
            alignment=Alignment(
                horizontal=HorizontalAlignment.CENTER,
                vertical=VerticalAlignment.CENTER,
            ),
            border=Border.all_sides(BorderStyle.THIN),
        )

    @classmethod
    def title(cls) -> CellStyle:
        """Create standard title style."""
        return cls(
            font=Font(bold=True, size=14),
            alignment=Alignment(
                horizontal=HorizontalAlignment.CENTER,
                vertical=VerticalAlignment.CENTER,
            ),
        )

    @classmethod
    def currency(cls) -> CellStyle:
        """Create currency style."""
        return cls(
            alignment=Alignment(horizontal=HorizontalAlignment.RIGHT),
        )

    @classmethod
    def percentage(cls) -> CellStyle:
        """Create percentage style."""
        return cls(
            alignment=Alignment(horizontal=HorizontalAlignment.RIGHT),
        )

    @classmethod
    def negative_value(cls) -> CellStyle:
        """Create style for negative values."""
        return cls(
            font=Font(color=Color("FF0000")),
            alignment=Alignment(horizontal=HorizontalAlignment.RIGHT),
        )

    def merge(self, other: Optional[CellStyle]) -> CellStyle:
        """
        Merge this style with another, with other taking precedence.

        Args:
            other: Style to merge with (can be None)

        Returns:
            New merged CellStyle
        """
        if other is None:
            return self

        return CellStyle(
            font=other.font if other.font is not None else self.font,
            fill=other.fill if other.fill is not None else self.fill,
            border=other.border if other.border is not None else self.border,
            alignment=other.alignment if other.alignment is not None else self.alignment,
            number_format=other.number_format
            if other.number_format is not None
            else self.number_format,
        )
