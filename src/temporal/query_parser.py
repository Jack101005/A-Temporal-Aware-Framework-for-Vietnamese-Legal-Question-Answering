"""
query_parser.py
===============
Figures out WHICH DATE a user's question is about.

This is the first step of the temporal pipeline. It reads the question and
returns a query_date. If the user mentions a year/date, we use it; otherwise
we default to today.
"""

import re
from datetime import date


def parse_query_date(question: str) -> date:
    """Detect a date in the question; fall back to today().

    Handles simple cases:
      - explicit year:  "năm 2020", "in 2022", "2019"
      - full date:      "01/07/2024", "1/7/2024"
      - "current/hiện tại/now" -> today
    """
    # Full date dd/mm/yyyy
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", question)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return date(y, mo, d)
        except ValueError:
            pass

    # A 4-digit year between 1990 and 2099
    m = re.search(r"\b(19[9]\d|20\d{2})\b", question)
    if m:
        return date(int(m.group(1)), 1, 1)

    # Default: today (covers "current", "hiện tại", or no date at all)
    return date.today()
