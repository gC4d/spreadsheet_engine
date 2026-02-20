"""
DRE (Income Statement) Report - Production implementation.

This demonstrates the simplified public API with domain mapping.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from ...core.models.position import CellPosition
from ...core.report import Report, ReportMapper, ReportMetadata
from ...core.styles.cell_style import (
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
from ...core.styles.conditional import ConditionalRule
from ...core.styles.number_format import NumberFormat
from ...core.templates.data import SheetData, SpreadsheetData, TableData
from ...core.templates.template import (
    ColumnDefinition,
    SectionDefinition,
    SheetTemplate,
    SpreadsheetTemplate,
    TableTemplate,
)


# Version constant
DRE_TEMPLATE_VERSION = "2026.1"


@dataclass
class DRELineItem:
    """Domain model for a DRE line item."""
    
    account: str
    value: float
    percent: float = 0.0


@dataclass
class DREData:
    """Domain model for DRE data."""
    
    period: str
    revenue_items: List[DRELineItem]
    cost_items: List[DRELineItem]
    expense_items: List[DRELineItem]
    financial_items: List[DRELineItem]
    tax_items: List[DRELineItem]
    
    title: str = "DEMONSTRAÇÃO DO RESULTADO DO EXERCÍCIO"


class DREMapper(ReportMapper):
    """Maps DRE domain model to spreadsheet data."""
    
    def map(self, domain_model: DREData) -> SpreadsheetData:
        """
        Map DRE domain data to spreadsheet format.
        
        Args:
            domain_model: DRE domain data
            
        Returns:
            SpreadsheetData ready for rendering
        """
        # Convert line items to dict format
        def items_to_dicts(items: List[DRELineItem]) -> List[Dict[str, Any]]:
            return [
                {
                    "account": item.account,
                    "value": item.value,
                    "percent": item.percent,
                }
                for item in items
            ]
        
        # Create table data with sections
        table_data = TableData()
        table_data.add_section_data("revenue", items_to_dicts(domain_model.revenue_items))
        table_data.add_section_data("costs", items_to_dicts(domain_model.cost_items))
        table_data.add_section_data("expenses", items_to_dicts(domain_model.expense_items))
        table_data.add_section_data("financial", items_to_dicts(domain_model.financial_items))
        table_data.add_section_data("taxes", items_to_dicts(domain_model.tax_items))
        
        # Create sheet data
        sheet_data = SheetData()
        sheet_data.add_table_data("dre", table_data)
        
        # Create spreadsheet data
        spreadsheet_data = SpreadsheetData()
        spreadsheet_data.add_sheet_data("DRE", sheet_data)
        
        # Add metadata
        spreadsheet_data.metadata["period"] = domain_model.period
        spreadsheet_data.metadata["title"] = domain_model.title
        
        return spreadsheet_data


class DREReport(Report):
    """
    DRE (Income Statement) Report.
    
    Simplified public API - users never see templates or renderers.
    
    Usage:
        dre_data = DREData(
            period="Janeiro/2024",
            revenue_items=[...],
            cost_items=[...],
            ...
        )
        
        report = DREReport.from_domain(dre_data)
        report.export("dre.xlsx")
    """
    
    def __init__(self, data: SpreadsheetData, period: str, title: str):
        """
        Initialize DRE report.
        
        Args:
            data: Spreadsheet data
            period: Report period
            title: Report title
        """
        metadata = ReportMetadata(
            report_type="DRE",
            version=DRE_TEMPLATE_VERSION,
            template_version=DRE_TEMPLATE_VERSION,
            description=f"Demonstração do Resultado do Exercício - {period}",
            tags={"period": period, "report_family": "financial"},
        )
        
        super().__init__(data, metadata)
        self._period = period
        self._title = title
    
    @classmethod
    def from_domain(cls, domain_model: DREData, **kwargs) -> DREReport:
        """
        Create DRE report from domain model.
        
        Args:
            domain_model: DRE domain data
            **kwargs: Additional options
            
        Returns:
            DREReport instance
        """
        mapper = DREMapper()
        data = mapper.map(domain_model)
        
        return cls(
            data=data,
            period=domain_model.period,
            title=domain_model.title,
        )
    
    def _create_template(self) -> SpreadsheetTemplate:
        """Create DRE template."""
        # Styles
        title_style = CellStyle(
            font=Font(bold=True, size=14, color=Color("2F5496")),
            alignment=Alignment(horizontal=HorizontalAlignment.CENTER),
        )
        
        header_style = CellStyle(
            font=Font(bold=True, size=11, color=Color("FFFFFF")),
            fill=Fill(
                pattern=PatternFill.SOLID,
                foreground_color=Color("4472C4"),
            ),
            alignment=Alignment(horizontal=HorizontalAlignment.CENTER),
            border=Border.all_sides(BorderStyle.THIN),
        )
        
        section_style = CellStyle(
            font=Font(bold=True, size=11, color=Color("2F5496")),
            fill=Fill(
                pattern=PatternFill.SOLID,
                foreground_color=Color("E7E6E6"),
            ),
            border=Border.all_sides(BorderStyle.THIN),
        )
        
        total_style = CellStyle(
            font=Font(bold=True, size=11),
            fill=Fill(
                pattern=PatternFill.SOLID,
                foreground_color=Color("D9E1F2"),
            ),
            border=Border.all_sides(BorderStyle.MEDIUM),
        )
        
        # Columns
        columns = [
            ColumnDefinition(
                key="account",
                label="Conta",
                width=40,
                header_style=header_style,
            ),
            ColumnDefinition(
                key="value",
                label="Valor (R$)",
                width=18,
                number_format=NumberFormat.CURRENCY_BRL.value,
                header_style=header_style,
                style=CellStyle(
                    alignment=Alignment(horizontal=HorizontalAlignment.RIGHT)
                ),
            ),
            ColumnDefinition(
                key="percent",
                label="% Receita",
                width=15,
                number_format=NumberFormat.PERCENTAGE_2.value,
                header_style=header_style,
                style=CellStyle(
                    alignment=Alignment(horizontal=HorizontalAlignment.RIGHT)
                ),
            ),
        ]
        
        # Sections
        sections = [
            SectionDefinition(
                key="revenue",
                label="RECEITA BRUTA",
                style=section_style,
            ),
            SectionDefinition(
                key="costs",
                label="(-) CUSTOS",
                style=section_style,
            ),
            SectionDefinition(
                key="gross_profit",
                label="= LUCRO BRUTO",
                style=total_style,
                is_total=True,
            ),
            SectionDefinition(
                key="expenses",
                label="(-) DESPESAS OPERACIONAIS",
                style=section_style,
            ),
            SectionDefinition(
                key="operating_profit",
                label="= LUCRO OPERACIONAL",
                style=total_style,
                is_total=True,
            ),
            SectionDefinition(
                key="financial",
                label="RESULTADO FINANCEIRO",
                style=section_style,
            ),
            SectionDefinition(
                key="ebt",
                label="= LUCRO ANTES DOS IMPOSTOS",
                style=total_style,
                is_total=True,
            ),
            SectionDefinition(
                key="taxes",
                label="(-) IMPOSTOS",
                style=section_style,
            ),
            SectionDefinition(
                key="net_profit",
                label="= LUCRO LÍQUIDO",
                style=total_style,
                is_total=True,
            ),
        ]
        
        # Conditional formatting
        negative_rule = ConditionalRule.cell_is_negative(
            style=CellStyle(
                font=Font(color=Color("FF0000")),
            )
        )
        
        # Table template
        table_template = TableTemplate(
            name="dre",
            columns=columns,
            sections=sections,
            title=self._title,
            title_style=title_style,
            header_style=header_style,
            conditional_rules=[negative_rule],
            start_position=CellPosition(1, 1),
            freeze_headers=True,
        )
        
        # Sheet template
        sheet_template = SheetTemplate(
            name="DRE",
            tables=[table_template],
            freeze_panes=CellPosition(3, 1),
        )
        
        # Spreadsheet template
        template = SpreadsheetTemplate(
            sheets=[sheet_template],
            metadata={
                "report_type": "DRE",
                "template_version": DRE_TEMPLATE_VERSION,
            },
        )
        
        return template
    
    def _get_metadata(self) -> ReportMetadata:
        """Get report metadata."""
        return self._metadata


# Helper function for backward compatibility
def create_dre_report(
    period: str,
    revenue_items: List[Dict[str, Any]],
    cost_items: List[Dict[str, Any]],
    expense_items: List[Dict[str, Any]],
    financial_items: List[Dict[str, Any]],
    tax_items: List[Dict[str, Any]],
    title: str = "DEMONSTRAÇÃO DO RESULTADO DO EXERCÍCIO",
) -> DREReport:
    """
    Create DRE report from raw data.
    
    Args:
        period: Report period
        revenue_items: Revenue line items
        cost_items: Cost line items
        expense_items: Expense line items
        financial_items: Financial result line items
        tax_items: Tax line items
        title: Report title
        
    Returns:
        DREReport instance
    """
    def to_line_items(items: List[Dict[str, Any]]) -> List[DRELineItem]:
        return [
            DRELineItem(
                account=item["account"],
                value=item["value"],
                percent=item.get("percent", 0.0),
            )
            for item in items
        ]
    
    dre_data = DREData(
        period=period,
        revenue_items=to_line_items(revenue_items),
        cost_items=to_line_items(cost_items),
        expense_items=to_line_items(expense_items),
        financial_items=to_line_items(financial_items),
        tax_items=to_line_items(tax_items),
        title=title,
    )
    
    return DREReport.from_domain(dre_data)
