"""
THRS v3 Production Scoring Module (`src/thrs_v3_scoring.py`)
============================================================
Authoritative production module for Total Health & Risk Score (THRS v3).
Implements the locked Phase 4F Candidate 2 continuous piecewise nutrition
and decoupled additive formulation signal engine.

System Boundaries:
  - P_nutrition capped at 40.0 pts (Sugar <= 25, SatFat <= 15, Sodium <= 15).
  - P_ingredient capped at 25.0 pts (Colors -8, Sweeteners -6, Preservatives -5,
    Flavor Enhancers -4, Industrial Emulsifiers -4, Refined Palm Oil -3).
  - Double-counting safeguard: Sugar and Salt text contribute 0.0 pts to P_ingredient.
  - Master Score: THRS_v3 = max(0.0, min(100.0, 100.0 - (P_nutrition + P_ingredient))).

Pure, deterministic functions with zero side effects.
"""

import re
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd


def parse_numeric_nutrient(val: Any) -> Optional[float]:
    """Parses numeric nutrient strings, handling inequality labels (<0.5 -> 0.25)."""
    if pd.isna(val) or val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    if s.startswith('<'):
        try:
            return float(s[1:].strip()) / 2.0
        except ValueError:
            return None
    try:
        return float(s)
    except ValueError:
        return None


def get_serving_norm_factor(serving_size_g: Any) -> float:
    """Computes normalization factor to standard 100g/ml basis."""
    try:
        sz = float(serving_size_g)
        if sz > 0.0 and sz != 100.0:
            return 100.0 / sz
    except (ValueError, TypeError):
        pass
    return 1.0


def calc_sugar_penalty_v3(sugar_g: float, is_liquid: bool = False) -> float:
    """
    Computes Locked Candidate 2 Sugar Penalty (Sub-cap = 25.0 pts).
    Solid:  T_low=5.0g, T_high=22.5g, Base=14.0, Slope=0.25 pts/g, Cap=25.0
    Liquid: T_low=2.5g, T_high=11.25g, Base=14.0, Slope=1.00 pts/g, Cap=25.0
    """
    if pd.isna(sugar_g) or sugar_g is None:
        return np.nan
    s = float(sugar_g)
    if is_liquid:
        t_low, t_high = 2.5, 11.25
        if s <= t_low:
            return 0.0
        elif s <= t_high:
            return 14.0 * ((s - t_low) / (t_high - t_low))
        else:
            return min(25.0, 14.0 + 1.00 * (s - t_high))
    else:
        t_low, t_high = 5.0, 22.5
        if s <= t_low:
            return 0.0
        elif s <= t_high:
            return 14.0 * ((s - t_low) / (t_high - t_low))
        else:
            return min(25.0, 14.0 + 0.25 * (s - t_high))


def calc_sat_fat_penalty_v3(sat_fat_g: float, is_liquid: bool = False) -> float:
    """
    Computes Frozen Saturated Fat Penalty (Sub-cap = 15.0 pts).
    Solid:  T_low=1.5g, T_high=5.0g, Base=8.0, Slope=0.50 pts/g, Cap=15.0
    Liquid: T_low=0.75g, T_high=2.5g, Base=8.0, Slope=0.50 pts/g, Cap=15.0
    """
    if pd.isna(sat_fat_g) or sat_fat_g is None:
        return np.nan
    f = float(sat_fat_g)
    t_low = 0.75 if is_liquid else 1.5
    t_high = 2.5 if is_liquid else 5.0
    if f <= t_low:
        return 0.0
    elif f <= t_high:
        return 8.0 * ((f - t_low) / (t_high - t_low))
    else:
        return min(15.0, 8.0 + 0.50 * (f - t_high))


def calc_sodium_penalty_v3(sodium_mg: float, is_liquid: bool = False) -> float:
    """
    Computes Frozen Sodium Penalty (Sub-cap = 15.0 pts).
    Solid/Liquid: T_low=120mg, T_high=600mg (300mg liq), Base=8.0, Slope=0.01 pts/mg, Cap=15.0
    """
    if pd.isna(sodium_mg) or sodium_mg is None:
        return np.nan
    na = float(sodium_mg)
    t_low = 120.0
    t_high = 300.0 if is_liquid else 600.0
    if na <= t_low:
        return 0.0
    elif na <= t_high:
        return 8.0 * ((na - t_low) / (t_high - t_low))
    else:
        return min(15.0, 8.0 + 0.01 * (na - t_high))


def calc_p_nutrition_v3(
    sugar_g: float, sat_fat_g: float, sodium_mg: float, is_liquid: bool = False
) -> Dict[str, float]:
    """
    Computes combined nutrition component penalties (Overall Ceiling = 40.0 pts).
    Returns dictionary with individual and combined penalties.
    """
    p_s = calc_sugar_penalty_v3(sugar_g, is_liquid)
    p_f = calc_sat_fat_penalty_v3(sat_fat_g, is_liquid)
    p_na = calc_sodium_penalty_v3(sodium_mg, is_liquid)

    if pd.isna(p_s) or pd.isna(p_f) or pd.isna(p_na):
        return {
            'p_sugar': np.nan,
            'p_sat_fat': np.nan,
            'p_sodium': np.nan,
            'p_nutrition': np.nan,
        }

    p_nutri = min(40.0, float(p_s) + float(p_f) + float(p_na))
    return {
        'p_sugar': round(float(p_s), 2),
        'p_sat_fat': round(float(p_f), 2),
        'p_sodium': round(float(p_na), 2),
        'p_nutrition': round(p_nutri, 2),
    }


def detect_ingredient_penalties_v3(
    ingredients_text: str, decoded_e_dict: Optional[Dict[str, str]] = None
) -> Tuple[float, List[str]]:
    """
    Computes Frozen Qualitative Ingredient Penalties (Component Cap = 25.0 pts).
    Double-counting safeguard: Sugar and Salt text contribute 0.0 pts.
    Returns (capped_penalty, detected_signal_classes).
    """
    raw_s = str(ingredients_text) if pd.notna(ingredients_text) and ingredients_text else ''
    # Strip allergen / cross-contamination disclaimers
    recipe_text = re.split(r'allergen\s+information|may\s+contain', raw_s, flags=re.IGNORECASE)[0].lower()

    e_codes = set()
    if isinstance(decoded_e_dict, dict):
        for k in decoded_e_dict.keys():
            clean_k = str(k).upper().replace('E-', '').replace('E', '').replace('INS', '').replace(' ', '').strip()
            if clean_k in recipe_text or f"ins {clean_k.lower()}" in recipe_text or f"({clean_k.lower()})" in recipe_text:
                e_codes.add(clean_k)
            elif not ingredients_text:
                e_codes.add(clean_k)

    found_ins = re.findall(r'ins\s*(\d+[a-z]*)', recipe_text)
    for c in found_ins:
        e_codes.add(c.upper().strip())

    detected_classes = []
    total_penalty = 0.0

    # 1. Colors (-8 pts)
    azo_codes = {'102', '110', '124', '129'}
    triaryl_codes = {'133'}
    azo_kw = ['tartrazine', 'sunset yellow', 'allura red', 'ponceau']
    triaryl_kw = ['brilliant blue']
    if any(c in e_codes for c in azo_codes | triaryl_codes) or any(k in recipe_text for k in azo_kw + triaryl_kw):
        detected_classes.append('SYNTHETIC_COLORS')
        total_penalty += 8.0

    # 2. Sweeteners (-6 pts)
    sweet_codes = {'950', '951', '954', '955'}
    sweet_kw = ['sucralose', 'aspartame', 'acesulfame', 'saccharin']
    if any(c in e_codes for c in sweet_codes) or any(k in recipe_text for k in sweet_kw):
        detected_classes.append('ARTIFICIAL_SWEETENERS')
        total_penalty += 6.0

    # 3. Preservatives (-5 pts)
    pres_codes = {'211', '202', '220', '221', '222', '223', '224', '228'}
    pres_kw = ['sodium benzoate', 'potassium sorbate', 'preservative (211)', 'preservative (202)', 'benzoate', 'sorbate', 'metabisulphite', 'metabisulfite']
    if any(c in e_codes for c in pres_codes) or any(k in recipe_text for k in pres_kw):
        detected_classes.append('CHEMICAL_PRESERVATIVES')
        total_penalty += 5.0

    # 4. Flavor Enhancers (-4 pts)
    flav_codes = {'621', '627', '631', '635'}
    flav_kw = ['glutamate', 'inosinate', 'guanylate', 'ribonucleotide', 'msg', 'flavour enhancer (635)']
    if any(c in e_codes for c in flav_codes) or any(k in recipe_text for k in flav_kw):
        detected_classes.append('FLAVOR_ENHANCERS')
        total_penalty += 4.0

    # 5. Industrial Emulsifiers (-4 pts)
    emul_codes = {'476', '442', '471', '472E', '472'}
    emul_kw = ['polyricinoleate', 'pgpr', 'ammonium phosphatide', 'mono- and di-glycerides', 'mono- and diglycerides', 'datem', 'ins 471', 'ins 476']
    if any(c in e_codes for c in emul_codes) or any(k in recipe_text for k in emul_kw):
        detected_classes.append('INDUSTRIAL_EMULSIFIERS')
        total_penalty += 4.0

    # 6. Refined Palm Oil (-3 pts)
    explicit_palm = ['palm oil', 'palmolein', 'palm fat', 'fractionated fat', 'palm kernel', 'vegetable oil (palm']
    if any(k in recipe_text for k in explicit_palm):
        detected_classes.append('REFINED_PALM_OIL')
        total_penalty += 3.0

    capped_penalty = min(25.0, total_penalty)
    return capped_penalty, detected_classes


def compute_thrs_v3(
    sugar_g: float,
    sat_fat_g: float,
    sodium_mg: float,
    ingredients_text: str,
    is_liquid: bool = False,
    decoded_e_dict: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Computes complete THRS v3 score breakdown for a single product.
    Returns dictionary with all component penalties, total deduction, and final score.
    """
    nutri_res = calc_p_nutrition_v3(sugar_g, sat_fat_g, sodium_mg, is_liquid)
    p_ing, signals = detect_ingredient_penalties_v3(ingredients_text, decoded_e_dict)

    if pd.isna(nutri_res['p_nutrition']):
        return {
            'thrs_v3_score': np.nan,
            'p_nutrition': np.nan,
            'p_sugar': np.nan,
            'p_sat_fat': np.nan,
            'p_sodium': np.nan,
            'p_ingredient': p_ing,
            'p_total': np.nan,
            'detected_signals': signals,
        }

    p_tot = float(nutri_res['p_nutrition']) + float(p_ing)
    v3_score = max(0.0, min(100.0, 100.0 - p_tot))

    return {
        'thrs_v3_score': round(v3_score, 1),
        'p_nutrition': nutri_res['p_nutrition'],
        'p_sugar': nutri_res['p_sugar'],
        'p_sat_fat': nutri_res['p_sat_fat'],
        'p_sodium': nutri_res['p_sodium'],
        'p_ingredient': round(p_ing, 2),
        'p_total': round(p_tot, 2),
        'detected_signals': signals,
    }
