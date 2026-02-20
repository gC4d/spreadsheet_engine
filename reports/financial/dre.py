"""DRE (Demonstração do Resultado do Exercício) - Income Statement template."""

from __future__ import annotations

from typing import List, Dict, Any

from ...core.models.position import CellPosition
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


class DRETemplate:
    """
    DRE (Income Statement) template builder.

    Provides a complete, professional DRE layout with:
    - Revenue sections
    - Cost and expense sections
    - Automatic totals via formulas
    - Percentage calculations
    - Conditional formatting for negative values
    - Professional styling
    """

    @staticmethod
    def create_template(
        title: str = "DEMONSTRAÇÃO DO RESULTADO DO EXERCÍCIO",
        period: str = "Período: 2024",
    ) -> SpreadsheetTemplate:
        """
        Create DRE template.

        Args:
            title: Report title
            period: Period description

        Returns:
            SpreadsheetTemplate for DRE
        """
        header_style = CellStyle(
            font=Font(bold=True, size=11, color=Color("FFFFFF")),
            fill=Fill(
                pattern=PatternFill.SOLID,
                foreground_color=Color("4472C4"),
            ),
            alignment=Alignment(
                horizontal=HorizontalAlignment.CENTER,
                vertical=VerticalAlignment.CENTER,
            ),
            border=Border.all_sides(BorderStyle.THIN),
        )

        title_style = CellStyle(
            font=Font(bold=True, size=14),
            alignment=Alignment(
                horizontal=HorizontalAlignment.CENTER,
                vertical=VerticalAlignment.CENTER,
            ),
        )

        section_style = CellStyle(
            font=Font(bold=True, size=11, color=Color("FFFFFF")),
            fill=Fill(
                pattern=PatternFill.SOLID,
                foreground_color=Color("70AD47"),
            ),
            alignment=Alignment(
                horizontal=HorizontalAlignment.LEFT,
                vertical=VerticalAlignment.CENTER,
            ),
            border=Border.all_sides(BorderStyle.THIN),
        )

        total_style = CellStyle(
            font=Font(bold=True, size=11),
            fill=Fill(
                pattern=PatternFill.SOLID,
                foreground_color=Color("D9E1F2"),
            ),
            alignment=Alignment(
                horizontal=HorizontalAlignment.LEFT,
                vertical=VerticalAlignment.CENTER,
            ),
            border=Border.all_sides(BorderStyle.MEDIUM),
        )

        negative_style = CellStyle(
            font=Font(color=Color("FF0000")),
        )

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
                width=20,
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

        sections = [
            SectionDefinition(
                key="gross_revenue",
                label="RECEITA BRUTA",
                style=section_style,
            ),
            SectionDefinition(
                key="deductions",
                label="(-) DEDUÇÕES DA RECEITA",
                style=section_style,
            ),
            SectionDefinition(
                key="net_revenue",
                label="= RECEITA LÍQUIDA",
                style=total_style,
                is_total=True,
            ),
            SectionDefinition(
                key="cost_of_sales",
                label="(-) CUSTO DAS VENDAS",
                style=section_style,
            ),
            SectionDefinition(
                key="gross_profit",
                label="= LUCRO BRUTO",
                style=total_style,
                is_total=True,
            ),
            SectionDefinition(
                key="operating_expenses",
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
                key="financial_result",
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
                label="(-) IMPOSTOS SOBRE LUCRO",
                style=section_style,
            ),
            SectionDefinition(
                key="net_profit",
                label="= LUCRO LÍQUIDO",
                style=total_style,
                is_total=True,
            ),
        ]

        conditional_rules = [
            ConditionalRule.cell_is_negative(negative_style, priority=1),
        ]

        table = TableTemplate(
            name="dre",
            columns=columns,
            sections=sections,
            title=f"{title}\n{period}",
            title_style=title_style,
            header_style=header_style,
            conditional_rules=conditional_rules,
            start_position=CellPosition(1, 1),
            freeze_headers=True,
        )

        sheet = SheetTemplate(
            name="DRE",
            tables=[table],
            freeze_panes=CellPosition(4, 1),
        )

        return SpreadsheetTemplate(sheets=[sheet])

    @staticmethod
    def create_sample_data() -> SpreadsheetData:
        """
        Create sample DRE data for testing.

        Returns:
            SpreadsheetData with sample financial data
        """
        data = {
            "gross_revenue": [
                {"account": "Vendas de Produtos", "value": 1000000, "percent": 1.0},
                {"account": "Vendas de Serviços", "value": 500000, "percent": 0.5},
            ],
            "deductions": [
                {"account": "Impostos sobre Vendas", "value": -150000, "percent": -0.15},
                {"account": "Devoluções", "value": -50000, "percent": -0.05},
            ],
            "net_revenue": [
                {"account": "Receita Líquida", "value": 1300000, "percent": 1.0},
            ],
            "cost_of_sales": [
                {"account": "Custo dos Produtos Vendidos", "value": -600000, "percent": -0.46},
                {"account": "Custo dos Serviços", "value": -200000, "percent": -0.15},
            ],
            "gross_profit": [
                {"account": "Lucro Bruto", "value": 500000, "percent": 0.38},
            ],
            "operating_expenses": [
                {"account": "Despesas Administrativas", "value": -150000, "percent": -0.12},
                {"account": "Despesas Comerciais", "value": -100000, "percent": -0.08},
                {"account": "Despesas com Pessoal", "value": -80000, "percent": -0.06},
            ],
            "operating_profit": [
                {"account": "Lucro Operacional", "value": 170000, "percent": 0.13},
            ],
            "financial_result": [
                {"account": "Receitas Financeiras", "value": 20000, "percent": 0.02},
                {"account": "Despesas Financeiras", "value": -30000, "percent": -0.02},
            ],
            "ebt": [
                {"account": "Lucro Antes dos Impostos", "value": 160000, "percent": 0.12},
            ],
            "taxes": [
                {"account": "IR e CSLL", "value": -54400, "percent": -0.04},
            ],
            "net_profit": [
                {"account": "Lucro Líquido", "value": 105600, "percent": 0.08},
            ],
        }

        table_data = TableData()
        for section_key, rows in data.items():
            table_data.add_section_data(section_key, rows)

        sheet_data = SheetData()
        sheet_data.add_table_data("dre", table_data)

        spreadsheet_data = SpreadsheetData()
        spreadsheet_data.add_sheet_data("DRE", sheet_data)

        return spreadsheet_data

    @staticmethod
    def generate_sample_report(output_path: str) -> None:
        """
        Generate a sample DRE report.

        Args:
            output_path: Path to save the report
        """
        from ...engine.renderer import SpreadsheetRenderer

        template = DRETemplate.create_template()
        data = DRETemplate.create_sample_data()

        renderer = SpreadsheetRenderer()
        renderer.render(template, data, output=output_path)


def create_dre_from_data(
    revenue_items: List[Dict[str, Any]],
    cost_items: List[Dict[str, Any]],
    expense_items: List[Dict[str, Any]],
    financial_items: List[Dict[str, Any]],
    tax_items: List[Dict[str, Any]],
    period: str = "2024",
) -> SpreadsheetData:
    """
    Create DRE data from structured financial data.

    Args:
        revenue_items: Revenue line items
        cost_items: Cost line items
        expense_items: Operating expense items
        financial_items: Financial result items
        tax_items: Tax items
        period: Period description

    Returns:
        SpreadsheetData ready for rendering
    """
    gross_revenue_total = sum(item["value"] for item in revenue_items)

    def calc_percent(value: float) -> float:
        if gross_revenue_total == 0:
            return 0.0
        return value / gross_revenue_total

    for item in revenue_items:
        item["percent"] = calc_percent(item["value"])

    for item in cost_items:
        item["percent"] = calc_percent(item["value"])

    for item in expense_items:
        item["percent"] = calc_percent(item["value"])

    for item in financial_items:
        item["percent"] = calc_percent(item["value"])

    for item in tax_items:
        item["percent"] = calc_percent(item["value"])

    table_data = TableData()
    table_data.add_section_data("gross_revenue", revenue_items)
    table_data.add_section_data("cost_of_sales", cost_items)
    table_data.add_section_data("operating_expenses", expense_items)
    table_data.add_section_data("financial_result", financial_items)
    table_data.add_section_data("taxes", tax_items)

    sheet_data = SheetData()
    sheet_data.add_table_data("dre", table_data)

    spreadsheet_data = SpreadsheetData()
    spreadsheet_data.add_sheet_data("DRE", sheet_data)

    return spreadsheet_data
