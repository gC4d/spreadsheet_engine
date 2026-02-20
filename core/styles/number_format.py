"""Number formatting system."""

from enum import Enum


class NumberFormat(str, Enum):
    """
    Standard number formats for spreadsheet cells.

    These are format-agnostic definitions that adapters translate
    to format-specific format strings.
    """

    GENERAL = "General"
    INTEGER = "0"
    DECIMAL_1 = "0.0"
    DECIMAL_2 = "0.00"
    DECIMAL_3 = "0.000"
    DECIMAL_4 = "0.0000"
    THOUSANDS = "#,##0"
    THOUSANDS_DECIMAL_2 = "#,##0.00"
    CURRENCY_BRL = 'R$ #,##0.00'
    CURRENCY_BRL_NEGATIVE = 'R$ #,##0.00_);[Red](R$ #,##0.00)'
    CURRENCY_USD = '$#,##0.00'
    CURRENCY_EUR = '€#,##0.00'
    ACCOUNTING_BRL = '_-R$ * #,##0.00_-;-R$ * #,##0.00_-;_-R$ * "-"??_-;_-@_-'
    ACCOUNTING_USD = '_-$* #,##0.00_-;-$* #,##0.00_-;_-$* "-"??_-;_-@_-'
    PERCENTAGE = "0%"
    PERCENTAGE_1 = "0.0%"
    PERCENTAGE_2 = "0.00%"
    DATE_ISO = "YYYY-MM-DD"
    DATE_BR = "DD/MM/YYYY"
    DATE_US = "MM/DD/YYYY"
    DATE_LONG_BR = "DD [de] MMMM [de] YYYY"
    DATETIME_BR = "DD/MM/YYYY HH:MM:SS"
    DATETIME_ISO = "YYYY-MM-DD HH:MM:SS"
    TIME = "HH:MM:SS"
    TIME_SHORT = "HH:MM"
    SCIENTIFIC = "0.00E+00"
    FRACTION = "# ?/?"
    TEXT = "@"

    @classmethod
    def currency(cls, currency_code: str = "BRL") -> str:
        """
        Get currency format for specific currency.

        Args:
            currency_code: ISO currency code (BRL, USD, EUR, etc.)

        Returns:
            Format string for the currency
        """
        currency_formats = {
            "BRL": cls.CURRENCY_BRL.value,
            "USD": cls.CURRENCY_USD.value,
            "EUR": cls.CURRENCY_EUR.value,
        }
        return currency_formats.get(currency_code.upper(), cls.CURRENCY_BRL.value)

    @classmethod
    def accounting(cls, currency_code: str = "BRL") -> str:
        """
        Get accounting format for specific currency.

        Args:
            currency_code: ISO currency code (BRL, USD, EUR, etc.)

        Returns:
            Accounting format string for the currency
        """
        accounting_formats = {
            "BRL": cls.ACCOUNTING_BRL.value,
            "USD": cls.ACCOUNTING_USD.value,
        }
        return accounting_formats.get(currency_code.upper(), cls.ACCOUNTING_BRL.value)
