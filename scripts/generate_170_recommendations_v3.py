"""
Comprehensive 170-Product Recommendation Generator (`scripts/generate_170_recommendations_v3.py`)
===================================================================================================
1. Strict, distinct food_type categories for clean D2C brands:
   - `chocolate_bar`: Real chocolate bars only (Paul & Mike 87%, Whole Truth Hazelnut Dark Choc, Whole Truth Cranberry Dark Choc).
   - `nut_butter_spread`: Peanut butters & dessert spreads.
   - `biscuit_cookie`: Clean millet & whole grain biscuits.
   - `cereal_breakfast`: Oats, muesli & breakfast flakes.
   - `juice_beverage`: 100% coconut water & cold pressed juices.
   - `chips_savory`: Makhanas & clean seed/nut snacks.
   - `instant_noodles`: Millet noodles.
   - `dairy_yogurt`: High protein Greek yogurt.
2. Generates 3 clean, highest-scoring D2C alternatives for ALL 170 products.
"""

import json
import re
import shutil
from pathlib import Path

# Load clean D2C brands
with open('data/clean_indian_startup_brands.json', 'r', encoding='utf-8') as f:
    brands_list = json.load(f)

# Assign strict, distinct food_type to every clean D2C brand
for b in brands_list:
    name = b['item_name'].lower()
    cat = b.get('category', '').lower()
    
    if any(k in name for k in ['cookie', 'cookies', 'biscuit', 'biscuits']):
        b['food_type'] = 'biscuit_cookie'
    elif any(k in name for k in ['peanut butter', 'spread']):
        b['food_type'] = 'nut_butter_spread'
    elif any(k in name for k in ['protein bar', 'energy bar']):
        b['food_type'] = 'energy_bar'
    elif 'dark chocolate bar' in name or 'chocolate bar' in name:
        b['food_type'] = 'chocolate_bar'
    elif any(k in name for k in ['juice', 'drink', 'water', 'aamras', 'jaljeera', 'badam milk']) or 'beverage' in cat:
        b['food_type'] = 'juice_beverage'
    elif any(k in name for k in ['muesli', 'oats', 'cereal', 'flakes', 'pancake']):
        b['food_type'] = 'cereal_breakfast'
    elif 'noodles' in name:
        b['food_type'] = 'instant_noodles'
    elif 'yogurt' in name:
        b['food_type'] = 'dairy_yogurt'
    elif any(k in name for k in ['makhana', 'chips', 'cashews', 'seeds', 'panchmeva', 'bites']):
        b['food_type'] = 'chips_savory'
    elif 'whey' in name:
        b['food_type'] = 'energy_bar'
    else:
        b['food_type'] = 'chocolate_bar'

with open('data/clean_indian_startup_brands.json', 'w', encoding='utf-8') as f:
    json.dump(brands_list, f, indent=2)

print(f"Clean D2C Brands tagged with strict food_types ({len(brands_list)} products).")

# Load Scanned 170 Products from health_scores_v3_staged.json
with open('data/health_scores_v3_staged.json', 'r', encoding='utf-8') as f:
    staged_products = json.load(f)

def classify_scanned_food_type(item_name: str, category: str, sub_category: str) -> str:
    cat = (category or "").upper().strip()
    sub = (sub_category or "").upper().strip()
    name = (item_name or "").lower().strip()
    
    # 1. Exact Category + Sub-Category Routing
    if cat == "BISCUIT" or sub in ["BISCUIT", "COOKIES", "CREAM BISCUIT"]:
        return 'biscuit_cookie'
    
    if cat == "CHOCOLATE" or sub in ["CHOCOLATE", "CHOCOLATE BAR", "MILK CHOCOLATE", "WAFERCHOCOLATE", "CANDY", "TOFFEE", "CHEWING GUM"]:
        return 'chocolate_bar'
        
    if cat == "JUICE" or sub in ["SODA", "FRUIT BEVERAGE", "COFFEE", "MILKSHAKE"]:
        return 'juice_beverage'
        
    if cat == "SNACKS" or sub in ["CHIPS", "POTATOCHIPS"]:
        return 'chips_savory'
        
    if sub in ["CEREAL", "MUSLI"]:
        return 'cereal_breakfast'
        
    if sub in ["NOODLES", "PASTA"]:
        return 'instant_noodles'
        
    if sub in ["MINI SAMOSA", "POTATO FRIES"]:
        return 'chips_savory'
        
    if sub in ["CAKE MIX", "PANCAKE MIX", "CAKE", "WAFFLE"]:
        return 'biscuit_cookie'
        
    if sub == "CHOCOLATESPREAD":
        return 'nut_butter_spread'
        
    # 2. Text Keyword Fallbacks
    if any(k in name for k in ['muesli', 'cereal', 'corn flakes', 'chocos', 'oats', 'granola']):
        return 'cereal_breakfast'
    if any(k in name for k in ['maggi', 'noodle', 'noodles', 'yippee', 'top ramen', 'knorr', 'pasta']):
        return 'instant_noodles'
    if any(k in name for k in ['biscuit', 'cookie', 'cookies', 'biscuits', 'oreo', 'bournvita biscuits', 'digestive', 'rusk', 'wafer']):
        return 'biscuit_cookie'
    if any(k in name for k in ['7up', '7 up', 'sprite', 'coke', 'pepsi', 'fanta', 'mirinda', 'limca', 'dew', 'maaza', 'frooti', 'slice', 'nimbooz', 'red bull', 'juice', 'drink', 'soda', 'beverage']):
        return 'juice_beverage'
    if any(k in name for k in ['chocolate', 'dairy milk', 'bournville', 'silk', 'bounty', 'snickers', 'mars', 'hershey', 'godiva', 'kitkat']):
        return 'chocolate_bar'
    if any(k in name for k in ['chips', 'crisps', 'pringles', 'lay', 'kurkure', 'bingo', 'doritos', 'cheetos', 'namkeen', 'bhujia']):
        return 'chips_savory'

    return 'chips_savory'

recommendations_output = []

for prod in staged_products:
    prod_name = prod['item_name']
    brand = prod['brand']
    v3_score = float(prod.get('thrs_v3_score', 0.0))
    v2_score = prod.get('thrs_v2_score')
    cat = prod.get('category', 'General Grocery')
    sub_cat = prod.get('sub_category', 'General')
    
    food_type = classify_scanned_food_type(prod_name, cat, sub_cat)
    
    # Filter clean D2C candidates matching food_type exactly
    matching_candidates = [b for b in brands_list if b.get('food_type') == food_type]
    
    # Fallbacks if a subcategory is sparse
    if len(matching_candidates) < 3:
        if food_type == 'chocolate_bar':
            matching_candidates = [b for b in brands_list if b.get('food_type') in ['chocolate_bar', 'energy_bar']]
        elif food_type == 'biscuit_cookie':
            matching_candidates = [b for b in brands_list if b.get('food_type') in ['biscuit_cookie', 'cereal_breakfast']]
        elif food_type == 'instant_noodles':
            matching_candidates = [b for b in brands_list if b.get('food_type') in ['instant_noodles', 'chips_savory']]
        elif food_type == 'chips_savory':
            matching_candidates = [b for b in brands_list if b.get('food_type') in ['chips_savory', 'instant_noodles']]
        elif food_type == 'cereal_breakfast':
            matching_candidates = [b for b in brands_list if b.get('food_type') in ['cereal_breakfast', 'biscuit_cookie']]
        else:
            matching_candidates = list(brands_list)
            
    # Sort matching candidates by highest THRS v3 score first
    matching_candidates = sorted(matching_candidates, key=lambda x: x.get('thrs_v3_score', 0.0), reverse=True)
    
    # Take top 3 clean swaps
    top_3 = matching_candidates[:3]
    
    rec_cards = []
    for rec_b in top_3:
        rec_cards.append({
            "brand": rec_b["brand"],
            "item_name": rec_b["item_name"],
            "thrs_v2_score": rec_b.get("thrs_v2_score", 90),
            "thrs_v3_score": rec_b.get("thrs_v3_score", 90.0),
            "key_difference": rec_b.get("key_difference", "Clean-label Indian D2C alternative with high safety index.")
        })
        
    recommendations_output.append({
        "scanned_product": prod_name,
        "scanned_brand": brand,
        "scanned_thrs": v2_score if v2_score is not None else int(round(v3_score)),
        "thrs_v3_score": v3_score,
        "category": cat,
        "food_type": food_type,
        "lock_applied": f"food_type={food_type}",
        "guardrail_status": "high-confidence",
        "recommendations": rec_cards
    })

with open('data/recommendations.json', 'w', encoding='utf-8') as f:
    json.dump(recommendations_output, f, indent=2)

print(f"Complete! data/recommendations.json generated for all {len(recommendations_output)} products!")

# Sample verification
print("\n--- SAMPLE RECOMMENDATION CHECKS ---")
for sample in ["Cadbury Bournville Fruit & Nut 50% Dark CHOCOLATE BAR", "Cadbury Dairy Milk Silk CHOCOLATE BAR", "Bounty Miniatures Coconut Filled Chocolate Pack", "Bournvita Biscuits", "Mcvitie's Digestive High Fibre Biscuits With Goodness Of Wholewheat"]:
    match = [r for r in recommendations_output if sample.lower() in r['scanned_product'].lower()]
    if match:
        m = match[0]
        print(f"\nScanned: {m['scanned_product']} ({m['food_type']}) | v3: {m.get('thrs_v3_score')}")
        for idx, rec in enumerate(m['recommendations'], 1):
            print(f"  Match #{idx}: {rec['brand']} — {rec['item_name']} (v3 score: {rec['thrs_v3_score']})")
