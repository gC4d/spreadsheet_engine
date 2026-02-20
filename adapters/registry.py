"""
Plugin-based adapter registry.

Supports lazy loading, optional dependencies, and capability discovery.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional, Set, Type

from .base import SpreadsheetAdapter


@dataclass
class AdapterCapabilities:
    """
    Adapter capability metadata.
    
    Describes what features an adapter supports.
    """

    supports_formulas: bool = True
    supports_styling: bool = True
    supports_conditional_formatting: bool = False
    supports_multiple_sheets: bool = True
    supports_streaming: bool = False
    supports_charts: bool = False
    max_rows: Optional[int] = None
    max_columns: Optional[int] = None


@dataclass
class AdapterPlugin:
    """
    Adapter plugin registration.
    
    Supports lazy loading to avoid importing optional dependencies.
    """

    format_name: str
    adapter_class: Optional[Type[SpreadsheetAdapter]]
    loader: Optional[Callable[[], Type[SpreadsheetAdapter]]]
    capabilities: AdapterCapabilities
    required_packages: Set[str]

    def get_adapter_class(self) -> Type[SpreadsheetAdapter]:
        """Get adapter class (lazy load if needed)."""
        if self.adapter_class is not None:
            return self.adapter_class

        if self.loader is None:
            raise RuntimeError(f"No adapter class or loader for format: {self.format_name}")

        # Lazy load
        self.adapter_class = self.loader()
        return self.adapter_class


class AdapterRegistry:
    """
    Plugin-based adapter registry.
    
    Features:
    - Lazy loading of adapters
    - Optional dependency handling
    - Capability discovery
    - Runtime registration
    """

    _plugins: Dict[str, AdapterPlugin] = {}

    @classmethod
    def register(
        cls,
        format_name: str,
        adapter_class: Optional[Type[SpreadsheetAdapter]] = None,
        loader: Optional[Callable[[], Type[SpreadsheetAdapter]]] = None,
        capabilities: Optional[AdapterCapabilities] = None,
        required_packages: Optional[Set[str]] = None,
    ) -> None:
        """
        Register an adapter plugin.
        
        Args:
            format_name: Format identifier (e.g., "xlsx", "csv", "pdf")
            adapter_class: Adapter class (if already imported)
            loader: Lazy loader function (if optional dependency)
            capabilities: Adapter capabilities
            required_packages: Required Python packages
            
        Example:
            # Eager registration
            AdapterRegistry.register("xlsx", XLSXAdapter, capabilities=...)
            
            # Lazy registration (optional dependency)
            AdapterRegistry.register(
                "pdf",
                loader=lambda: __import__("my_pdf_adapter").PDFAdapter,
                required_packages={"reportlab"},
            )
        """
        if adapter_class is None and loader is None:
            raise ValueError("Must provide either adapter_class or loader")

        plugin = AdapterPlugin(
            format_name=format_name,
            adapter_class=adapter_class,
            loader=loader,
            capabilities=capabilities or AdapterCapabilities(),
            required_packages=required_packages or set(),
        )

        cls._plugins[format_name] = plugin

    @classmethod
    def get_adapter(cls, format_name: str) -> SpreadsheetAdapter:
        """
        Get adapter instance for format.
        
        Args:
            format_name: Format identifier
            
        Returns:
            Adapter instance
            
        Raises:
            ValueError: If format not registered
            ImportError: If required packages not installed
        """
        if format_name not in cls._plugins:
            raise ValueError(
                f"No adapter registered for format: {format_name}. "
                f"Available formats: {', '.join(cls.list_formats())}"
            )

        plugin = cls._plugins[format_name]

        # Check required packages
        if plugin.required_packages:
            missing = cls._check_missing_packages(plugin.required_packages)
            if missing:
                raise ImportError(
                    f"Adapter for '{format_name}' requires packages: {', '.join(missing)}. "
                    f"Install with: pip install {' '.join(missing)}"
                )

        adapter_class = plugin.get_adapter_class()
        return adapter_class()

    @classmethod
    def get_adapter_by_name(cls, format_name: str) -> SpreadsheetAdapter:
        """Alias for get_adapter (for compatibility)."""
        return cls.get_adapter(format_name)

    @classmethod
    def list_formats(cls) -> list[str]:
        """List all registered format names."""
        return list(cls._plugins.keys())

    @classmethod
    def get_capabilities(cls, format_name: str) -> AdapterCapabilities:
        """
        Get capabilities for a format.
        
        Args:
            format_name: Format identifier
            
        Returns:
            AdapterCapabilities
        """
        if format_name not in cls._plugins:
            raise ValueError(f"No adapter registered for format: {format_name}")

        return cls._plugins[format_name].capabilities

    @classmethod
    def is_available(cls, format_name: str) -> bool:
        """
        Check if format is available (dependencies installed).
        
        Args:
            format_name: Format identifier
            
        Returns:
            True if adapter can be used
        """
        if format_name not in cls._plugins:
            return False

        plugin = cls._plugins[format_name]
        if not plugin.required_packages:
            return True

        missing = cls._check_missing_packages(plugin.required_packages)
        return len(missing) == 0

    @classmethod
    def get_supported_formats(cls) -> Dict[str, AdapterCapabilities]:
        """
        Get all supported formats with capabilities.
        
        Returns:
            Dict mapping format name to capabilities
        """
        return {
            name: plugin.capabilities
            for name, plugin in cls._plugins.items()
            if cls.is_available(name)
        }

    @classmethod
    def _check_missing_packages(cls, packages: Set[str]) -> Set[str]:
        """Check which packages are missing."""
        missing = set()
        for package in packages:
            try:
                __import__(package)
            except ImportError:
                missing.add(package)
        return missing


def register_default_adapters() -> None:
    """Register default adapters with capabilities."""
    
    # XLSX adapter (openpyxl)
    def load_xlsx():
        from .xlsx.adapter import XLSXAdapter
        return XLSXAdapter

    AdapterRegistry.register(
        format_name="xlsx",
        loader=load_xlsx,
        capabilities=AdapterCapabilities(
            supports_formulas=True,
            supports_styling=True,
            supports_conditional_formatting=True,
            supports_multiple_sheets=True,
            supports_streaming=False,
            supports_charts=False,
            max_rows=1_048_576,
            max_columns=16_384,
        ),
        required_packages={"openpyxl"},
    )

    # CSV adapter (built-in)
    def load_csv():
        from .csv.adapter import CSVAdapter
        return CSVAdapter

    AdapterRegistry.register(
        format_name="csv",
        loader=load_csv,
        capabilities=AdapterCapabilities(
            supports_formulas=False,
            supports_styling=False,
            supports_conditional_formatting=False,
            supports_multiple_sheets=False,
            supports_streaming=True,
            supports_charts=False,
            max_rows=None,
            max_columns=None,
        ),
        required_packages=set(),
    )


register_default_adapters()
