"""
Governance features - Template registry, deprecation, and change tracking.

Provides enterprise governance for templates and reports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set


class DeprecationStatus(str, Enum):
    """Deprecation status."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    REMOVED = "removed"


@dataclass
class ChangeLogEntry:
    """Change log entry for template versioning."""
    
    version: str
    date: str
    changes: List[str]
    breaking_changes: List[str] = field(default_factory=list)
    author: str = "system"
    
    def is_breaking(self) -> bool:
        """Check if this version has breaking changes."""
        return len(self.breaking_changes) > 0


@dataclass
class TemplateRegistration:
    """Template registration metadata."""
    
    template_id: str
    template_type: str
    version: str
    status: DeprecationStatus
    registered_at: str
    deprecated_at: Optional[str] = None
    removed_at: Optional[str] = None
    replacement: Optional[str] = None
    changelog: List[ChangeLogEntry] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    
    def deprecate(self, replacement: Optional[str] = None) -> None:
        """Mark template as deprecated."""
        self.status = DeprecationStatus.DEPRECATED
        self.deprecated_at = datetime.utcnow().isoformat()
        self.replacement = replacement
    
    def remove(self) -> None:
        """Mark template as removed."""
        self.status = DeprecationStatus.REMOVED
        self.removed_at = datetime.utcnow().isoformat()
    
    def add_changelog(self, entry: ChangeLogEntry) -> None:
        """Add changelog entry."""
        self.changelog.append(entry)
        self.version = entry.version


@dataclass
class ReportRegistration:
    """Report registration metadata."""
    
    report_id: str
    report_type: str
    template_id: str
    version: str
    status: DeprecationStatus
    registered_at: str
    deprecated_at: Optional[str] = None
    removed_at: Optional[str] = None
    replacement: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    
    def deprecate(self, replacement: Optional[str] = None) -> None:
        """Mark report as deprecated."""
        self.status = DeprecationStatus.DEPRECATED
        self.deprecated_at = datetime.utcnow().isoformat()
        self.replacement = replacement
    
    def remove(self) -> None:
        """Mark report as removed."""
        self.status = DeprecationStatus.REMOVED
        self.removed_at = datetime.utcnow().isoformat()


class TemplateRegistry:
    """
    Registry for template governance.
    
    Tracks template versions, deprecation, and changes.
    """
    
    _templates: Dict[str, TemplateRegistration] = {}
    
    @classmethod
    def register(
        cls,
        template_id: str,
        template_type: str,
        version: str,
        tags: Optional[Set[str]] = None,
    ) -> TemplateRegistration:
        """
        Register a template.
        
        Args:
            template_id: Unique template identifier
            template_type: Template type (e.g., "DRE", "BalanceSheet")
            version: Template version
            tags: Optional tags
            
        Returns:
            TemplateRegistration
        """
        registration = TemplateRegistration(
            template_id=template_id,
            template_type=template_type,
            version=version,
            status=DeprecationStatus.ACTIVE,
            registered_at=datetime.utcnow().isoformat(),
            tags=tags or set(),
        )
        
        cls._templates[template_id] = registration
        return registration
    
    @classmethod
    def get(cls, template_id: str) -> Optional[TemplateRegistration]:
        """Get template registration."""
        return cls._templates.get(template_id)
    
    @classmethod
    def deprecate(
        cls,
        template_id: str,
        replacement: Optional[str] = None,
    ) -> None:
        """
        Deprecate a template.
        
        Args:
            template_id: Template to deprecate
            replacement: Optional replacement template ID
        """
        if template_id not in cls._templates:
            raise ValueError(f"Template not registered: {template_id}")
        
        cls._templates[template_id].deprecate(replacement)
    
    @classmethod
    def list_active(cls) -> List[TemplateRegistration]:
        """List all active templates."""
        return [
            reg for reg in cls._templates.values()
            if reg.status == DeprecationStatus.ACTIVE
        ]
    
    @classmethod
    def list_deprecated(cls) -> List[TemplateRegistration]:
        """List all deprecated templates."""
        return [
            reg for reg in cls._templates.values()
            if reg.status == DeprecationStatus.DEPRECATED
        ]
    
    @classmethod
    def find_by_type(cls, template_type: str) -> List[TemplateRegistration]:
        """Find templates by type."""
        return [
            reg for reg in cls._templates.values()
            if reg.template_type == template_type
        ]
    
    @classmethod
    def find_by_tag(cls, tag: str) -> List[TemplateRegistration]:
        """Find templates by tag."""
        return [
            reg for reg in cls._templates.values()
            if tag in reg.tags
        ]


class ReportRegistry:
    """
    Registry for report governance.
    
    Tracks report implementations and their templates.
    """
    
    _reports: Dict[str, ReportRegistration] = {}
    
    @classmethod
    def register(
        cls,
        report_id: str,
        report_type: str,
        template_id: str,
        version: str,
        tags: Optional[Set[str]] = None,
    ) -> ReportRegistration:
        """
        Register a report.
        
        Args:
            report_id: Unique report identifier
            report_type: Report type
            template_id: Associated template ID
            version: Report version
            tags: Optional tags
            
        Returns:
            ReportRegistration
        """
        registration = ReportRegistration(
            report_id=report_id,
            report_type=report_type,
            template_id=template_id,
            version=version,
            status=DeprecationStatus.ACTIVE,
            registered_at=datetime.utcnow().isoformat(),
            tags=tags or set(),
        )
        
        cls._reports[report_id] = registration
        return registration
    
    @classmethod
    def get(cls, report_id: str) -> Optional[ReportRegistration]:
        """Get report registration."""
        return cls._reports.get(report_id)
    
    @classmethod
    def deprecate(
        cls,
        report_id: str,
        replacement: Optional[str] = None,
    ) -> None:
        """Deprecate a report."""
        if report_id not in cls._reports:
            raise ValueError(f"Report not registered: {report_id}")
        
        cls._reports[report_id].deprecate(replacement)
    
    @classmethod
    def list_active(cls) -> List[ReportRegistration]:
        """List all active reports."""
        return [
            reg for reg in cls._reports.values()
            if reg.status == DeprecationStatus.ACTIVE
        ]
    
    @classmethod
    def find_by_type(cls, report_type: str) -> List[ReportRegistration]:
        """Find reports by type."""
        return [
            reg for reg in cls._reports.values()
            if reg.report_type == report_type
        ]
    
    @classmethod
    def find_by_template(cls, template_id: str) -> List[ReportRegistration]:
        """Find reports using a specific template."""
        return [
            reg for reg in cls._reports.values()
            if reg.template_id == template_id
        ]


# Register built-in templates
def register_builtin_templates():
    """Register built-in templates."""
    
    # DRE Template
    dre_reg = TemplateRegistry.register(
        template_id="dre_v2026_1",
        template_type="DRE",
        version="2026.1",
        tags={"financial", "income_statement", "builtin"},
    )
    
    dre_reg.add_changelog(
        ChangeLogEntry(
            version="2026.1",
            date="2026-02-20",
            changes=[
                "Initial production release",
                "Added section-based layout",
                "Added conditional formatting for negatives",
                "Added percentage of revenue column",
            ],
            breaking_changes=[],
            author="SpreadsheetEngine",
        )
    )
    
    # Register DRE Report
    ReportRegistry.register(
        report_id="dre_report_v2026_1",
        report_type="DRE",
        template_id="dre_reg",
        version="2026.1",
        tags={"financial", "builtin"},
    )


# Auto-register on import
register_builtin_templates()
