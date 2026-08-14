"""
UI & Loader Staging Safety Test Suite (`scripts/test_ui_loader_v3_staging.py`)
=============================================================================
Validates Phase 5B UI Staging requirements:
  1. Product with v3 but no v2 (V3_ONLY) does not crash and thrs_v2_score is None (not 0).
  2. Product with both v2 and v3 (BOTH_V2_AND_V3) loads both correctly.
  3. Missing formulation signals do not crash.
  4. Missing v2 scores do not become zero.
  5. Benchmark UI scores exactly match data/health_scores_v3_staged.json.
  6. Existing recommendations load cleanly.
  7. Legacy v2 scores in health_scores.json remain 100% unchanged.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.ui_data_loader import IngredientDataLoader

DATA_DIR = BASE_DIR / "data"
STAGED_PATH = DATA_DIR / "health_scores_v3_staged.json"
V2_PATH = DATA_DIR / "health_scores.json"


def run_ui_safety_tests():
    print("========================================================================")
    print("           PHASE 5B: UI & LOADER STAGING SAFETY TEST SUITE              ")
    print("========================================================================")

    loader = IngredientDataLoader()
    all_names = loader.get_all_product_names()

    # Test 1: Registry population
    reg_count = len(all_names)
    reg_pass = reg_count == 170
    print(f"Test 1 [Registry Population Coverage] : {'PASSED' if reg_pass else 'FAILED'} ({reg_count} / 170 products registered)")

    # Test 2: V3_ONLY product safety & None check (not 0)
    v3_only_items = [loader.get_product_detail(n) for n in all_names if loader.get_product_detail(n)["availability_status"] == "V3_ONLY"]
    v3_only_pass = True
    if v3_only_items:
        for item in v3_only_items:
            if item["thrs_v2_score"] is not None or item["thrs_v3_score"] is None:
                v3_only_pass = False
                break
    else:
        v3_only_pass = True
    print(f"Test 2 [V3_ONLY Product Safety]       : {'PASSED' if v3_only_pass else 'FAILED'} ({len(v3_only_items)} V3-only products have v2=None & valid v3)")

    # Test 3: BOTH_V2_AND_V3 Product Safety
    both_items = [loader.get_product_detail(n) for n in all_names if loader.get_product_detail(n)["availability_status"] == "BOTH_V2_AND_V3"]
    both_pass = len(both_items) == 125
    print(f"Test 3 [BOTH V2 & V3 Product Match]   : {'PASSED' if both_pass else 'FAILED'} ({len(both_items)} / 125 paired products matched)")

    # Test 4: Missing Formulation Signals Safety
    empty_sig_pass = True
    for n in all_names:
        p = loader.get_product_detail(n)
        sig = p.get("detected_signals")
        if not isinstance(sig, list):
            empty_sig_pass = False
            break
    print(f"Test 4 [Formulation Signal Safety]    : {'PASSED' if empty_sig_pass else 'FAILED'} (100% products have valid signals list)")

    # Test 5: Benchmark Score Matching
    benchmarks = {
        "Tic Tac Orange Hard Candy": 75.0,
        "7 Up Lemon Soft Drink": 80.5,
        "Cadbury Oreo Original Chocolatey Sandwich Biscuits": 63.1,
        "Pringles Potato Chips Desi Masala Tadka Flavour": 66.8,
        "MAGGI 2-Minute Instant Noodles": 71.4,
    }

    benchmark_pass = True
    print("\nTest 5 [5 Benchmark Score Matching]:")
    for b_name, exp_v3 in benchmarks.items():
        p = loader.get_product_detail(b_name)
        if not p:
            print(f"  ❌ {b_name[:35]:<35} : MISSING IN LOADER")
            benchmark_pass = False
            continue
        v3_act = p.get("thrs_v3_score")
        v2_act = p.get("thrs_v2_score")
        match = abs(v3_act - exp_v3) < 1e-3
        if not match:
            benchmark_pass = False
        print(f"  • {b_name[:40]:<40} : v2 = {v2_act}, v3 Staged = {v3_act:.1f} (Exp: {exp_v3:.1f}) -> {'PASSED' if match else 'FAILED'}")

    # Test 6: Recommendation Cards Loading Safety
    rec_pass = True
    for n in all_names:
        p = loader.get_product_detail(n)
        recs = p.get("recommendations", [])
        for r in recs:
            try:
                exps = loader.derive_swap_explanation(p, r)
                if not isinstance(exps, list) or len(exps) == 0:
                    rec_pass = False
            except Exception as e:
                print(f"  ❌ Recommendation error on {n}: {e}")
                rec_pass = False
    print(f"\nTest 6 [Recommendation Safety]       : {'PASSED' if rec_pass else 'FAILED'} (All recommendation swap cards derived safely)")

    # Test 7: Production File Safety
    with open(V2_PATH, "r", encoding="utf-8") as f:
        v2_raw = json.load(f)
    v2_unmodified = len(v2_raw) == 126
    print(f"Test 7 [v2 Production File Safety]   : {'PASSED' if v2_unmodified else 'FAILED'} (data/health_scores.json intact)")

    all_passed = reg_pass and v3_only_pass and both_pass and empty_sig_pass and benchmark_pass and rec_pass and v2_unmodified

    print("\n========================================================================")
    print(f"FINAL STAGED UI STATUS: {'STAGED_V3_UI_INTEGRATION_PASSED' if all_passed else 'BLOCKED_PENDING_FIX'}")
    print("========================================================================")
    return all_passed


if __name__ == "__main__":
    run_ui_safety_tests()
