"""
Performance metrics and contracts.

Provides measurable performance guarantees and monitoring.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional
import psutil
import os


@dataclass
class RenderMetrics:
    """
    Performance metrics for spreadsheet rendering.
    
    Captures actual performance data to verify contracts are met.
    """

    rows_rendered: int
    render_time_ms: float
    peak_memory_mb: float
    streaming_enabled: bool
    format: str
    autofit_enabled: bool
    template_version: str
    report_type: str
    
    # Additional metrics
    sheet_count: int = 0
    table_count: int = 0
    cell_count: int = 0
    formula_count: int = 0
    
    # Memory details
    initial_memory_mb: float = 0.0
    final_memory_mb: float = 0.0
    
    # Timing breakdown
    merge_time_ms: float = 0.0
    adapter_time_ms: float = 0.0
    io_time_ms: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary for logging."""
        return {
            "rows_rendered": self.rows_rendered,
            "render_time_ms": round(self.render_time_ms, 2),
            "peak_memory_mb": round(self.peak_memory_mb, 2),
            "streaming_enabled": self.streaming_enabled,
            "format": self.format,
            "autofit_enabled": self.autofit_enabled,
            "template_version": self.template_version,
            "report_type": self.report_type,
            "sheet_count": self.sheet_count,
            "table_count": self.table_count,
            "cell_count": self.cell_count,
            "formula_count": self.formula_count,
            "memory_growth_mb": round(self.final_memory_mb - self.initial_memory_mb, 2),
            "merge_time_ms": round(self.merge_time_ms, 2),
            "adapter_time_ms": round(self.adapter_time_ms, 2),
            "io_time_ms": round(self.io_time_ms, 2),
        }

    @property
    def memory_growth_mb(self) -> float:
        """Memory growth during rendering."""
        return self.final_memory_mb - self.initial_memory_mb

    @property
    def rows_per_second(self) -> float:
        """Rendering throughput."""
        if self.render_time_ms == 0:
            return 0
        return (self.rows_rendered / self.render_time_ms) * 1000

    def meets_performance_contract(self) -> tuple[bool, list[str]]:
        """
        Check if metrics meet performance contracts.
        
        Returns:
            (meets_contract, violations)
        """
        violations = []

        # Contract: Must support 100k rows
        if self.rows_rendered > 100000:
            violations.append(f"Row count {self.rows_rendered} exceeds tested limit of 100k")

        # Contract: Streaming must not grow memory linearly
        if self.streaming_enabled:
            # Memory should not grow more than 500MB for any dataset when streaming
            if self.memory_growth_mb > 500:
                violations.append(
                    f"Streaming memory growth {self.memory_growth_mb}MB exceeds 500MB limit"
                )
        else:
            # Non-streaming: reasonable limit for small datasets
            if self.rows_rendered < 10000 and self.memory_growth_mb > 200:
                violations.append(
                    f"Memory growth {self.memory_growth_mb}MB excessive for {self.rows_rendered} rows"
                )

        # Contract: Reasonable rendering time
        # Target: < 1ms per row for standard mode, < 0.5ms per row for streaming
        if self.streaming_enabled:
            max_ms_per_row = 0.5
        else:
            max_ms_per_row = 1.0

        if self.rows_rendered > 0:
            actual_ms_per_row = self.render_time_ms / self.rows_rendered
            if actual_ms_per_row > max_ms_per_row:
                violations.append(
                    f"Render time {actual_ms_per_row:.3f}ms/row exceeds {max_ms_per_row}ms/row target"
                )

        return len(violations) == 0, violations


class MetricsCollector:
    """
    Collects performance metrics during rendering.
    
    Usage:
        with MetricsCollector() as collector:
            # render spreadsheet
            collector.record_rows(1000)
            
        metrics = collector.get_metrics(...)
    """

    def __init__(self):
        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None
        self._initial_memory: Optional[float] = None
        self._peak_memory: float = 0.0
        self._final_memory: Optional[float] = None
        
        self._rows_rendered: int = 0
        self._sheet_count: int = 0
        self._table_count: int = 0
        self._cell_count: int = 0
        self._formula_count: int = 0
        
        self._merge_start: Optional[float] = None
        self._merge_time: float = 0.0
        self._adapter_start: Optional[float] = None
        self._adapter_time: float = 0.0
        self._io_start: Optional[float] = None
        self._io_time: float = 0.0

    def __enter__(self):
        """Start metrics collection."""
        self._start_time = time.perf_counter()
        self._initial_memory = self._get_memory_mb()
        self._peak_memory = self._initial_memory
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End metrics collection."""
        self._end_time = time.perf_counter()
        self._final_memory = self._get_memory_mb()
        self._peak_memory = max(self._peak_memory, self._final_memory)

    def _get_memory_mb(self) -> float:
        """Get current process memory in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024

    def update_peak_memory(self):
        """Update peak memory (call periodically during rendering)."""
        current = self._get_memory_mb()
        self._peak_memory = max(self._peak_memory, current)

    def record_rows(self, count: int):
        """Record number of rows rendered."""
        self._rows_rendered += count

    def record_sheets(self, count: int):
        """Record number of sheets."""
        self._sheet_count += count

    def record_tables(self, count: int):
        """Record number of tables."""
        self._table_count += count

    def record_cells(self, count: int):
        """Record number of cells."""
        self._cell_count += count

    def record_formulas(self, count: int):
        """Record number of formulas."""
        self._formula_count += count

    def start_merge(self):
        """Start timing merge phase."""
        self._merge_start = time.perf_counter()

    def end_merge(self):
        """End timing merge phase."""
        if self._merge_start:
            self._merge_time = (time.perf_counter() - self._merge_start) * 1000

    def start_adapter(self):
        """Start timing adapter phase."""
        self._adapter_start = time.perf_counter()

    def end_adapter(self):
        """End timing adapter phase."""
        if self._adapter_start:
            self._adapter_time = (time.perf_counter() - self._adapter_start) * 1000

    def start_io(self):
        """Start timing I/O phase."""
        self._io_start = time.perf_counter()

    def end_io(self):
        """End timing I/O phase."""
        if self._io_start:
            self._io_time = (time.perf_counter() - self._io_start) * 1000

    def get_metrics(
        self,
        streaming_enabled: bool,
        format: str,
        autofit_enabled: bool,
        template_version: str,
        report_type: str,
    ) -> RenderMetrics:
        """
        Get collected metrics.
        
        Args:
            streaming_enabled: Whether streaming was used
            format: Output format
            autofit_enabled: Whether autofit was enabled
            template_version: Template version
            report_type: Report type
            
        Returns:
            RenderMetrics instance
        """
        if self._start_time is None or self._end_time is None:
            raise RuntimeError("MetricsCollector not properly used with context manager")

        render_time_ms = (self._end_time - self._start_time) * 1000

        return RenderMetrics(
            rows_rendered=self._rows_rendered,
            render_time_ms=render_time_ms,
            peak_memory_mb=self._peak_memory,
            streaming_enabled=streaming_enabled,
            format=format,
            autofit_enabled=autofit_enabled,
            template_version=template_version,
            report_type=report_type,
            sheet_count=self._sheet_count,
            table_count=self._table_count,
            cell_count=self._cell_count,
            formula_count=self._formula_count,
            initial_memory_mb=self._initial_memory or 0.0,
            final_memory_mb=self._final_memory or 0.0,
            merge_time_ms=self._merge_time,
            adapter_time_ms=self._adapter_time,
            io_time_ms=self._io_time,
        )


@dataclass
class PerformanceContract:
    """
    Performance contract definition.
    
    Defines guaranteed performance characteristics.
    """

    max_rows: int = 100_000
    max_memory_growth_mb_streaming: float = 500.0
    max_memory_growth_mb_standard: float = 200.0
    max_ms_per_row_streaming: float = 0.5
    max_ms_per_row_standard: float = 1.0
    
    def validate(self, metrics: RenderMetrics) -> tuple[bool, list[str]]:
        """
        Validate metrics against contract.
        
        Returns:
            (is_valid, violations)
        """
        return metrics.meets_performance_contract()
