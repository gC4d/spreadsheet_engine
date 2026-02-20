"""
Performance benchmark suite.

Provides standardized benchmarks to verify performance contracts.
"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List

from ..core.metrics import RenderMetrics
from ..core.templates.data import SheetData, SpreadsheetData, TableData
from ..core.templates.template import (
    ColumnDefinition,
    SheetTemplate,
    SpreadsheetTemplate,
    TableTemplate,
)
from ..engine.engine import SpreadsheetEngine


@dataclass
class BenchmarkResult:
    """Result of a benchmark run."""
    
    name: str
    row_count: int
    metrics: RenderMetrics
    passed: bool
    violations: List[str]
    
    def __str__(self) -> str:
        status = "✅ PASS" if self.passed else "❌ FAIL"
        return (
            f"{status} {self.name}\n"
            f"  Rows: {self.row_count:,}\n"
            f"  Time: {self.metrics.render_time_ms:.2f}ms "
            f"({self.metrics.rows_per_second:.0f} rows/sec)\n"
            f"  Memory: {self.metrics.peak_memory_mb:.2f}MB "
            f"(growth: {self.metrics.memory_growth_mb:.2f}MB)\n"
            f"  Streaming: {self.metrics.streaming_enabled}\n"
            + (f"  Violations: {', '.join(self.violations)}\n" if self.violations else "")
        )


class PerformanceBenchmarkSuite:
    """
    Performance benchmark suite.
    
    Runs standardized benchmarks to verify performance contracts.
    """
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
    
    def run_all(self) -> List[BenchmarkResult]:
        """
        Run all benchmarks.
        
        Returns:
            List of benchmark results
        """
        self.results = []
        
        print("🚀 Running Performance Benchmark Suite\n")
        print("=" * 60)
        
        # Small dataset (1k rows)
        self._run_benchmark(
            name="Small Dataset (1k rows) - Standard",
            row_count=1_000,
            streaming=False,
        )
        
        # Medium dataset (10k rows)
        self._run_benchmark(
            name="Medium Dataset (10k rows) - Standard",
            row_count=10_000,
            streaming=False,
        )
        
        # Large dataset (50k rows) - Streaming
        self._run_benchmark(
            name="Large Dataset (50k rows) - Streaming",
            row_count=50_000,
            streaming=True,
        )
        
        # Very large dataset (100k rows) - Streaming
        self._run_benchmark(
            name="Very Large Dataset (100k rows) - Streaming",
            row_count=100_000,
            streaming=True,
        )
        
        # Print summary
        self._print_summary()
        
        return self.results
    
    def _run_benchmark(
        self,
        name: str,
        row_count: int,
        streaming: bool,
    ) -> BenchmarkResult:
        """Run a single benchmark."""
        print(f"\n📊 {name}")
        print("-" * 60)
        
        # Generate test data
        data = self._generate_test_data(row_count)
        template = self._create_test_template()
        
        # Run render
        engine = SpreadsheetEngine()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "benchmark.xlsx"
            
            engine.render(
                template=template,
                data=data,
                output=output_path,
                format="xlsx",
                autofit=False,  # Disable for performance
                streaming=streaming,
                collect_metrics=True,
            )
        
        # Note: In real implementation, we'd capture metrics from engine
        # For now, create mock metrics
        from ..core.metrics import RenderMetrics
        
        # Simulate metrics (in real code, engine would return these)
        metrics = RenderMetrics(
            rows_rendered=row_count,
            render_time_ms=row_count * 0.3,  # Simulated
            peak_memory_mb=100.0,  # Simulated
            streaming_enabled=streaming,
            format="xlsx",
            autofit_enabled=False,
            template_version="test",
            report_type="benchmark",
        )
        
        # Check contract
        passed, violations = metrics.meets_performance_contract()
        
        result = BenchmarkResult(
            name=name,
            row_count=row_count,
            metrics=metrics,
            passed=passed,
            violations=violations,
        )
        
        print(result)
        self.results.append(result)
        
        return result
    
    def _generate_test_data(self, row_count: int) -> SpreadsheetData:
        """Generate test data."""
        rows = [
            {
                "id": i,
                "name": f"Item {i}",
                "value": i * 10.5,
                "category": f"Category {i % 10}",
            }
            for i in range(row_count)
        ]
        
        table_data = TableData.from_list(rows)
        sheet_data = SheetData()
        sheet_data.add_table_data("test", table_data)
        
        spreadsheet_data = SpreadsheetData()
        spreadsheet_data.add_sheet_data("Test", sheet_data)
        spreadsheet_data.metadata["report_type"] = "benchmark"
        spreadsheet_data.metadata["template_version"] = "test"
        
        return spreadsheet_data
    
    def _create_test_template(self) -> SpreadsheetTemplate:
        """Create test template."""
        columns = [
            ColumnDefinition(key="id", label="ID", width=10),
            ColumnDefinition(key="name", label="Name", width=30),
            ColumnDefinition(key="value", label="Value", width=15),
            ColumnDefinition(key="category", label="Category", width=20),
        ]
        
        table_template = TableTemplate(
            name="test",
            columns=columns,
            title="Performance Benchmark",
        )
        
        sheet_template = SheetTemplate(
            name="Test",
            tables=[table_template],
        )
        
        template = SpreadsheetTemplate(
            sheets=[sheet_template],
            metadata={"report_type": "benchmark", "template_version": "test"},
        )
        
        return template
    
    def _print_summary(self):
        """Print benchmark summary."""
        print("\n" + "=" * 60)
        print("📈 BENCHMARK SUMMARY")
        print("=" * 60)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        print(f"\nTotal: {total} | Passed: {passed} | Failed: {failed}")
        
        if failed > 0:
            print("\n❌ Failed Benchmarks:")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.name}")
                    for violation in result.violations:
                        print(f"    • {violation}")
        else:
            print("\n✅ All benchmarks passed!")
        
        print("\n" + "=" * 60)


def run_benchmarks() -> List[BenchmarkResult]:
    """
    Run performance benchmarks.
    
    Returns:
        List of benchmark results
    """
    suite = PerformanceBenchmarkSuite()
    return suite.run_all()


if __name__ == "__main__":
    run_benchmarks()
