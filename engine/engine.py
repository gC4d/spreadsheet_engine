"""
Unified Spreadsheet Engine - Production-grade rendering with observability.

This replaces the old SpreadsheetRenderer with a hardened, observable,
and performance-monitored implementation.
"""

from __future__ import annotations

import time
from io import BytesIO
from pathlib import Path
from typing import Optional, Union

from ..adapters.base import SpreadsheetAdapter
from ..adapters.registry import AdapterRegistry
from ..core.metrics import MetricsCollector, RenderMetrics
from ..core.models.spreadsheet import Spreadsheet
from ..core.observability import RenderEventLogger, SpreadsheetLogger, get_default_logger
from ..core.templates.data import SpreadsheetData
from ..core.templates.merger import TemplateMerger
from ..core.templates.template import SpreadsheetTemplate


class SpreadsheetEngine:
    """
    Production-grade spreadsheet rendering engine.
    
    Features:
    - Performance monitoring with metrics
    - Structured logging and observability
    - Plugin-based adapter system
    - Memory-safe streaming
    - Template versioning
    - Performance contracts
    
    This is the internal engine. Users should interact with Report classes,
    not this engine directly.
    """

    def __init__(self, logger: Optional[SpreadsheetLogger] = None):
        """
        Initialize engine.
        
        Args:
            logger: Optional logger (uses default if None)
        """
        self._logger = logger or get_default_logger()
        self._event_logger = RenderEventLogger(self._logger)

    def render(
        self,
        template: SpreadsheetTemplate,
        data: SpreadsheetData,
        output: Union[str, Path],
        format: str = "xlsx",
        autofit: bool = True,
        streaming: bool = False,
        collect_metrics: bool = True,
    ) -> Path:
        """
        Render spreadsheet to file.
        
        Args:
            template: Spreadsheet template
            data: Spreadsheet data
            output: Output file path
            format: Output format ("xlsx", "csv")
            autofit: Whether to auto-fit column widths
            streaming: Whether to use streaming mode
            collect_metrics: Whether to collect performance metrics
            
        Returns:
            Path to generated file
        """
        output_path = Path(output)

        if collect_metrics:
            with MetricsCollector() as collector:
                result = self._render_with_metrics(
                    template=template,
                    data=data,
                    output=output_path,
                    format=format,
                    autofit=autofit,
                    streaming=streaming,
                    collector=collector,
                )
            return result
        else:
            return self._render_internal(
                template=template,
                data=data,
                output=output_path,
                format=format,
                autofit=autofit,
                streaming=streaming,
            )

    def render_to_bytes(
        self,
        template: SpreadsheetTemplate,
        data: SpreadsheetData,
        format: str = "xlsx",
        autofit: bool = True,
        streaming: bool = False,
        collect_metrics: bool = True,
    ) -> bytes:
        """
        Render spreadsheet to bytes.
        
        Args:
            template: Spreadsheet template
            data: Spreadsheet data
            format: Output format
            autofit: Whether to auto-fit column widths
            streaming: Whether to use streaming mode
            collect_metrics: Whether to collect performance metrics
            
        Returns:
            Bytes representation
        """
        if collect_metrics:
            with MetricsCollector() as collector:
                result = self._render_to_bytes_with_metrics(
                    template=template,
                    data=data,
                    format=format,
                    autofit=autofit,
                    streaming=streaming,
                    collector=collector,
                )
            return result
        else:
            return self._render_to_bytes_internal(
                template=template,
                data=data,
                format=format,
                autofit=autofit,
                streaming=streaming,
            )

    def _render_with_metrics(
        self,
        template: SpreadsheetTemplate,
        data: SpreadsheetData,
        output: Path,
        format: str,
        autofit: bool,
        streaming: bool,
        collector: MetricsCollector,
    ) -> Path:
        """Render with metrics collection."""
        report_type = template.metadata.get("report_type", "unknown")
        template_version = template.metadata.get("template_version", "unknown")

        # Estimate row count
        estimated_rows = sum(
            table_data.row_count
            for sheet_data in data.sheet_data.values()
            for table_data in sheet_data.table_data.values()
        )

        self._event_logger.render_started(
            report_type=report_type,
            template_version=template_version,
            format=format,
            streaming=streaming,
            row_count=estimated_rows,
        )

        start_time = time.perf_counter()

        try:
            result = self._render_internal(
                template=template,
                data=data,
                output=output,
                format=format,
                autofit=autofit,
                streaming=streaming,
                collector=collector,
            )

            # Collect metrics
            metrics = collector.get_metrics(
                streaming_enabled=streaming,
                format=format,
                autofit_enabled=autofit,
                template_version=template_version,
                report_type=report_type,
            )

            self._event_logger.render_completed(
                report_type=report_type,
                metrics=metrics,
            )

            # Check performance contract
            meets_contract, violations = metrics.meets_performance_contract()
            if not meets_contract:
                self._event_logger.contract_violation(
                    violations=violations,
                    metrics=metrics,
                )

            return result

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self._event_logger.render_failed(
                report_type=report_type,
                error=e,
                duration_ms=duration_ms,
            )
            raise

    def _render_to_bytes_with_metrics(
        self,
        template: SpreadsheetTemplate,
        data: SpreadsheetData,
        format: str,
        autofit: bool,
        streaming: bool,
        collector: MetricsCollector,
    ) -> bytes:
        """Render to bytes with metrics collection."""
        report_type = template.metadata.get("report_type", "unknown")
        template_version = template.metadata.get("template_version", "unknown")

        estimated_rows = sum(
            table_data.row_count
            for sheet_data in data.sheet_data.values()
            for table_data in sheet_data.table_data.values()
        )

        self._event_logger.render_started(
            report_type=report_type,
            template_version=template_version,
            format=format,
            streaming=streaming,
            row_count=estimated_rows,
        )

        start_time = time.perf_counter()

        try:
            result = self._render_to_bytes_internal(
                template=template,
                data=data,
                format=format,
                autofit=autofit,
                streaming=streaming,
                collector=collector,
            )

            metrics = collector.get_metrics(
                streaming_enabled=streaming,
                format=format,
                autofit_enabled=autofit,
                template_version=template_version,
                report_type=report_type,
            )

            self._event_logger.render_completed(
                report_type=report_type,
                metrics=metrics,
            )

            meets_contract, violations = metrics.meets_performance_contract()
            if not meets_contract:
                self._event_logger.contract_violation(
                    violations=violations,
                    metrics=metrics,
                )

            return result

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self._event_logger.render_failed(
                report_type=report_type,
                error=e,
                duration_ms=duration_ms,
            )
            raise

    def _render_internal(
        self,
        template: SpreadsheetTemplate,
        data: SpreadsheetData,
        output: Path,
        format: str,
        autofit: bool,
        streaming: bool,
        collector: Optional[MetricsCollector] = None,
    ) -> Path:
        """Internal render implementation."""
        # Merge template with data
        if collector:
            collector.start_merge()

        spreadsheet = TemplateMerger.merge_spreadsheet(template, data)

        if collector:
            collector.end_merge()
            collector.record_sheets(spreadsheet.sheet_count)
            # Count tables and rows
            total_rows = 0
            total_tables = 0
            for sheet in spreadsheet.sheets:
                total_tables += len(sheet.tables)
                for table in sheet.tables:
                    total_rows += table.row_count
            collector.record_tables(total_tables)
            collector.record_rows(total_rows)
            collector.update_peak_memory()

        # Get adapter
        adapter = AdapterRegistry.get_adapter_by_name(format)
        
        self._event_logger.adapter_selected(
            adapter_type=type(adapter).__name__,
            format=format,
        )

        # Render
        if collector:
            collector.start_adapter()

        if streaming and hasattr(adapter, 'render_streaming'):
            workbook = adapter.render_streaming(spreadsheet, autofit=autofit)
        else:
            workbook = adapter.render(spreadsheet, autofit=autofit)

        if collector:
            collector.end_adapter()
            collector.update_peak_memory()

        # Write to file
        if collector:
            collector.start_io()

        output.parent.mkdir(parents=True, exist_ok=True)
        adapter.to_file(workbook, output)

        if collector:
            collector.end_io()

        return output

    def _render_to_bytes_internal(
        self,
        template: SpreadsheetTemplate,
        data: SpreadsheetData,
        format: str,
        autofit: bool,
        streaming: bool,
        collector: Optional[MetricsCollector] = None,
    ) -> bytes:
        """Internal render to bytes implementation."""
        # Merge
        if collector:
            collector.start_merge()

        spreadsheet = TemplateMerger.merge_spreadsheet(template, data)

        if collector:
            collector.end_merge()
            collector.record_sheets(spreadsheet.sheet_count)
            total_rows = sum(table.row_count for sheet in spreadsheet.sheets for table in sheet.tables)
            total_tables = sum(len(sheet.tables) for sheet in spreadsheet.sheets)
            collector.record_tables(total_tables)
            collector.record_rows(total_rows)
            collector.update_peak_memory()

        # Get adapter
        adapter = AdapterRegistry.get_adapter_by_name(format)

        # Render
        if collector:
            collector.start_adapter()

        if streaming and hasattr(adapter, 'render_streaming'):
            workbook = adapter.render_streaming(spreadsheet, autofit=autofit)
        else:
            workbook = adapter.render(spreadsheet, autofit=autofit)

        if collector:
            collector.end_adapter()
            collector.update_peak_memory()

        # Convert to bytes
        if collector:
            collector.start_io()

        result = adapter.to_bytes(workbook)

        if collector:
            collector.end_io()

        return result
