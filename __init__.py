"""
Enterprise Spreadsheet Engine - Production Grade.

A complete, extensible, enterprise-grade spreadsheet generation system
with performance guarantees, observability, and simplified public API.

PUBLIC API (Use these):
    - Report classes (DREReport, etc.)
    - AdapterRegistry (for plugin management)
    - Performance benchmarks

INTERNAL API (Advanced use only):
    - Core models, templates, styles
    - Engine internals
"""

# ============================================================================
# PUBLIC API - Use these for normal operations
# ============================================================================

# Reports (Primary API)
from .reports.financial.dre_report import DREReport, DREData, DRELineItem, create_dre_report

# Adapter Registry (Plugin management)
from .adapters.registry import AdapterRegistry, AdapterCapabilities

# Observability (Optional)
from .core.observability import (
    set_default_logger,
    get_default_logger,
    StandardLogger,
    NullLogger,
)

# Governance (Optional)
from .core.governance import TemplateRegistry, ReportRegistry

# Benchmarks (Testing)
from .benchmarks.performance_suite import run_benchmarks

# ============================================================================
# INTERNAL API - For advanced use and custom reports
# ============================================================================

# Core Report abstraction
from .core.report import Report, ReportMapper, ReportMetadata

# Metrics
from .core.metrics import RenderMetrics, MetricsCollector, PerformanceContract

# Core models
from .core.models.cell import Cell, CellDataType
from .core.models.position import CellPosition, CellRange
from .core.models.sheet import Sheet
from .core.models.spreadsheet import Spreadsheet
from .core.models.table import Table

# Styles
from .core.styles.cell_style import (
    Alignment,
    Border,
    BorderStyle,
    CellStyle,
    Color,
    Fill,
    Font,
    HorizontalAlignment,
    PatternFill,
    VerticalAlignment,
)
from .core.styles.conditional import ConditionalRule, RuleType
from .core.styles.number_format import NumberFormat

# Templates
from .core.templates.data import SheetData, SpreadsheetData, TableData
from .core.templates.template import (
    ColumnDefinition,
    SectionDefinition,
    SheetTemplate,
    SpreadsheetTemplate,
    TableTemplate,
)

# Engine
from .engine.engine import SpreadsheetEngine

__all__ = [
    # ========================================================================
    # PUBLIC API
    # ========================================================================
    # Reports
    "DREReport",
    "DREData",
    "DRELineItem",
    "create_dre_report",
    # Adapter management
    "AdapterRegistry",
    "AdapterCapabilities",
    # Observability
    "set_default_logger",
    "get_default_logger",
    "StandardLogger",
    "NullLogger",
    # Governance
    "TemplateRegistry",
    "ReportRegistry",
    # Benchmarks
    "run_benchmarks",
    
    # ========================================================================
    # INTERNAL API (Advanced)
    # ========================================================================
    # Report abstraction
    "Report",
    "ReportMapper",
    "ReportMetadata",
    # Metrics
    "RenderMetrics",
    "MetricsCollector",
    "PerformanceContract",
    # Core models
    "Cell",
    "CellDataType",
    "CellPosition",
    "CellRange",
    "Sheet",
    "Spreadsheet",
    "Table",
    # Styles
    "Alignment",
    "Border",
    "BorderStyle",
    "CellStyle",
    "Color",
    "Fill",
    "Font",
    "HorizontalAlignment",
    "PatternFill",
    "VerticalAlignment",
    "ConditionalRule",
    "RuleType",
    "NumberFormat",
    # Templates
    "SheetData",
    "SpreadsheetData",
    "TableData",
    "ColumnDefinition",
    "SectionDefinition",
    "SheetTemplate",
    "SpreadsheetTemplate",
    "TableTemplate",
    # Engine
    "SpreadsheetEngine",
]

# Version
__version__ = "2.0.0"
