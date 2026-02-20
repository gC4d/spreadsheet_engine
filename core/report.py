"""
Report abstraction - Simplified public API.

This is the primary interface for consumers. Users should never directly
instantiate templates, renderers, or adapters.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Protocol

from .templates.data import SpreadsheetData
from .templates.template import SpreadsheetTemplate


class ReportMapper(Protocol):
    """
    Protocol for mapping domain models to spreadsheet data.
    
    Each report must implement this to transform domain entities
    into the spreadsheet data format.
    """

    def map(self, domain_model: Any) -> SpreadsheetData:
        """
        Map domain model to spreadsheet data.
        
        Args:
            domain_model: Domain entity or collection
            
        Returns:
            SpreadsheetData ready for rendering
        """
        ...


@dataclass
class ReportMetadata:
    """
    Metadata embedded in every report.
    
    Used for versioning, governance, and debugging.
    """

    report_type: str
    version: str
    template_version: str
    created_by: str = "SpreadsheetEngine"
    description: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for embedding."""
        result = {
            "report_type": self.report_type,
            "version": self.version,
            "template_version": self.template_version,
            "created_by": self.created_by,
        }
        if self.description:
            result["description"] = self.description
        result.update(self.tags)
        return result


class Report(ABC):
    """
    Base class for all reports.
    
    This is the primary public API. Users interact with concrete
    report classes (DREReport, SalesReport, etc.) and never need
    to know about templates, renderers, or adapters.
    
    Usage:
        report = DREReport.from_domain(financial_data)
        report.export("dre.xlsx")
    """

    def __init__(self, data: SpreadsheetData, metadata: ReportMetadata):
        """
        Initialize report.
        
        Args:
            data: Spreadsheet data (already mapped from domain)
            metadata: Report metadata
        """
        self._data = data
        self._metadata = metadata
        self._template: Optional[SpreadsheetTemplate] = None

    @classmethod
    @abstractmethod
    def from_domain(cls, domain_model: Any, **kwargs) -> Report:
        """
        Create report from domain model.
        
        This is the primary factory method. Subclasses must implement
        the domain-to-data mapping logic.
        
        Args:
            domain_model: Domain entity or collection
            **kwargs: Additional configuration
            
        Returns:
            Report instance ready to export
        """
        ...

    @abstractmethod
    def _create_template(self) -> SpreadsheetTemplate:
        """
        Create the template for this report.
        
        Called lazily on first export. Subclasses define the layout here.
        
        Returns:
            SpreadsheetTemplate defining the report structure
        """
        ...

    @abstractmethod
    def _get_metadata(self) -> ReportMetadata:
        """
        Get report metadata.
        
        Returns:
            ReportMetadata with version and type information
        """
        ...

    def export(
        self,
        output: str | Path,
        format: str = "xlsx",
        **options,
    ) -> Path:
        """
        Export report to file.
        
        This is the primary public method. All complexity is hidden.
        
        Args:
            output: Output file path
            format: Output format ("xlsx", "csv")
            **options: Format-specific options (autofit, streaming, etc.)
            
        Returns:
            Path to generated file
            
        Example:
            report.export("sales.xlsx")
            report.export("data.csv", format="csv")
            report.export("large.xlsx", streaming=True, autofit=False)
        """
        from ..engine.engine import SpreadsheetEngine

        if self._template is None:
            self._template = self._create_template()

        # Embed metadata
        self._data.metadata.update(self._metadata.to_dict())
        self._template.metadata.update(self._metadata.to_dict())

        output_path = Path(output)
        
        engine = SpreadsheetEngine()
        return engine.render(
            template=self._template,
            data=self._data,
            output=output_path,
            format=format,
            **options,
        )

    def to_bytes(self, format: str = "xlsx", **options) -> bytes:
        """
        Export report to bytes (for HTTP responses).
        
        Args:
            format: Output format
            **options: Format-specific options
            
        Returns:
            Bytes representation
            
        Example:
            data = report.to_bytes()
            return HttpResponse(data, content_type="application/vnd.ms-excel")
        """
        from ..engine.engine import SpreadsheetEngine

        if self._template is None:
            self._template = self._create_template()

        # Embed metadata
        self._data.metadata.update(self._metadata.to_dict())
        self._template.metadata.update(self._metadata.to_dict())

        engine = SpreadsheetEngine()
        return engine.render_to_bytes(
            template=self._template,
            data=self._data,
            format=format,
            **options,
        )

    @property
    def metadata(self) -> ReportMetadata:
        """Get report metadata."""
        return self._metadata

    @property
    def data(self) -> SpreadsheetData:
        """Get spreadsheet data (for testing/inspection)."""
        return self._data
