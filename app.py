"""
TRUE INGREDIENTS — Consumer Food Intelligence Platform (`app.py`)
===================================================================
A modern, consumer-facing application built on 5 backend phases of
cross-border ingredient intelligence and clean Indian D2C recommendations.

Phase 5C Final Micro-Polish Pass:
  - Neutral Model Difference Delta: 'Model difference: +42.0' (No health implication)
  - Muted Amber/Terracotta Formulation Signal Badges (#FDF6E9 bg, #9A6615 text, #EED4A2 border)
  - Widened Score Area (180px, nowrap) ensuring numbers like '82.0' stay on one line
  - Zero Emojis throughout entire platform for a polished editorial look
  - Flatter, unboxed visual hierarchy with horizontal impact bars and active score guide highlight
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import textwrap
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from src.ui_data_loader import IngredientDataLoader

# ── 1. Page Configuration (Clean Editorial Title, No Emojis) ─────────────────
st.set_page_config(
    page_title="TRUE INGREDIENTS — Food Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper function to render HTML cleanly without code-block escaping
def render_html(html_str: str):
    if hasattr(st, "html"):
        st.html(textwrap.dedent(html_str))
    else:
        st.markdown(textwrap.dedent(html_str), unsafe_allow_html=True)

# ── 2. Load Unified Backend Data ───────────────────────────────────────────
def load_data_manager():
    return IngredientDataLoader()

data_manager = load_data_manager()
all_products = data_manager.get_all_product_names()

# ── 3. Helper Functions for Presentation ───────────────────────────────────

def get_v2_v3_delta_html(v2_val: Optional[int], v3_val: float) -> str:
    """Generates comparative V2 -> V3 delta component with neutral model difference styling."""
    if v2_val is None:
        return f"""
        <div class="delta-box delta-neutral">
            <span>Previous model (v2): <b style="color:#78756E;">Not evaluated</b></span>
            <span style="color:#D6CEBF; margin:0 6px;">·</span>
            <span>True Ingredients (v3): <b style="color:#183B3A;">{v3_val:.1f}</b></span>
        </div>
        """
    
    delta = v3_val - float(v2_val)
    if delta > 0.001:
        delta_text = f"+{delta:.1f}"
    elif delta < -0.001:
        delta_text = f"{delta:.1f}"
    else:
        delta_text = "0.0"

    return f"""
    <div class="delta-box delta-neutral">
        <span>Previous model (v2): <b>{v2_val}</b></span>
        <span style="color:#D6CEBF; margin:0 6px;">→</span>
        <span>True Ingredients (v3): <b>{v3_val:.1f}</b></span>
        <span style="color:#D6CEBF; margin:0 6px;">·</span>
        <span>Model difference: <b style="color:#183B3A;">{delta_text}</b></span>
    </div>
    """

def get_why_this_score_bars_html(product: Dict[str, Any]) -> str:
    """Renders the flat, unboxed 'Why this score?' section with 4 horizontal impact bars."""
    if not product or not product.get("has_v3", False):
        return ""
    
    p_s = product.get("p_sugar", 0.0) or 0.0
    p_f = product.get("p_sat_fat", 0.0) or 0.0
    p_na = product.get("p_sodium", 0.0) or 0.0
    p_ing = product.get("p_ingredient", 0.0) or 0.0
    signals = product.get("detected_signals", [])

    # Horizontal Bar percentages (relative to individual caps)
    pct_s = min(100.0, (p_s / 25.0) * 100.0) if p_s > 0 else 0.0
    pct_f = min(100.0, (p_f / 15.0) * 100.0) if p_f > 0 else 0.0
    pct_na = min(100.0, (p_na / 15.0) * 100.0) if p_na > 0 else 0.0
    pct_ing = min(100.0, (p_ing / 25.0) * 100.0) if p_ing > 0 else 0.0

    # Clean signal tags with muted amber/terracotta styling
    if signals:
        sig_tags = "".join([f'<span class="signal-pill">{s.replace("_", " ").title()}</span>' for s in signals])
    else:
        sig_tags = '<span class="clean-pill">No high-risk additive signals detected</span>'

    return f"""
    <div class="ti-neutral-section">
        <div style="font-size: 1.2rem; font-weight: 800; color: #183B3A; margin-bottom: 4px;">Why this score?</div>
        <div style="font-size: 0.84rem; color: #66736D; margin-bottom: 18px;">Modeled point deductions across key macronutrient vectors and additive formulation signals</div>
        
        <div class="driver-bars-container">
            <!-- Sugar -->
            <div class="driver-row">
                <div class="driver-label">Sugar</div>
                <div class="driver-bar-track">
                    <div class="driver-bar-fill" style="width: {pct_s:.1f}%; background-color: #C96A4A;"></div>
                </div>
                <div class="driver-val">-{p_s:.2f} pts</div>
            </div>

            <!-- Saturated Fat -->
            <div class="driver-row">
                <div class="driver-label">Saturated fat</div>
                <div class="driver-bar-track">
                    <div class="driver-bar-fill" style="width: {pct_f:.1f}%; background-color: #D9A441;"></div>
                </div>
                <div class="driver-val">-{p_f:.2f} pts</div>
            </div>

            <!-- Sodium -->
            <div class="driver-row">
                <div class="driver-label">Sodium</div>
                <div class="driver-bar-track">
                    <div class="driver-bar-fill" style="width: {pct_na:.1f}%; background-color: #C58A2B;"></div>
                </div>
                <div class="driver-val">-{p_na:.2f} pts</div>
            </div>

            <!-- Formulation Signals -->
            <div class="driver-row">
                <div class="driver-label">Formulation signals</div>
                <div class="driver-bar-track">
                    <div class="driver-bar-fill" style="width: {pct_ing:.1f}%; background-color: #A84832;"></div>
                </div>
                <div class="driver-val">-{p_ing:.2f} pts</div>
            </div>
        </div>

        <div style="margin-top: 16px; padding-top: 14px; border-top: 1px solid #EDE5D8;">
            <div style="font-size: 0.78rem; font-weight: 800; color: #8C9690; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px;">
                Detected Formulation Signals:
            </div>
            <div>
                {sig_tags}
            </div>
        </div>
    </div>
    """

def get_score_guide_html(current_score: float) -> str:
    """Renders score guide with semantic color bands and dynamic 'YOU ARE HERE' highlight."""
    bands = [
        (80, 100, "Strong profile", "guide-strong", current_score >= 80, "#235431", "#E8F2EA"),
        (60, 79,  "Moderate profile", "guide-moderate", 60 <= current_score < 80, "#356840", "#F0F6EE"),
        (40, 59,  "Higher modeled burden", "guide-high-burden", 40 <= current_score < 60, "#9A6615", "#FDF6E9"),
        (0, 39,   "High modeled burden", "guide-severe", current_score < 40, "#98382C", "#FAF0EB"),
    ]

    items_html = ""
    for low, high, label, cls, is_active, text_color, bg_color in bands:
        if is_active:
            active_badge = '<span class="you-are-here-pill">YOU ARE HERE</span>'
            active_style = f"background-color: {bg_color}; border: 2px solid {text_color}; font-weight: 700;"
        else:
            active_badge = ""
            active_style = "background-color: #FFFDF8; border: 1px solid #EAE0D2; opacity: 0.75;"

        items_html += f"""
        <div class="guide-band-row" style="{active_style}">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-weight:800; color:{text_color}; font-size:0.88rem; min-width:55px;">{low}–{high}</span>
                <span style="color:#183B3A; font-size:0.84rem;">{label}</span>
            </div>
            {active_badge}
        </div>
        """

    return f"""
    <div class="ti-card" style="background-color: #FAF6EF;">
        <div style="font-size: 0.95rem; font-weight: 800; color: #183B3A; margin-bottom: 12px;">THRS Score Guide</div>
        <div style="display: flex; flex-direction: column; gap: 8px;">
            {items_html}
        </div>
    </div>
    """

def classify_additive(e_code: str, e_name: str) -> Tuple[str, str, str]:
    """Classifies additive into (chip_class, category_badge, tag_style)."""
    name_lower = (e_name or "").lower()
    code_str = str(e_code).strip()

    if any(k in name_lower for k in [
        "color", "colour", "tartrazine", "sunset yellow", "allura red", "brilliant blue",
        "carmoisine", "ponceau", "preservative", "benzoate", "sorbate", "sulphite", "sulfite",
        "nitrite", "nitrate", "sweetener", "aspartame", "sucralose", "acesulfame", "saccharin",
        "enhancer", "monosodium glutamate", "msg", "ribonucleotide", "guanylate", "inosinate"
    ]) or code_str in ["102", "110", "122", "124", "129", "133", "211", "224", "249", "250", "621", "627", "631", "635", "950", "951", "955"]:
        return "chip-signal", "Formulation Signal", "#9A6615"

    elif any(k in name_lower for k in [
        "emulsifier", "lecithin", "polysorbate", "e471", "e472", "stabilizer", "stabiliser",
        "thickener", "gum", "carrageenan", "acidity regulator"
    ]) or code_str in ["322", "407", "412", "415", "471", "472", "476"]:
        return "chip-watch", "Watch Additive", "#9A6615"

    else:
        return "chip-standard", "Standard Additive", "#235431"

def format_match_confidence(is_valid: bool, confidence: float) -> str:
    """Formats global counterpart match confidence clearly without clinical claims."""
    if not is_valid or confidence <= 0:
        return "Indian Market Variant · No direct overseas match needed"
    conf_val = int(confidence)
    tier = "High match" if conf_val >= 75 else ("Moderate match" if conf_val >= 50 else "Partial match")
    return f"Global match confidence: {conf_val}% · {tier}"

# ── 4. Warm Editorial Design System & CSS ────────────────────────────────────
render_html("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400..800;1,9..40,400..800&family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Canvas */
    .stApp {
        background-color: #F5EFE4 !important;
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #183B3A;
    }
    
    .block-container {
        max-width: 1200px !important;
        padding-top: 1.8rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    [data-testid="stSidebarUserContent"] {
        padding-top: 1.6rem !important;
        padding-left: 1.15rem !important;
        padding-right: 1.15rem !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #FAF6EF !important;
        border-right: 1px solid #DFD5C4 !important;
        box-shadow: 1px 0 10px rgba(24, 59, 58, 0.03) !important;
    }
    
    div[data-testid="stRadio"] > label {
        display: none !important;
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] {
        gap: 4px !important;
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        display: flex !important;
        align-items: center !important;
        padding: 10px 14px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        color: #55625C !important;
        background-color: transparent !important;
        border-left: 4px solid transparent !important;
        transition: all 0.15s ease-in-out !important;
        cursor: pointer !important;
        margin-bottom: 2px !important;
    }
    
    /* Complete Elimination of Native Radio Circles & Dots */
    div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child,
    div[data-testid="stRadio"] div[role="radiogroup"] label > span:first-child,
    div[data-testid="stRadio"] div[role="radiogroup"] label div[aria-hidden="true"],
    div[data-testid="stRadio"] input[type="radio"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        opacity: 0 !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label p,
    div[data-testid="stRadio"] div[role="radiogroup"] label span,
    div[data-testid="stRadio"] div[role="radiogroup"] label div {
        color: #55625C !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] label:hover,
    div[data-testid="stRadio"] div[role="radiogroup"] label:hover p,
    div[data-testid="stRadio"] div[role="radiogroup"] label:hover span {
        background-color: #EFE7DA !important;
        color: #183B3A !important;
    }
    
    /* Brand Green Active Navigation State */
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"],
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked),
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] p,
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p,
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] span,
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) span {
        background-color: #E2ECE4 !important;
        color: #183B3A !important;
        font-weight: 800 !important;
        border-left: 4px solid #2D5A3D !important;
    }

    /* High Impact Sidebar Stat Card */
    .sidebar-stat-card {
        background-color: #FFFDF8;
        border: 1px solid #E5DBCB;
        border-radius: 10px;
        padding: 10px 12px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(24, 59, 58, 0.02);
    }
    .sidebar-stat-row {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 6px 0;
        font-size: 0.80rem;
        color: #4B5853;
    }
    .sidebar-stat-row:not(:last-child) {
        border-bottom: 1px solid #EFE6D8;
    }
    .sidebar-stat-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 22px;
        height: 22px;
        border-radius: 5px;
        background-color: #E5EEE7;
        color: #2D5A3D;
        flex-shrink: 0;
    }

    /* Flatter Cards & Containers */
    .ti-card {
        background-color: #FFFDF8;
        border: 1px solid #E3D8C8;
        border-radius: 14px;
        padding: 24px 26px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(24, 59, 58, 0.04);
        overflow-wrap: break-word;
        word-break: break-word;
    }
    
    .ti-hero-product {
        background-color: #FFFDF8;
        border: 1px solid #E3D8C8;
        border-radius: 16px;
        padding: 28px 30px;
        margin-bottom: 22px;
        box-shadow: 0 2px 6px rgba(24, 59, 58, 0.05);
        overflow-wrap: break-word;
        word-break: break-word;
    }
    
    .ti-neutral-section {
        background-color: #FFFDF8;
        border: 1px solid #E3D8C8;
        border-radius: 14px;
        padding: 24px 26px;
        margin-bottom: 22px;
        box-shadow: 0 1px 3px rgba(24, 59, 58, 0.04);
        overflow-wrap: break-word;
        word-break: break-word;
    }

    .ti-hero {
        background-color: #FFFDF8;
        border: 1px solid #E3D8C8;
        border-radius: 16px;
        padding: 34px 38px;
        margin-bottom: 26px;
        box-shadow: 0 2px 6px rgba(24, 59, 58, 0.04);
    }

    /* Typography System */
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #183B3A;
        letter-spacing: -0.025em;
        line-height: 1.15;
        margin-bottom: 8px;
    }
    
    .hero-sub {
        font-size: 1.08rem;
        color: #66736D;
        line-height: 1.55;
        max-width: 760px;
        margin-bottom: 0;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #183B3A;
        letter-spacing: -0.015em;
        margin-bottom: 16px;
    }

    /* Widened Single-Line Primary Score Area */
    .ti-score-focal {
        text-align: center;
        padding: 16px 20px;
        border-radius: 14px;
        min-width: 175px;
        width: 180px;
        flex-shrink: 0;
    }
    
    .ti-score-num-primary {
        font-size: 3.1rem;
        font-weight: 800;
        line-height: 1;
        letter-spacing: -0.02em;
        white-space: nowrap;
    }
    
    .ti-score-num-secondary {
        font-size: 1.6rem;
        font-weight: 700;
        line-height: 1;
    }

    /* V2 -> V3 Delta Comparison Component */
    .delta-box {
        display: inline-flex;
        align-items: center;
        flex-wrap: wrap;
        font-size: 0.86rem;
        padding: 6px 12px;
        border-radius: 8px;
        margin-top: 10px;
        border: 1px solid #EAE0D2;
        background-color: #FAF6EF;
        color: #183B3A;
    }
    .delta-neutral { background-color: #FAF6EF; border-color: #EAE0D2; }

    /* Horizontal Driver Impact Bars */
    .driver-bars-container {
        display: flex;
        flex-direction: column;
        gap: 14px;
        margin-top: 12px;
    }
    
    .driver-row {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    
    .driver-label {
        font-size: 0.88rem;
        font-weight: 700;
        color: #183B3A;
        min-width: 150px;
    }
    
    .driver-bar-track {
        flex: 1;
        height: 12px;
        background-color: #FAF6EF;
        border: 1px solid #EAE0D2;
        border-radius: 6px;
        overflow: hidden;
    }
    
    .driver-bar-fill {
        height: 100%;
        border-radius: 5px;
        transition: width 0.3s ease;
    }
    
    .driver-val {
        font-size: 0.88rem;
        font-weight: 800;
        color: #A84832;
        min-width: 85px;
        text-align: right;
    }

    /* Score Guide with 'YOU ARE HERE' Highlight */
    .guide-band-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 12px;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    
    .you-are-here-pill {
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.05em;
        background-color: #183B3A;
        color: #FFFDF8;
        padding: 3px 8px;
        border-radius: 4px;
        text-transform: uppercase;
    }

    /* Risk Tier Themes */
    .tier-excellent { background-color: #E8F2EA; color: #235431; border: 1px solid #A6C9AD; }
    .tier-good      { background-color: #F0F6EE; color: #356840; border: 1px solid #BDD9C1; }
    .tier-average   { background-color: #FDF6E9; color: #9A6615; border: 1px solid #EED4A2; }
    .tier-poor      { background-color: #FAF0EB; color: #98382C; border: 1px solid #E8C8BE; }
    .tier-unscored  { background-color: #F2EFE9; color: #78756E; border: 1px solid #D6D0C5; }

    /* Muted Amber/Terracotta Formulation Badges */
    .signal-pill {
        display: inline-block;
        background-color: #FDF6E9;
        color: #9A6615;
        border: 1px solid #EED4A2;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    
    .clean-pill {
        display: inline-block;
        background-color: #EEF3EC;
        color: #235431;
        border: 1px solid #C4DAC6;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
    }

    .fact-tag {
        display: inline-block;
        background-color: #EEF3EC;
        color: #235431;
        border: 1px solid #C4DAC6;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 8px;
    }

    /* Additive Chips Grid */
    .additive-chip-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 12px;
        margin-top: 14px;
    }
    
    .additive-card {
        padding: 12px 14px;
        border-radius: 10px;
        font-size: 0.88rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .chip-signal {
        background-color: #FDF6E9;
        border: 1px solid #EED4A2;
        color: #183B3A;
    }
    
    .chip-watch {
        background-color: #FDF6E9;
        border: 1px solid #EED4A2;
        color: #183B3A;
    }
    
    .chip-standard {
        background-color: #EEF3EC;
        border: 1px solid #C4DAC6;
        color: #183B3A;
    }

    /* Scannable Recipe Blocks */
    .recipe-box-in {
        background-color: #FAF6EF;
        border: 1px solid #E6DCce;
        border-radius: 10px;
        padding: 16px;
        font-size: 0.9rem;
        line-height: 1.65;
        color: #183B3A;
        min-height: 140px;
        word-break: break-word;
    }
    
    .recipe-box-uk {
        background-color: #F2F7F1;
        border: 1px solid #D0E2CE;
        border-radius: 10px;
        padding: 16px;
        font-size: 0.9rem;
        line-height: 1.65;
        color: #183B3A;
        min-height: 140px;
        word-break: break-word;
    }

    /* Tables */
    .ti-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 12px;
        font-size: 0.92rem;
    }
    .ti-table th {
        background-color: #F7F2E8;
        color: #183B3A;
        padding: 10px 16px;
        text-align: left;
        font-weight: 700;
        border-bottom: 1px solid #E3D8C8;
    }
    .ti-table td {
        padding: 12px 16px;
        border-bottom: 1px solid #EDE5D8;
        color: #183B3A;
    }
    
    /* Premium Interactive Search Bar & Selectbox System */
    div[data-testid="stSelectbox"] {
        margin-bottom: 22px !important;
    }
    
    div[data-testid="stSelectbox"] label,
    div[data-testid="stSelectbox"] label p {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.82rem !important;
        font-weight: 800 !important;
        color: #2D5A3D !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        margin-bottom: 8px !important;
    }
    
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: transparent !important;
        border: none !important;
    }
    
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background-color: #FFFDF8 !important;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%232D5A3D' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'%3E%3C/circle%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'%3E%3C/line%3E%3C/svg%3E") !important;
        background-repeat: no-repeat !important;
        background-position: 14px center !important;
        padding-left: 44px !important;
        padding-right: 14px !important;
        border: 1.5px solid #D5C7B3 !important;
        border-radius: 12px !important;
        min-height: 52px !important;
        box-shadow: 0 2px 6px rgba(24, 59, 58, 0.04) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex !important;
        align-items: center !important;
        cursor: pointer !important;
    }
    
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {
        background-color: #FFFFFF !important;
        border-color: #2D5A3D !important;
        box-shadow: 0 4px 14px rgba(45, 90, 61, 0.12) !important;
    }
    
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
        background-color: #FFFFFF !important;
        border-color: #2D5A3D !important;
        box-shadow: 0 0 0 3.5px rgba(45, 90, 61, 0.16), 0 4px 12px rgba(24, 59, 58, 0.06) !important;
    }
    
    /* Text Inside Search Bar */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] span,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] input,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] div[aria-selected="true"] {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        color: #183B3A !important;
        letter-spacing: -0.01em !important;
    }
    
    /* Search Dropdown Popover & Options Menu Universal Warm Override */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    div[data-baseweb="menu"],
    div[data-baseweb="menu"] * {
        background-color: #FFFDF8 !important;
        color: #183B3A !important;
    }
    
    div[data-baseweb="popover"] {
        border: 1.5px solid #D5C7B3 !important;
        border-radius: 12px !important;
        box-shadow: 0 12px 32px rgba(24, 59, 58, 0.16) !important;
        overflow: hidden !important;
    }
    
    ul[role="listbox"] {
        background-color: #FFFDF8 !important;
        padding: 6px !important;
    }
    
    li[role="option"] {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #183B3A !important;
        background-color: #FFFDF8 !important;
        padding: 10px 14px !important;
        border-radius: 8px !important;
        margin-bottom: 2px !important;
        transition: all 0.12s ease-in-out !important;
        cursor: pointer !important;
    }
    
    li[role="option"] * {
        color: #183B3A !important;
        background-color: transparent !important;
    }
    
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"],
    li[role="option"]:focus {
        background-color: #E2ECE4 !important;
        color: #183B3A !important;
    }

    li[role="option"]:hover *,
    li[role="option"][aria-selected="true"] *,
    li[role="option"]:focus * {
        color: #183B3A !important;
    }
    
    /* Dropdown Chevron Arrow Color */
    div[data-testid="stSelectbox"] svg,
    div[data-baseweb="select"] svg {
        display: block !important;
        visibility: visible !important;
        fill: #2D5A3D !important;
        stroke: #2D5A3D !important;
    }

    /* Popular Shelf Button Pills (Tactile & Clean) */
    div[data-testid="stButton"] button {
        background-color: #FFFDF8 !important;
        border: 1.5px solid #D5C7B3 !important;
        border-radius: 20px !important;
        padding: 6px 14px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.84rem !important;
        font-weight: 700 !important;
        color: #183B3A !important;
        transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 1px 3px rgba(24, 59, 58, 0.04) !important;
        white-space: nowrap !important;
        width: 100% !important;
        text-align: center !important;
    }
    
    div[data-testid="stButton"] button:hover {
        background-color: #E2ECE4 !important;
        border-color: #2D5A3D !important;
        color: #183B3A !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 10px rgba(45, 90, 61, 0.12) !important;
    }
    
    div[data-testid="stButton"] button:active {
        background-color: #2D5A3D !important;
        color: #FFFFFF !important;
        transform: translateY(0) !important;
    }

    /* Selected / Active State Pill Button (Distinct Brand Green Highlight) */
    div[data-testid="stButton"] button[kind="primary"],
    div[data-testid="stButton"] button[data-testid="baseButton-primary"] {
        background-color: #2D5A3D !important;
        border: 1.5px solid #1E3D29 !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        box-shadow: 0 3px 10px rgba(45, 90, 61, 0.28) !important;
    }

    div[data-testid="stButton"] button[kind="primary"] p,
    div[data-testid="stButton"] button[data-testid="baseButton-primary"] p {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    div[data-testid="stButton"] button[kind="primary"]:hover,
    div[data-testid="stButton"] button[data-testid="baseButton-primary"]:hover {
        background-color: #1E3D29 !important;
        border-color: #152B1D !important;
        color: #FFFFFF !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 14px rgba(45, 90, 61, 0.35) !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""")

# ── 5. Sidebar Architecture & Clean Project Identity (No Emojis) ─────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 0 0 14px 0; margin-bottom: 16px; border-bottom: 1px solid #DFD5C4;">
        <div style="display: flex; align-items: center; gap: 11px;">
            <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #183B3A 0%, #2D5A3D 100%); border-radius: 9px; display: flex; align-items: center; justify-content: center; box-shadow: 0 3px 8px rgba(24, 59, 58, 0.16); border: 1px solid #3D7350; flex-shrink: 0;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FAF6EF" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/>
                    <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>
                </svg>
            </div>
            <div>
                <div style="font-family: 'DM Sans', sans-serif; font-size: 1.18rem; font-weight: 900; color: #183B3A; letter-spacing: 0.03em; line-height: 1.1;">
                    TRUE<span style="color: #2D5A3D; margin-left: 3px;">INGREDIENTS</span>
                </div>
                <div style="display: flex; align-items: center; gap: 5px; margin-top: 3px;">
                    <span style="display: inline-block; width: 5px; height: 5px; background-color: #2D5A3D; border-radius: 50%;"></span>
                    <span style="font-size: 0.65rem; font-weight: 800; color: #4F7D5B; letter-spacing: 0.10em; text-transform: uppercase;">Food Intelligence</span>
                </div>
            </div>
        </div>
    </div>
    
    <div class="sidebar-stat-card">
        <div class="sidebar-stat-row">
            <span class="sidebar-stat-icon">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M3 5v14M8 5v14M12 5v14M17 5v14M21 5v14"/></svg>
            </span>
            <div><b>170</b> Packaged Foods Analyzed</div>
        </div>
        <div class="sidebar-stat-row">
            <span class="sidebar-stat-icon">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m16 3 4 4-4 4M20 7H4M8 21l-4-4 4-4M4 17h16"/></svg>
            </span>
            <div><b>60</b> Clean Indian D2C Swaps</div>
        </div>
        <div class="sidebar-stat-row">
            <span class="sidebar-stat-icon">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="m16 12-4-4v8"/></svg>
            </span>
            <div><b>THRS v3.0</b> Scoring Engine</div>
        </div>
    </div>

    <p style='font-size:0.72rem; font-weight:800; color:#8C9690; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:6px;'>NAVIGATION</p>
    """, unsafe_allow_html=True)

    nav_selection = st.sidebar.radio(
        "Navigation",
        ["Home", "Check a Product", "Better Swaps", "How Scoring Works"],
        index=0,
        key="nav_radio"
    )

    st.markdown("""
    <div style="margin-top: 40px; padding-top: 14px; border-top: 1px solid #DFD5C4; font-size: 0.72rem; color: #8C9690; line-height: 1.45;">
        <div style="font-weight: 800; color: #55625C; letter-spacing: 0.02em;">True Ingredients v3.0</div>
        <div>Indian Food Chemistry & Formulation Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

# Unified Session State Synchronization
if "selected_product" not in st.session_state:
    st.session_state["selected_product"] = all_products[0] if all_products else ""

def sync_product_selection(key_name):
    """Guarantees 100% deterministic state synchronization across views."""
    st.session_state["selected_product"] = st.session_state[key_name]

# ────────────────────────────────────────────────────────────────────────────
# 1. HOME EXPERIENCE
# ────────────────────────────────────────────────────────────────────────────
if nav_selection == "Home":
    
    # Hero Introduction
    render_html("""
    <div class="ti-hero">
        <div class="hero-title">Know what's inside your food.</div>
        <div class="hero-sub">Empirical ingredient intelligence, cross-border recipe differences, and clean Indian food alternatives before you buy.</div>
    </div>
    """)
    
    # Product Search
    st.markdown("<p style='font-size: 0.82rem; font-weight: 800; color: #2D5A3D; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px;'>SEARCH OR SELECT A PACKAGED PRODUCT:</p>", unsafe_allow_html=True)
    
    current_idx = all_products.index(st.session_state["selected_product"]) if st.session_state["selected_product"] in all_products else 0
    st.selectbox(
        "Search or select a packaged food product:",
        all_products,
        index=current_idx,
        key="home_search_select",
        on_change=sync_product_selection,
        args=("home_search_select",),
        label_visibility="collapsed"
    )
    
    # Popular Quick Searches Shelf (6 Balanced Categories)
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 14px; margin-bottom: 8px;">
        <span style="font-size: 0.75rem; font-weight: 800; color: #8C9690; text-transform: uppercase; letter-spacing: 0.06em;">POPULAR 1-CLICK PICKS (6 CATEGORIES):</span>
        <span style="font-size: 0.72rem; font-weight: 700; color: #4F7D5B;">1-Click Instant Scan & Score</span>
    </div>
    """, unsafe_allow_html=True)
    
    qcol1, qcol2, qcol3, qcol4, qcol5, qcol6 = st.columns(6)
    
    curr_item = st.session_state.get("selected_product", "").lower()
    is_maggi = "maggi" in curr_item
    is_oreo = "oreo" in curr_item
    is_7up = "7 up" in curr_item or "7up" in curr_item
    is_silk = "silk" in curr_item
    is_lays = "lay" in curr_item and "choc" not in curr_item
    is_muesli = "muesli" in curr_item
    
    def set_search_and_rerun(exact_target):
        if exact_target in all_products:
            st.session_state["selected_product"] = exact_target
        else:
            matches = [p for p in all_products if exact_target.lower() in p.lower()]
            if matches:
                st.session_state["selected_product"] = matches[0]
        st.session_state["scroll_to_results"] = True
        st.rerun()
            
    if qcol1.button("MAGGI · Noodles", type="primary" if is_maggi else "secondary"): set_search_and_rerun("MAGGI 2-Minute Instant Noodles")
    if qcol2.button("Oreo · Biscuit", type="primary" if is_oreo else "secondary"): set_search_and_rerun("Cadbury Oreo Original Chocolatey Sandwich Biscuits")
    if qcol3.button("7 Up · Soda", type="primary" if is_7up else "secondary"): set_search_and_rerun("7 Up Lemon Soft Drink")
    if qcol4.button("Silk · Chocolate", type="primary" if is_silk else "secondary"): set_search_and_rerun("Cadbury Dairy Milk Silk CHOCOLATE BAR")
    if qcol5.button("Lay's · Chips", type="primary" if is_lays else "secondary"): set_search_and_rerun("Lay's Classic Salted Potato Chips")
    if qcol6.button("Muesli · Cereal", type="primary" if is_muesli else "secondary"): set_search_and_rerun("Kellogg's Chocolate Muesli")

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # 4-Step Process Bar
    render_html("""
    <div class="ti-card">
        <div class="section-title">How True Ingredients Works</div>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; text-align: left; margin-top: 16px;">
            <div style="background: #FAF6EF; padding: 18px; border-radius: 10px; border: 1px solid #EAE0D2;">
                <div style="font-size: 0.72rem; font-weight: 800; color: #4F7D5B; letter-spacing: 0.06em;">01 — ANALYZE</div>
                <div style="font-weight: 800; font-size: 0.96rem; margin: 4px 0; color: #183B3A;">Decode Additives</div>
                <div style="font-size: 0.82rem; color: #66736D; line-height: 1.4;">Identify INS E-numbers, preservatives & synthetic dyes</div>
            </div>
            <div style="background: #FAF6EF; padding: 18px; border-radius: 10px; border: 1px solid #EAE0D2;">
                <div style="font-size: 0.72rem; font-weight: 800; color: #4F7D5B; letter-spacing: 0.06em;">02 — SCORE</div>
                <div style="font-weight: 800; font-size: 0.96rem; margin: 4px 0; color: #183B3A;">THRS Risk Profile</div>
                <div style="font-size: 0.82rem; color: #66736D; line-height: 1.4;">Evaluate safety index from 0 to 100</div>
            </div>
            <div style="background: #FAF6EF; padding: 18px; border-radius: 10px; border: 1px solid #EAE0D2;">
                <div style="font-size: 0.72rem; font-weight: 800; color: #4F7D5B; letter-spacing: 0.06em;">03 — COMPARE</div>
                <div style="font-size: 0.96rem; font-weight: 800; margin: 4px 0; color: #183B3A;">Global Recipe Gap</div>
                <div style="font-size: 0.82rem; color: #66736D; line-height: 1.4;">Compare Indian formula vs UK/Global counterpart</div>
            </div>
            <div style="background: #FAF6EF; padding: 18px; border-radius: 10px; border: 1px solid #EAE0D2;">
                <div style="font-size: 0.72rem; font-weight: 800; color: #4F7D5B; letter-spacing: 0.06em;">04 — SWAP</div>
                <div style="font-weight: 800; font-size: 0.96rem; margin: 4px 0; color: #183B3A;">Better Alternatives</div>
                <div style="font-size: 0.82rem; color: #66736D; line-height: 1.4;">Recommend verified clean Indian D2C swaps</div>
            </div>
        </div>
    </div>
    """)
    
    # Selected Product Overview Snapshot
    product = data_manager.get_product_detail(st.session_state["selected_product"])
    if product:
        st.markdown("<div id='selected-product-profile-section' style='margin-top:20px;'></div>", unsafe_allow_html=True)
        
        if st.session_state.get("scroll_to_results"):
            st.session_state["scroll_to_results"] = False
            components.html("""
            <script>
                function executeScroll() {
                    try {
                        const pDoc = window.parent.document;
                        const target = pDoc.getElementById("selected-product-profile-section") || pDoc.querySelector(".ti-hero-product");
                        if (target) {
                            const rect = target.getBoundingClientRect();
                            const offset = rect.top + window.parent.pageYOffset - 50;
                            window.parent.scrollTo({ top: offset, behavior: 'smooth' });
                        }
                    } catch(e) {
                        console.error("Scroll error:", e);
                    }
                }
                setTimeout(executeScroll, 60);
                setTimeout(executeScroll, 220);
            </script>
            """, height=0, width=0)
            
        render_html("<div class='section-title'>Selected Product Profile</div>")
        
        c1, c2 = st.columns([2, 1])
        with c1:
            v2_val = product.get("thrs_v2_score")
            v3_val = product.get("thrs_v3_score", 0.0)
            
            # Primary Focal Score Tier
            tier_class_v3 = "tier-excellent" if v3_val >= 80 else ("tier-good" if v3_val >= 60 else ("tier-average" if v3_val >= 40 else "tier-poor"))
            profile_label = "STRONG PROFILE" if v3_val >= 80 else ("MODERATE PROFILE" if v3_val >= 60 else ("HIGHER BURDEN" if v3_val >= 40 else "HIGH BURDEN"))

            delta_html = get_v2_v3_delta_html(v2_val, v3_val)
            why_html = get_why_this_score_bars_html(product)

            # Hero Product Card (Single-line score)
            render_html(f"""
            <div class="ti-hero-product">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="flex: 1; padding-right: 16px;">
                        <div style="font-size: 0.78rem; font-weight: 800; color: #8C9690; text-transform: uppercase; letter-spacing: 0.08em;">{product['brand']}</div>
                        <div style="font-size: 1.65rem; font-weight: 800; color: #183B3A; margin: 2px 0 8px 0; line-height: 1.25;">{product['item_name']}</div>
                        <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-top: 4px;">
                            <span style="background: #F7F2E8; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; color: #183B3A; font-weight: 600; border: 1px solid #E3D8C8;">
                                Category: {product['category']}
                            </span>
                            {delta_html}
                        </div>
                    </div>
                    <div class="ti-score-focal {tier_class_v3}">
                        <div class="ti-score-num-primary">{v3_val:.1f}</div>
                        <div style="font-size:0.75rem; font-weight:700; opacity:0.85; margin-top:2px;">/ 100</div>
                        <div style="font-size:0.72rem; font-weight:800; text-transform:uppercase; margin-top:6px; letter-spacing:0.04em;">{profile_label}</div>
                    </div>
                </div>
            </div>
            """)
            
            # Why this score section (Flat horizontal bars)
            render_html(why_html)
            
        with c2:
            render_html(get_score_guide_html(v3_val))

# ────────────────────────────────────────────────────────────────────────────
# 2. CHECK A PRODUCT
# ────────────────────────────────────────────────────────────────────────────
elif nav_selection == "Check a Product":
    
    render_html("<div class='section-title'>Product Inspector & Cross-Border Recipe Panel</div>")
    
    current_idx = all_products.index(st.session_state["selected_product"]) if st.session_state["selected_product"] in all_products else 0
    st.selectbox(
        "Select product to inspect:",
        all_products,
        index=current_idx,
        key="inspector_select",
        on_change=sync_product_selection,
        args=("inspector_select",)
    )
    
    product = data_manager.get_product_detail(st.session_state["selected_product"])
    
    if product:
        v2_val = product.get("thrs_v2_score")
        v3_val = product.get("thrs_v3_score", 0.0)
        
        tier_class_v3 = "tier-excellent" if v3_val >= 80 else ("tier-good" if v3_val >= 60 else ("tier-average" if v3_val >= 40 else "tier-poor"))
        profile_label = "STRONG PROFILE" if v3_val >= 80 else ("MODERATE PROFILE" if v3_val >= 60 else ("HIGHER BURDEN" if v3_val >= 40 else "HIGH BURDEN"))
        
        delta_html = get_v2_v3_delta_html(v2_val, v3_val)
        why_html = get_why_this_score_bars_html(product)
        
        # 1. HERO PRODUCT SECTION (Single-line score area)
        render_html(f"""
        <div class="ti-hero-product">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="flex: 1; padding-right: 16px;">
                    <div style="font-size: 0.8rem; font-weight: 800; color: #8C9690; text-transform: uppercase; letter-spacing: 0.08em;">{product['brand']}</div>
                    <div style="font-size: 1.8rem; font-weight: 800; color: #183B3A; margin: 4px 0 8px 0; line-height: 1.25;">{product['item_name']}</div>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-top: 4px;">
                        <span style="background-color: #F7F2E8; padding: 4px 12px; border-radius: 6px; font-size: 0.82rem; color: #183B3A; font-weight: 600; border: 1px solid #E3D8C8;">
                            Category: {product['category']} | Sub-Category: {product['sub_category']}
                        </span>
                        {delta_html}
                    </div>
                </div>
                <div class="ti-score-focal {tier_class_v3}">
                    <div class="ti-score-num-primary">{v3_val:.1f}</div>
                    <div style="font-size:0.75rem; font-weight:700; opacity:0.85; margin-top:2px;">/ 100</div>
                    <div style="font-size:0.72rem; font-weight:800; text-transform:uppercase; margin-top:6px; letter-spacing:0.04em;">{profile_label}</div>
                </div>
            </div>
        </div>
        """)

        # 2. WHY THIS SCORE (Flat Horizontal Bars) & SCORE GUIDE
        c1, c2 = st.columns([2, 1])
        with c1:
            render_html(why_html)
        with c2:
            render_html(get_score_guide_html(v3_val))
        
        # 3. FORMULATION GAP (Visual INDIA vs GLOBAL Comparison)
        match_info_text = format_match_confidence(product.get('is_valid_match', False), product.get('match_confidence', 0.0))
        
        render_html(f"""
        <div style="margin-top: 26px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: flex-end;">
            <div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #183B3A;">India vs Global Formulation Difference</div>
                <div style="font-size: 0.82rem; color: #66736D; margin-top: 2px;">Side-by-side recipe comparison across international market variants</div>
            </div>
            <div style="font-size: 0.82rem; font-weight: 600; color: #4F7D5B; background: #EEF3EC; padding: 4px 10px; border-radius: 6px; border: 1px solid #C4DAC6;">
                {match_info_text}
            </div>
        </div>
        """)
        
        rcol1, rcol2 = st.columns(2)
        with rcol1:
            render_html(f"""
            <div class="ti-card" style="height: 100%;">
                <div style="font-size: 0.78rem; font-weight: 800; color: #C96A4A; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;">
                    INDIA MARKET RECIPE
                </div>
                <div class="recipe-box-in">
                    {product['ingredients_raw']}
                </div>
            </div>
            """)
            
        with rcol2:
            render_html(f"""
            <div class="ti-card" style="height: 100%;">
                <div style="font-size: 0.78rem; font-weight: 800; color: #4F7D5B; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;">
                    GLOBAL MARKET RECIPE (UK / INTERNATIONAL)
                </div>
                <div class="recipe-box-uk">
                    {product.get('uk_ingredients_raw', 'UK/Global counterpart recipe text not available for this product variant.')}
                </div>
            </div>
            """)
            
        # Highlighted Difference Callout Box
        render_html(f"""
        <div class="ti-card" style="background-color: #FAF6EF; border-left: 5px solid #C96A4A;">
            <div style="font-size: 0.78rem; font-weight: 800; color: #C96A4A; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px;">
                KEY FORMULATION DIFFERENCE
            </div>
            <div style="font-size: 1.02rem; color: #183B3A; line-height: 1.6; font-weight: 500;">
                {product['key_difference']}
            </div>
        </div>
        """)
        
        # 4. COMPACT ADDITIVE CHIPS PRESENTATION
        e_numbers = product.get("decoded_e_numbers", {})
        
        st.markdown("<h4 style='color:#183B3A; font-weight:800; margin-top:24px; margin-bottom:6px;'>Decoded Food Additives (INS / E-Numbers)</h4>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.84rem; color:#66736D; margin-bottom:12px;'>Functional breakdown of detected additive INS codes.</p>", unsafe_allow_html=True)
        
        if e_numbers and isinstance(e_numbers, dict):
            chips_html = ""
            for e_code, e_name in e_numbers.items():
                chip_class, cat_badge, badge_color = classify_additive(e_code, e_name)
                chips_html += f"""
                <div class="additive-card {chip_class}">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                        <b style="font-size:0.92rem; color:{badge_color};">INS {e_code} / E{e_code}</b>
                        <span style="font-size:0.68rem; font-weight:700; text-transform:uppercase; color:{badge_color}; opacity:0.85;">{cat_badge}</span>
                    </div>
                    <div style="font-size:0.85rem; color:#183B3A; font-weight:600; line-height:1.35;">
                        {e_name}
                    </div>
                </div>
                """
            
            render_html(f"""
            <div class="additive-chip-grid">
                {chips_html}
            </div>
            """)
            
            # Expandable Full Registry Table
            with st.expander("View complete decoded additives registry table"):
                rows_html = ""
                for e_code, e_name in e_numbers.items():
                    rows_html += f"""
                    <tr>
                        <td style="font-weight: 700; color: #183B3A;">INS {e_code} / E{e_code}</td>
                        <td style="font-weight: 500; color: #183B3A;">{e_name}</td>
                    </tr>
                    """
                
                render_html(f"""
                <table class="ti-table">
                    <thead>
                        <tr>
                            <th>Additive Code</th>
                            <th>Decoded Functional Name</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
                """)
        else:
            st.info("No synthetic E-number additives detected in this product label.")

# ────────────────────────────────────────────────────────────────────────────
# 3. BETTER SWAPS
# ────────────────────────────────────────────────────────────────────────────
elif nav_selection == "Better Swaps":
    
    render_html("<div class='section-title'>Clean Indian D2C Alternatives</div>")
    
    current_idx = all_products.index(st.session_state["selected_product"]) if st.session_state["selected_product"] in all_products else 0
    st.selectbox(
        "Select product to find cleaner swaps for:",
        all_products,
        index=current_idx,
        key="swaps_select",
        on_change=sync_product_selection,
        args=("swaps_select",)
    )
    
    product = data_manager.get_product_detail(st.session_state["selected_product"])
    
    if product:
        recs = product.get("recommendations", [])
        v3_val = product.get("thrs_v3_score", 0.0)
        v2_val = product.get("thrs_v2_score")
        
        delta_html = get_v2_v3_delta_html(v2_val, v3_val)
        
        render_html(f"""
        <div class="ti-hero-product" style="background-color: #FAF6EF;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1; padding-right: 16px;">
                    <div style="font-size: 0.75rem; font-weight: 800; color: #8C9690; letter-spacing: 0.06em; text-transform: uppercase;">SCANNED PRODUCT</div>
                    <div style="font-size: 1.45rem; font-weight: 800; color: #183B3A;">{product['brand']} — {product['item_name']}</div>
                    <div style="margin-top: 6px;">{delta_html}</div>
                </div>
                <div style="text-align: right;">
                    <div class="ti-score-focal tier-average" style="padding: 12px 18px; min-width: 120px;">
                        <div class="ti-score-num-secondary" style="font-size: 2.0rem;">{v3_val:.1f}</div>
                        <div style="font-size: 0.65rem; font-weight: 800; opacity:0.85;">THRS v3</div>
                    </div>
                </div>
            </div>
        </div>
        """)
        
        render_html("<div class='section-title' style='font-size: 1.15rem; margin-top: 24px;'>Recommended Healthier Swaps</div>")
        
        if recs:
            # Rank best alternative first by THRS v3 health score
            sorted_recs = sorted(recs, key=lambda x: x.get('thrs_v3_score') if x.get('thrs_v3_score') is not None else x.get('thrs_v2_score', 0), reverse=True)
            for idx, rec in enumerate(sorted_recs, 1):
                rec_score = rec.get("thrs_v3_score") if rec.get("thrs_v3_score") is not None else rec.get("thrs_v2_score", 0)
                reasons = data_manager.derive_swap_explanation(product, rec)
                
                facts_html = "".join([f'<span class="fact-tag">{r}</span>' for r in reasons])
                
                render_html(f"""
                <div class="ti-card" style="border-left: 5px solid #4F7D5B;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <div style="font-size: 0.72rem; font-weight: 800; color: #4F7D5B; letter-spacing: 0.06em; text-transform: uppercase;">
                                BETTER MATCH #{idx}
                            </div>
                            <div style="font-size: 1.35rem; font-weight: 800; color: #183B3A; margin: 4px 0 2px 0;">
                                {rec['brand']} — {rec['item_name']}
                            </div>
                        </div>
                        <div class="ti-score-focal tier-excellent" style="padding: 10px 18px;">
                            <div class="ti-score-num-secondary">{rec_score if isinstance(rec_score, (int, str)) else f"{rec_score:.1f}"}</div>
                            <div style="font-size: 0.65rem; font-weight: 800; color: #235431; margin-top: 2px;">THRS SCORE</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 14px;">
                        <div style="font-size: 0.82rem; font-weight: 800; color: #4F7D5B; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 8px;">
                            Why This Swap? (Verified Facts):
                        </div>
                        <div>
                            {facts_html}
                        </div>
                    </div>
                    
                    <hr style="margin: 14px 0; border: 0; border-top: 1px solid #EDE5D8;">
                    <div style="font-size: 0.88rem; color: #66736D; line-height: 1.5;">
                        <b style="color: #183B3A;">Product Profile:</b> {rec.get('key_difference', '')}
                    </div>
                </div>
                """)
        else:
            st.warning("No clean alternatives found passing the health floor guardrail for this product category.")

# ────────────────────────────────────────────────────────────────────────────
# 4. HOW SCORING WORKS
# ────────────────────────────────────────────────────────────────────────────
elif nav_selection == "How Scoring Works":
    render_html("<div class='section-title'>THRS Scoring Methodology & Engine Architecture</div>")
    
    render_html("""
    <!-- Overview Card -->
    <div class="ti-card">
        <div style="font-size: 1.25rem; font-weight: 800; color: #183B3A; margin-bottom: 8px;">
            The Evolution of Transparent Health Risk Scoring (THRS)
        </div>
        <p style="color: #66736D; line-height: 1.6; font-size: 0.95rem; margin-bottom: 0;">
            The True Ingredients platform underwent a rigorous mathematical upgrade from its initial prototype (<b>THRS v2.0</b>) to the locked production engine (<b>THRS v3.0</b>).
            This page breaks down both formulas and walks through real-world product examples to demonstrate why the new model is far more accurate, scientifically defensible, and reliable.
        </p>
    </div>

    <!-- Section 1: Side-by-Side Model Comparison -->
    <div class="ti-card">
        <div style="font-size: 1.10rem; font-weight: 800; color: #183B3A; margin-bottom: 14px;">
            1. Comparative Model Architecture: THRS v2.0 vs THRS v3.0
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px;">
            <!-- THRS v2.0 Box -->
            <div style="background: #FAF6EF; padding: 18px; border-radius: 10px; border: 1px solid #EAE0D2;">
                <div style="font-size: 0.75rem; font-weight: 800; color: #8C9690; text-transform: uppercase; letter-spacing: 0.05em;">Legacy Prototype</div>
                <div style="font-size: 1.20rem; font-weight: 800; color: #183B3A; margin: 4px 0 10px 0;">THRS v2.0 (Checklist Model)</div>
                <div style="background: #FFFDF8; padding: 10px 12px; border-radius: 6px; border: 1px solid #E3D8C8; font-size: 0.84rem; font-weight: 700; color: #183B3A; margin-bottom: 10px;">
                    Score = Category Base - Flat Penalties
                </div>
                <div style="font-size: 0.82rem; color: #55625C; line-height: 1.55;">
                    • <b>Arbitrary Category Baselines:</b> Beverages started at 70, Sweets at 85, General foods at 95.<br>
                    • <b>Step-Function Cliff Edges:</b> A single gram of sugar triggered the full -15 pt deduction.<br>
                    • <b>Double-Counting:</b> Refined sugar in ingredient text penalized the product twice (once in nutrition, once in checklist).
                </div>
            </div>

            <!-- THRS v3.0 Box -->
            <div style="background: #EEF4EE; padding: 18px; border-radius: 10px; border: 1px solid #CFDEC9;">
                <div style="font-size: 0.75rem; font-weight: 800; color: #2D5A3D; text-transform: uppercase; letter-spacing: 0.05em;">Locked Production Engine</div>
                <div style="font-size: 1.20rem; font-weight: 800; color: #183B3A; margin: 4px 0 10px 0;">THRS v3.0 (Dual-Vector Engine)</div>
                <div style="background: #FFFDF8; padding: 10px 12px; border-radius: 6px; border: 1px solid #CFDEC9; font-size: 0.84rem; font-weight: 700; color: #183B3A; margin-bottom: 10px;">
                    THRS v3 = 100.0 - P_nutrition - P_ingredient &nbsp; (P_nutrition ≤ 40, P_ingredient ≤ 25)
                </div>
                <div style="font-size: 0.82rem; color: #55625C; line-height: 1.55;">
                    • <b>Universal 100.0 Baseline:</b> Every product starts equal, eliminating category bias.<br>
                    • <b>Continuous Dose-Response:</b> Smooth piecewise curves measure exact nutrient density.<br>
                    • <b>Decoupled Additive Signals:</b> Chemical ultra-processing (INS dyes, preservatives, palm oil) is isolated from nutrition.
                </div>
            </div>
        </div>
    </div>

    <!-- Section 2: Step-by-Step Worked Product Examples -->
    <div class="ti-card" style="border-left: 5px solid #2D5A3D;">
        <div style="font-size: 1.10rem; font-weight: 800; color: #183B3A; margin-bottom: 6px;">
            2. Real-World Calculation Walkthroughs: v2 vs v3
        </div>
        <div style="font-size: 0.85rem; color: #66736D; margin-bottom: 18px;">
            Here is how both engines evaluate the exact same products step-by-step:
        </div>

        <!-- Example A: Cadbury Oreo -->
        <div style="background: #FAF6EF; padding: 18px; border-radius: 10px; border: 1px solid #EAE0D2; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="font-size: 1.05rem; font-weight: 800; color: #183B3A;">Example A: Cadbury Oreo Original Sandwich Biscuits (100g)</div>
                <div style="font-size: 0.82rem; font-weight: 700; color: #4F7D5B; background: #FFFDF8; padding: 4px 10px; border-radius: 6px; border: 1px solid #E3D8C8;">
                    Solid Food · 38g Sugar · 9.5g Sat Fat · 490mg Sodium · Palm Oil
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 10px; font-size: 0.84rem;">
                <div style="background: #FFFDF8; padding: 12px 14px; border-radius: 8px; border: 1px solid #E3D8C8;">
                    <b style="color: #8C9690; text-transform: uppercase;">Under THRS v2.0 (Legacy):</b><br>
                    • Category Base (Sweets/Biscuits): <b>85 pts</b><br>
                    • Sugar Penalty (Refined sugar in text): <b>-15 pts</b><br>
                    • Palm Oil Penalty (Palmolein detected): <b>-10 pts</b><br>
                    • Emulsifier Penalty (INS 322 detected): <b>-10 pts</b><br>
                    • <b>Result:</b> 85 - 15 - 10 - 10 = <b style="color: #98382C; font-size: 1.0rem;">35 / 100</b><br>
                    <span style="font-size: 0.78rem; color: #66736D;"><i>Flaw: Slashed a 9.5g fat biscuit down to severe 35 on arbitrary flat penalties.</i></span>
                </div>

                <div style="background: #EEF4EE; padding: 12px 14px; border-radius: 8px; border: 1px solid #CFDEC9;">
                    <b style="color: #2D5A3D; text-transform: uppercase;">Under THRS v3.0 (Production):</b><br>
                    • Universal Starting Base: <b>100.0 pts</b><br>
                    • Sugar Deduction (38.0g solid): <b>-17.9 pts</b><br>
                    • Saturated Fat Deduction (9.5g solid): <b>-10.3 pts</b><br>
                    • Sodium Deduction (490mg solid): <b>-6.1 pts</b><br>
                    • Formulation Signal (Refined Palm Oil): <b>-3.0 pts</b><br>
                    • <b>Result:</b> 100.0 - 34.3 (Nutri) - 3.0 (Signals) = <b style="color: #356840; font-size: 1.0rem;">63.1 / 100</b><br>
                    <span style="font-size: 0.78rem; color: #2D5A3D;"><i>Accurate: Correctly classifies Oreo as a moderate sweet treat.</i></span>
                </div>
            </div>
        </div>

        <!-- Example B: 7 Up Lemon Soft Drink -->
        <div style="background: #FAF6EF; padding: 18px; border-radius: 10px; border: 1px solid #EAE0D2;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="font-size: 1.05rem; font-weight: 800; color: #183B3A;">Example B: 7 Up Lemon Soft Drink (100ml)</div>
                <div style="font-size: 0.82rem; font-weight: 700; color: #4F7D5B; background: #FFFDF8; padding: 4px 10px; border-radius: 6px; border: 1px solid #E3D8C8;">
                    Liquid Beverage · 9.0g Sugar · 0.0g Sat Fat · 18mg Sodium · INS 211 Preservative
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 10px; font-size: 0.84rem;">
                <div style="background: #FFFDF8; padding: 12px 14px; border-radius: 8px; border: 1px solid #E3D8C8;">
                    <b style="color: #8C9690; text-transform: uppercase;">Under THRS v2.0 (Legacy):</b><br>
                    • Forced Soda Base (Pre-demoted): <b>70 pts</b><br>
                    • Sugar Penalty (Flat check): <b>-15 pts</b><br>
                    • Preservative Penalty (INS 211): <b>-15 pts</b><br>
                    • <b>Result:</b> 70 - 15 - 15 = <b style="color: #98382C; font-size: 1.0rem;">40 / 100</b><br>
                    <span style="font-size: 0.78rem; color: #66736D;"><i>Flaw: Double-penalized carbonated water with zero fat and salt down to 40.</i></span>
                </div>

                <div style="background: #EEF4EE; padding: 12px 14px; border-radius: 8px; border: 1px solid #CFDEC9;">
                    <b style="color: #2D5A3D; text-transform: uppercase;">Under THRS v3.0 (Production):</b><br>
                    • Universal Starting Base: <b>100.0 pts</b><br>
                    • Liquid Sugar Deduction (9.0g / 100ml): <b>-14.5 pts</b><br>
                    • Saturated Fat & Sodium (0g fat, 18mg sodium): <b>0.0 pts</b><br>
                    • Formulation Signal (INS 211 Sodium Benzoate): <b>-5.0 pts</b><br>
                    • <b>Result:</b> 100.0 - 14.5 (Nutri) - 5.0 (Signals) = <b style="color: #235431; font-size: 1.0rem;">80.5 / 100</b><br>
                    <span style="font-size: 0.78rem; color: #2D5A3D;"><i>Accurate: Accurately reflects 90% water, zero fat, with exact sugar and preservative load.</i></span>
                </div>
            </div>
        </div>
    </div>

    <!-- Section 3: Vector 1 Nutrition Details -->
    <div class="ti-card">
        <div style="font-size: 1.10rem; font-weight: 800; color: #183B3A; margin-bottom: 6px;">
            3. THRS v3.0 Vector 1: Continuous Macronutrient Curves (Max 40.0 Points Deduction)
        </div>
        <div style="font-size: 0.85rem; color: #66736D; margin-bottom: 18px;">
            Evaluates continuous nutrient density per 100g (solid foods) or 100ml (beverages) using piece-wise dose-response curves aligned with WHO & FSSAI thresholds:
        </div>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px;">
            <!-- Sugar Card -->
            <div style="background: #FAF6EF; padding: 16px; border-radius: 10px; border: 1px solid #EAE0D2;">
                <div style="font-size: 0.75rem; font-weight: 800; color: #C96A4A; text-transform: uppercase; letter-spacing: 0.05em;">Sugar Deduction</div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #183B3A; margin: 4px 0 8px 0;">Max 25.0 pts</div>
                <div style="font-size: 0.82rem; color: #55625C; line-height: 1.5;">
                    • <b>Solids:</b> 0 pts below 5.0g. Ramps to 14.0 pts at 22.5g (+0.25 pts/g above 22.5g).<br>
                    • <b>Liquids:</b> 0 pts below 2.5g. Ramps to 14.0 pts at 11.25g (+1.0 pt/g above 11.25g).
                </div>
            </div>

            <!-- Saturated Fat Card -->
            <div style="background: #FAF6EF; padding: 16px; border-radius: 10px; border: 1px solid #EAE0D2;">
                <div style="font-size: 0.75rem; font-weight: 800; color: #D9A441; text-transform: uppercase; letter-spacing: 0.05em;">Saturated Fat Deduction</div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #183B3A; margin: 4px 0 8px 0;">Max 15.0 pts</div>
                <div style="font-size: 0.82rem; color: #55625C; line-height: 1.5;">
                    • <b>Solids:</b> 0 pts below 1.5g. Deducts 8.0 pts at 5.0g (+0.50 pts/g above 5.0g).<br>
                    • <b>Liquids:</b> 0 pts below 0.75g. Deducts 8.0 pts at 2.5g (+0.50 pts/g above 2.5g).
                </div>
            </div>

            <!-- Sodium Card -->
            <div style="background: #FAF6EF; padding: 16px; border-radius: 10px; border: 1px solid #EAE0D2;">
                <div style="font-size: 0.75rem; font-weight: 800; color: #C58A2B; text-transform: uppercase; letter-spacing: 0.05em;">Sodium Deduction</div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #183B3A; margin: 4px 0 8px 0;">Max 15.0 pts</div>
                <div style="font-size: 0.82rem; color: #55625C; line-height: 1.5;">
                    • <b>Solids:</b> 0 pts below 120mg. Deducts 8.0 pts at 600mg (+0.01 pts/mg above 600mg).<br>
                    • <b>Liquids:</b> 0 pts below 120mg. Deducts 8.0 pts at 300mg (+0.01 pts/mg above 300mg).
                </div>
            </div>
        </div>

        <div style="font-size: 0.84rem; color: #66736D; background: #FFFDF8; padding: 12px 14px; border-radius: 8px; border: 1px solid #E3D8C8;">
            <b>Total Nutrition Cap:</b> The sum of Sugar + Saturated Fat + Sodium deductions is capped at a maximum of <b>40.0 points</b> to prevent single-nutrient distortion.
        </div>
    </div>

    <!-- Section 4: Vector 2 Formulation Details -->
    <div class="ti-card">
        <div style="font-size: 1.10rem; font-weight: 800; color: #183B3A; margin-bottom: 6px;">
            4. THRS v3.0 Vector 2: Additive Formulation Signals (Max 25.0 Points Deduction)
        </div>
        <div style="font-size: 0.85rem; color: #66736D; margin-bottom: 16px;">
            Evaluates qualitative presence of industrial ultra-processing ingredients and chemical additives detected in the ingredient label:
        </div>

        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; font-size: 0.88rem; color: #183B3A;">
            <div style="background: #FAF6EF; padding: 12px 14px; border-radius: 8px; border: 1px solid #EAE0D2; display: flex; justify-content: space-between; align-items: center;">
                <div><b>Synthetic Food Dyes</b> (Tartrazine, Sunset Yellow, Allura Red, Brilliant Blue)</div>
                <div style="font-weight: 800; color: #98382C; min-width: 70px; text-align: right;">-8.0 pts</div>
            </div>
            <div style="background: #FAF6EF; padding: 12px 14px; border-radius: 8px; border: 1px solid #EAE0D2; display: flex; justify-content: space-between; align-items: center;">
                <div><b>Artificial Sweeteners</b> (Aspartame, Sucralose, Acesulfame K, Saccharin)</div>
                <div style="font-weight: 800; color: #98382C; min-width: 70px; text-align: right;">-6.0 pts</div>
            </div>
            <div style="background: #FAF6EF; padding: 12px 14px; border-radius: 8px; border: 1px solid #EAE0D2; display: flex; justify-content: space-between; align-items: center;">
                <div><b>Chemical Preservatives</b> (INS 211 Sodium Benzoate, INS 202 Potassium Sorbate)</div>
                <div style="font-weight: 800; color: #98382C; min-width: 70px; text-align: right;">-5.0 pts</div>
            </div>
            <div style="background: #FAF6EF; padding: 12px 14px; border-radius: 8px; border: 1px solid #EAE0D2; display: flex; justify-content: space-between; align-items: center;">
                <div><b>Flavor Enhancers</b> (MSG / Monosodium Glutamate, INS 627, INS 631)</div>
                <div style="font-weight: 800; color: #9A6615; min-width: 70px; text-align: right;">-4.0 pts</div>
            </div>
            <div style="background: #FAF6EF; padding: 12px 14px; border-radius: 8px; border: 1px solid #EAE0D2; display: flex; justify-content: space-between; align-items: center;">
                <div><b>Industrial Emulsifiers</b> (INS 476 / PGPR, INS 442 Ammonium Phosphatides)</div>
                <div style="font-weight: 800; color: #9A6615; min-width: 70px; text-align: right;">-4.0 pts</div>
            </div>
            <div style="background: #FAF6EF; padding: 12px 14px; border-radius: 8px; border: 1px solid #EAE0D2; display: flex; justify-content: space-between; align-items: center;">
                <div><b>Refined Palm Oil & Palmolein</b> (Substitute for dairy fat / cold pressed oils)</div>
                <div style="font-weight: 800; color: #9A6615; min-width: 70px; text-align: right;">-3.0 pts</div>
            </div>
        </div>

        <div style="margin-top: 14px; font-size: 0.84rem; color: #66736D; background: #FFFDF8; padding: 12px 14px; border-radius: 8px; border: 1px solid #E3D8C8;">
            <b>Anti-Double Counting Rule:</b> Sugar, salt, and water mentioned in ingredient text do not trigger formulation penalties, as their physiological load is already measured continuously in the nutrition panel. Total additive deductions are capped at <b>25.0 points</b>.
        </div>
    </div>

    <!-- Section 5: Score Bands Reference Table -->
    <div class="ti-card">
        <div style="font-size: 1.10rem; font-weight: 800; color: #183B3A; margin-bottom: 14px;">
            5. THRS v3.0 Score Bands & Clinical Profiles
        </div>

        <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem; text-align: left;">
            <thead>
                <tr style="background-color: #FAF6EF; border-bottom: 2px solid #E3D8C8;">
                    <th style="padding: 10px 14px; color: #183B3A; font-weight: 800;">Score Range</th>
                    <th style="padding: 10px 14px; color: #183B3A; font-weight: 800;">Profile Tier</th>
                    <th style="padding: 10px 14px; color: #183B3A; font-weight: 800;">Formulation & Nutrient Interpretation</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid #EDE5D8;">
                    <td style="padding: 12px 14px; font-weight: 800; color: #235431;">80.0 – 100.0</td>
                    <td style="padding: 12px 14px; font-weight: 700; color: #235431;">Strong Profile</td>
                    <td style="padding: 12px 14px; color: #55625C;">Clean, low-risk formulation with low or moderate nutrient density and zero high-risk chemical additives.</td>
                </tr>
                <tr style="border-bottom: 1px solid #EDE5D8;">
                    <td style="padding: 12px 14px; font-weight: 800; color: #356840;">60.0 – 79.9</td>
                    <td style="padding: 12px 14px; font-weight: 700; color: #356840;">Moderate Profile</td>
                    <td style="padding: 12px 14px; color: #55625C;">Higher natural energy/fat density (e.g. dark chocolate) or minor formulation signals. Suitable as moderate choices.</td>
                </tr>
                <tr style="border-bottom: 1px solid #EDE5D8;">
                    <td style="padding: 12px 14px; font-weight: 800; color: #9A6615;">40.0 – 59.9</td>
                    <td style="padding: 12px 14px; font-weight: 700; color: #9A6615;">Higher Modeled Burden</td>
                    <td style="padding: 12px 14px; color: #55625C;">Elevated refined sugar, high saturated fat, or presence of industrial palm oil and emulsifiers.</td>
                </tr>
                <tr>
                    <td style="padding: 12px 14px; font-weight: 800; color: #98382C;">0.0 – 39.9</td>
                    <td style="padding: 12px 14px; font-weight: 700; color: #98382C;">High Modeled Burden</td>
                    <td style="padding: 12px 14px; color: #55625C;">Compounded nutrient penalties and multiple ultra-processed additive signals (synthetic dyes + chemical preservatives).</td>
                </tr>
            </tbody>
        </table>
    </div>
    """)

