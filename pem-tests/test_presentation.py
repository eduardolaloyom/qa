"""Integration tests for the Metricas Operativas presentation layer.

Tests verify:
- Tab navigation: metrics tab appears, page div exists, client pages shifted
- KPI cards: RAG coloring via CSS variables, Sin datos display, section titles
- Charts: canvas elements with correct IDs
- Theme support: no hardcoded colors in cards, CDN plugins loaded

These tests generate the full dashboard HTML via generate_html() with mock KPI data
and assert on the resulting HTML string.
"""
import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from generate_dashboard import generate_html

# ── Fixtures ──

FIXTURE_PATH = os.path.join(
    os.path.dirname(__file__), "fixtures", "kpis_sample.json"
)
with open(FIXTURE_PATH, "r", encoding="utf-8") as _f:
    KPI_DATA = json.load(_f)

# Minimal records for 3 clients (reuses pattern from test_generator_integration.py)
MINIMAL_RECORDS = [
    {
        "PageId": "page-001",
        "Tarea": "Task A1",
        "Tipo": "Tarea",
        "Cliente": "ClienteA",
        "Estado": "Completado",
        "Fase": "1. Levantamiento",
        "FechaInicio": "2025-01-01",
        "FechaTermino": "2025-01-15",
        "FechaFinalizacion": "2025-01-20",
        "Bloqueado": "",
        "Notas": "",
        "Responsables": [],
        "Relacion": [],
    },
    {
        "PageId": "page-002",
        "Tarea": "Task B1",
        "Tipo": "Tarea",
        "Cliente": "ClienteB",
        "Estado": "En progreso",
        "Fase": "4. Integracion",
        "FechaInicio": "2025-02-01",
        "FechaTermino": "2025-02-28",
        "FechaFinalizacion": "",
        "Bloqueado": "",
        "Notas": "",
        "Responsables": [],
        "Relacion": [],
    },
    {
        "PageId": "page-003",
        "Tarea": "Task C1",
        "Tipo": "Tarea",
        "Cliente": "ClienteC",
        "Estado": "Pendiente",
        "Fase": "1. Levantamiento",
        "FechaInicio": "2025-03-01",
        "FechaTermino": "2025-03-15",
        "FechaFinalizacion": "",
        "Bloqueado": "",
        "Notas": "",
        "Responsables": [],
        "Relacion": [],
    },
]

NOW_STR = "2025-01-01T00:00:00Z"

# Generate HTML once -- all tests share this
HTML = generate_html(MINIMAL_RECORDS, NOW_STR, KPI_DATA)


class TestTabNavigation:
    """Tests for metrics tab integration into the navigation bar."""

    def test_metrics_tab_in_nav(self):
        """Generated HTML contains the 'Metricas Operativas' tab button text."""
        assert "Metricas Operativas" in HTML

    def test_metrics_page_div_exists(self):
        """Generated HTML contains the metrics page div with id='page-5'."""
        assert 'id="page-5"' in HTML

    def test_client_pages_shifted(self):
        """Client detail pages use page-${i+6} template pattern (shifted from +5 to +6).
        Since JS template literals are not evaluated in the template string,
        we check for the i+6 pattern and the absence of i+5."""
        assert "i+6" in HTML, "Expected client pages to use i+6 pattern"
        assert "i+5" not in HTML, "Stale i+5 page index reference found"

    def test_showpage_references_shifted(self):
        """No showPage(N+5) references remain for client detail navigation;
        they all use +6. Nav pages 0-4 should exist, and client onclick values
        start at 6+."""
        # The template generates onclick="showPage(X)" for each client in the
        # ranking table and clients grid. After the shift, the first client
        # should use showPage(6), not showPage(5).
        # Check that page-5 onclick is NOT used for client navigation.
        # The string `showPage(5)` should exist only for the Metricas Operativas
        # tab in the nav bar, not in onclick attributes of client rows/cards.
        # Look for client row pattern: onclick="showPage(5)" should not appear
        # in <tr> or <div class="card"> contexts.
        client_row_pattern = re.compile(
            r'<tr[^>]*onclick="showPage\(5\)"'
        )
        assert not client_row_pattern.search(HTML), (
            "Found client row still using showPage(5) instead of showPage(6+)"
        )
        # Client card pattern
        client_card_pattern = re.compile(
            r'<div class="card"[^>]*onclick="showPage\(5\)"'
        )
        assert not client_card_pattern.search(HTML), (
            "Found client card still using showPage(5) instead of showPage(6+)"
        )


class TestKpiCards:
    """Tests for KPI card rendering with RAG coloring."""

    def test_rag_color_css_vars(self):
        """Generated HTML uses var(--green), var(--orange), var(--red) for KPI values."""
        assert "var(--green)" in HTML
        assert "var(--orange)" in HTML or "var(--red)" in HTML

    def test_sin_datos_display(self):
        """Generated HTML contains 'Sin datos' for KPIs with null values."""
        assert "Sin datos" in HTML

    def test_section_titles(self):
        """Generated HTML contains both KPI section titles."""
        assert "KPIs de Fechas" in HTML
        assert "KPIs de Historial" in HTML


class TestCharts:
    """Tests for Chart.js canvas elements in the metrics page."""

    def test_chart_canvas_elements(self):
        """Generated HTML contains canvas elements with IDs starting with 'chart-metrics-'."""
        assert "chart-metrics-" in HTML


class TestThemeSupport:
    """Tests for theme support and CDN plugin loading."""

    def test_no_hardcoded_colors_in_cards(self):
        """Card inline styles in the metrics page use only var(--xxx) references,
        not hex color literals."""
        # Extract the metrics page content (between page-5 div markers)
        page5_match = re.search(
            r'id="page-5">(.*?)(?=<div class="page"|$)',
            HTML,
            re.DOTALL,
        )
        assert page5_match is not None, "Could not find page-5 content"
        page5_content = page5_match.group(1)

        # Find all inline color: values in the metrics page
        # Hex colors look like #xxx or #xxxxxx
        color_values = re.findall(r'color:\s*(#[0-9a-fA-F]{3,6})', page5_content)
        assert len(color_values) == 0, (
            f"Found hardcoded hex colors in metrics page cards: {color_values}"
        )

    def test_cdn_scripts_present(self):
        """Generated HTML contains chartjs-plugin-annotation and chartjs-plugin-datalabels CDN script tags."""
        assert "chartjs-plugin-annotation" in HTML
        assert "chartjs-plugin-datalabels" in HTML
