"""Main rendering engine."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Optional, Union

from ..adapters.base import SpreadsheetAdapter
from ..adapters.registry import AdapterRegistry, SpreadsheetFormat
from ..core.models.spreadsheet import Spreadsheet
from ..core.templates.data import SpreadsheetData
from ..core.templates.merger import TemplateMerger
from ..core.templates.template import SpreadsheetTemplate


class SpreadsheetRenderer:
    """
    Main rendering engine for spreadsheet generation.

    Orchestrates the process of:
    1. Merging templates with data
    2. Selecting appropriate adapter
    3. Rendering to output format
    """

    def __init__(
        self,
        adapter: Optional[SpreadsheetAdapter] = None,
        format: Optional[SpreadsheetFormat] = None,
    ) -> None:
        """
        Initialize renderer.

        Args:
            adapter: Optional adapter instance (overrides format)
            format: Output format (XLSX, CSV, etc.)
        """
        if adapter is not None and format is not None:
            raise ValueError("Provide either adapter or format, not both")

        self.adapter = adapter
        self.format = format or SpreadsheetFormat.XLSX

    def render(
        self,
        template: SpreadsheetTemplate,
        data: SpreadsheetData,
        output: Optional[Union[str, Path, BytesIO]] = None,
        autofit: bool = True,
        streaming: bool = False,
    ) -> Union[bytes, Path, None]:
        """
        Render spreadsheet from template and data.

        Args:
            template: Spreadsheet template
            data: Spreadsheet data
            output: Output path or BytesIO (if None, returns bytes)
            autofit: Whether to auto-fit column widths
            streaming: Whether to use streaming mode (for large datasets)

        Returns:
            Bytes if output is None, Path if output is path, None if output is BytesIO
        """
        spreadsheet = TemplateMerger.merge_spreadsheet(template, data)

        adapter = self._get_adapter()

        if streaming:
            return self._render_streaming(adapter, spreadsheet, output, autofit)
        else:
            return self._render_standard(adapter, spreadsheet, output, autofit)

    def _render_standard(
        self,
        adapter: SpreadsheetAdapter,
        spreadsheet: Spreadsheet,
        output: Optional[Union[str, Path, BytesIO]],
        autofit: bool,
    ) -> Union[bytes, Path, None]:
        """Render using standard mode."""
        workbook = adapter.render(spreadsheet, autofit=autofit)

        if output is None:
            return adapter.to_bytes(workbook)
        elif isinstance(output, BytesIO):
            adapter.to_stream(workbook, output)
            return None
        else:
            output_path = Path(output)
            adapter.to_file(workbook, output_path)
            return output_path

    def _render_streaming(
        self,
        adapter: SpreadsheetAdapter,
        spreadsheet: Spreadsheet,
        output: Optional[Union[str, Path, BytesIO]],
        autofit: bool,
    ) -> Union[bytes, Path, None]:
        """Render using streaming mode (for large datasets)."""
        if not hasattr(adapter, 'render_streaming'):
            raise ValueError(f"Adapter {type(adapter).__name__} does not support streaming")

        workbook = adapter.render_streaming(spreadsheet, autofit=autofit)

        if output is None:
            return adapter.to_bytes(workbook)
        elif isinstance(output, BytesIO):
            adapter.to_stream(workbook, output)
            return None
        else:
            output_path = Path(output)
            adapter.to_file(workbook, output_path)
            return output_path

    def _get_adapter(self) -> SpreadsheetAdapter:
        """Get adapter instance."""
        if self.adapter is not None:
            return self.adapter
        return AdapterRegistry.get_adapter(self.format)

    @classmethod
    def quick_render(
        cls,
        template: SpreadsheetTemplate,
        data: SpreadsheetData,
        output: Union[str, Path],
        format: SpreadsheetFormat = SpreadsheetFormat.XLSX,
    ) -> Path:
        """
        Quick render to file.

        Args:
            template: Spreadsheet template
            data: Spreadsheet data
            output: Output file path
            format: Output format

        Returns:
            Output path
        """
        renderer = cls(format=format)
        return renderer.render(template, data, output)
