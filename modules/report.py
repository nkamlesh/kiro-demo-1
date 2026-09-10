"""HTML report builder using a Jinja2 template.

Produces a single self-contained HTML file with charts embedded as base64
PNGs, so it renders standalone without a server.
"""
from __future__ import annotations

import datetime as _dt
import os
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader, select_autoescape

_TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")


def build_html_report(
    filename: str,
    sheet_name: str,
    profiles: List[Dict],
    quality: Dict,
    recommendations: List[Dict],
    charts: List[Dict],
    insights: List[str],
) -> str:
    """Render the full HTML report and return it as a string."""
    env = Environment(
        loader=FileSystemLoader(_TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("report_template.html")
    return template.render(
        filename=filename,
        sheet_name=sheet_name,
        generated_at=_dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        profiles=profiles,
        quality=quality,
        recommendations=recommendations,
        charts=charts,
        insights=insights,
    )
