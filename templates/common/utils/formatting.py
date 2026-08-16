"""Display formatting.

Server-side helpers for values that are formatted *before* they reach a state
var. Anything formatted here becomes a plain string in state, which keeps the
frontend free of formatting logic.

Note: these operate on Python values, not Reflex Vars. To format inside a
component, use a computed var on the state instead.
"""

from datetime import date, datetime
from decimal import Decimal

_UNITS = ("B", "KB", "MB", "GB", "TB", "PB")


def format_date(value: date | datetime | None, fmt: str = "%Y-%m-%d") -> str:
    """Format a date, with empty string for None (never the text 'None')."""
    if value is None:
        return ""
    return value.strftime(fmt)


def format_datetime(value: datetime | None, fmt: str = "%Y-%m-%d %H:%M") -> str:
    if value is None:
        return ""
    return value.strftime(fmt)


def format_currency(
    value: Decimal | float | None,
    symbol: str = "€",
    decimals: int = 2,
) -> str:
    """Format a monetary amount, e.g. ``1234.5 -> '1,234.50 €'``."""
    if value is None:
        return ""
    # U+00A0 keeps the amount and its symbol on one line.
    return f"{value:,.{decimals}f}\u00a0{symbol}"


def truncate(text: str, length: int = 60, suffix: str = "…") -> str:
    """Shorten text to ``length`` characters, including the suffix."""
    if len(text) <= length:
        return text
    return text[: max(0, length - len(suffix))].rstrip() + suffix


def humanize_bytes(size: int | float, decimals: int = 1) -> str:
    """Render a byte count as ``'1.5 MB'``."""
    value = float(size)
    for unit in _UNITS:
        if abs(value) < 1024.0 or unit == _UNITS[-1]:
            precision = 0 if unit == "B" else decimals
            return f"{value:.{precision}f} {unit}"
        value /= 1024.0
    return f"{value:.{decimals}f} {_UNITS[-1]}"
