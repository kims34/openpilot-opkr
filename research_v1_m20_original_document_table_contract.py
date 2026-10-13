"""Offline M20 first-filed document row-shape audit; never expose amounts.

This is NOT financial-statement, PIT, or performance admission. Callers must
validate official original ZIP, first submission, CRC and entry bounds first.
"""
from html.parser import HTMLParser
import re

OPERATING_PROFIT_LABELS = frozenset(("영업이익", "영업이익(손실)", "영업손익", "영업손실"))
NUMBER = re.compile(r"^\\(?-?(?:\\d{1,3}(?:,\\d{3})+|\\d+)(?:\\.\\d+)?\\)?$")


def compact(value):
    return re.sub(r"\\s+", "", value).replace("（", "(").replace("）", ")")


class RowShape(HTMLParser):
    """Collect only aggregate structural counts; never retain rows after scan."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables = 0
        self.rows = 0
        self.profit_rows = 0
        self.profit_rows_with_number = 0
        self._row = None
        self._cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.tables += 1
        elif tag == "tr":
            self._finish_row()
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._finish_cell()
            if len(self._row) >= 64:
                raise ValueError("ROW_TOO_WIDE")
            self._cell = ""

    def handle_data(self, data):
        if self._cell is not None:
            if len(self._cell) + len(data) > 512:
                raise ValueError("CELL_TOO_LONG")
            self._cell += data

    def handle_endtag(self, tag):
        if tag in ("td", "th"):
            self._finish_cell()
        elif tag == "tr":
            self._finish_row()

    def _finish_cell(self):
        if self._cell is not None:
            self._row.append(compact(self._cell))
            self._cell = None

    def _finish_row(self):
        if self._row is None:
            return
        self._finish_cell()
        self.rows += 1
        if self.rows > 120000:
            raise ValueError("ROW_LIMIT")
        if any(x in OPERATING_PROFIT_LABELS for x in self._row):
            self.profit_rows += 1
            if any(NUMBER.fullmatch(x) for x in self._row):
                self.profit_rows_with_number += 1
        self._row = None

    def result(self):
        self._finish_row()
        return {
            "table_count": self.tables,
            "row_count": self.rows,
            "operating_profit_label_rows": self.profit_rows,
            "operating_profit_rows_with_numeric_sibling": self.profit_rows_with_number,
            "original_cfs_quarter_value_verified": False,
            "historical_pit_verified": False,
            "m20_performance_run_authorized": False,
            "independent_holdout_authorized": False,
            "real_orders_authorized": False,
            "ordering": "DISABLED",
        }


def scan_original_document_text(markup):
    if not isinstance(markup, str) or len(markup) > 32 * 1024 * 1024:
        raise ValueError("MARKUP_INVALID")
    parser = RowShape()
    parser.feed(markup)
    parser.close()
    return parser.result()
