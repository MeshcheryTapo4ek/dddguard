from typing import Final

# CSS Styles for Architecture Legend
LEGEND_CSS_H2: Final[str] = (
    "margin-top:0; color: #2C3E50; font-size: 16px; border-bottom: 2px solid #BDC3C7; padding-bottom: 5px;"
)
LEGEND_CSS_H3: Final[str] = (
    "margin-top: 10px; margin-bottom: 5px; color: #34495E; font-size: 14px; font-weight: bold;"
)
LEGEND_CSS_TXT: Final[str] = (
    "font-family: Helvetica; color: #333; font-size: 11px; line-height: 1.4;"
)
LEGEND_CSS_NOTE: Final[str] = (
    "background-color: #f4f6f7; padding: 5px; border-left: 3px solid #3498DB; font-style: italic; margin: 4px 0;"
)
LEGEND_CSS_UL: Final[str] = "margin-top: 2px; margin-bottom: 5px; padding-left: 15px;"
LEGEND_CSS_LI: Final[str] = "margin-bottom: 2px;"
LEGEND_CSS_SUB_H: Final[str] = (
    "font-size: 12px; font-weight: bold; margin-top: 4px; margin-bottom: 2px;"
)

# HTML Fragments
LEGEND_HTML_HEADER: Final[str] = f'<h2 style="{LEGEND_CSS_H2}">🗺️ System Architecture Map</h2>'

LEGEND_HTML_VISUAL_GUIDE: Final[str] = f"""
<h3 style="{LEGEND_CSS_H3}">🎨 Visual Guide</h3>
<ul style="{LEGEND_CSS_UL}">
  <li><b>Arrows (Imports):</b> <code>A ➜ B</code> means A imports B.</li>
  <li><b>Coloring:</b> <span style="color:#E67E22; font-weight:bold;">Source-Based.</span> All arrows from the same Node share a specific Hue.</li>
  <li><b>Wiring:</b> The <code>composition.py</code> module is the local assembler.</li>
</ul>
"""

LEGEND_HTML_LAYER_ANATOMY_HEADER: Final[str] = f'<h3 style="{LEGEND_CSS_H3}">🏗️ Layer Anatomy</h3>'

LEGEND_HTML_NOTE: Final[str] = f"""
<div style="{LEGEND_CSS_NOTE}">
  ⚠️ <b>Note:</b> Arrows originating from <b>Error</b> objects are hidden to reduce noise.
</div>
"""
