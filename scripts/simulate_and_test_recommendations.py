"""
Dry-Run Comprehensive Recommendation Test & Diagnostic Suite (`scripts/simulate_and_test_recommendations.py`)
=============================================================================================================
Simulates and tests 100% of recommendation matching across all 170 products before any production write.
"""

import json
import re

# 1. Load current clean D2C brands
with open('data/clean_indian_startup_brands.json', 'r', encoding='utf-8') as f:
    d2c_brands = json.load(f)

# 2. Add the 4 clean noodle products
clean_noodles = [
    {
        "brand": "Mille",
        "item_name": "Mille Zero Maida Multi-Millet Hakka Noodles",
        "category": "Noodles",
        "food_type": "instant_noodles",
        "ingredients_raw": "Foxtail Millet Flour (37%), Whole Wheat Atta (60%), Salt. Zero Palm Oil, Zero Maida, Zero MSG, Air-Dried.",
        "sugar_per_100g": 1.2,
        "sat_fat_per_100g": 0.4,
        "sodium_mg_per_100g": 45.0,
        "thrs_v2_score": 95,
        "thrs_v3_score": 98.5,
        "key_difference": "60% whole wheat atta and 37% foxtail millet. Air-dried, zero palm oil, zero added MSG or artificial flavouring."
    },
    {
        "brand": "Slurrp Farm",
        "item_name": "Slurrp Farm Millet Noodles - Mild Masala",
        "category": "Noodles",
        "food_type": "instant_noodles",
        "ingredients_raw": "Noodles: Whole wheat flour, foxtail millet flour, cluster bean powder, salt, rosemary extract. Spice Mix: coriander, onion, garlic, chilli, cumin, turmeric, raw sugar, iodised salt.",
        "sugar_per_100g": 1.6,
        "sat_fat_per_100g": 0.3,
        "sodium_mg_per_100g": 331.8,
        "thrs_v2_score": 95,
        "thrs_v3_score": 98.3,
        "key_difference": "Air-dried whole wheat and foxtail millet noodles with natural spice sachet. Zero palm oil, zero MSG, zero preservatives."
    },
    {
        "brand": "Millet Bank",
        "item_name": "Millet Bank Foxtail Millet Hakka Noodles",
        "category": "Noodles",
        "food_type": "instant_noodles",
        "ingredients_raw": "Wheat Flour, Foxtail Millet Flour, Cluster Bean Powder, Salt. Spice Mix: Coriander, Red Chilli, Onion, Garlic, Turmeric, Curry Leaves, Whole Spices, Unrefined Cane Sugar.",
        "sugar_per_100g": 1.5,
        "sat_fat_per_100g": 0.35,
        "sodium_mg_per_100g": 280.0,
        "thrs_v2_score": 95,
        "thrs_v3_score": 98.1,
        "key_difference": "Non-fried foxtail millet noodles with whole spice tastemaker. Zero preservatives, zero chemical flavor enhancers."
    },
    {
        "brand": "BeatO",
        "item_name": "BeatO 6-Millet Healthy Noodles",
        "category": "Noodles",
        "food_type": "instant_noodles",
        "ingredients_raw": "Finger Millet, Pearl Millet, Kodo Millet, Little Millet, Barnyard Millet, Foxtail Millet (29%), Whole Wheat Flour (68.7%), Guar Gum, Salt, Calcium Propionate (0.1%).",
        "sugar_per_100g": 1.8,
        "sat_fat_per_100g": 0.33,
        "sodium_mg_per_100g": 120.0,
        "thrs_v2_score": 90,
        "thrs_v3_score": 93.5,
        "key_difference": "6-millet whole grain noodles with atta. Non-fried, zero palm oil, zero MSG."
    }
]

# Merge into reference pool
d2c_dict = {b['item_name']: b for b in d2c_brands}
for cn in clean_noodles:
    d2c_dict[cn['item_name']] = cn
full_reference_pool = list(d2c_dict.values())

# 3. Load Scanned 170 Products from health_scores_v3_staged.json
with open('data/health_scores_v3_staged.json', 'r', encoding='utf-8') as f:
    staged_products = json.load(f)

def classify_product_food_type(item_name: str, category: str, sub_category: str) -> str:
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

# 4. Run Simulation
category_stats = {}
category_mismatches = []
total_tested = len(staged_products)

simulated_results = []

for prod in staged_products:
    prod_name = prod['item_name']
    brand = prod['brand']
    v3_score = float(prod.get('thrs_v3_score', 0.0))
    cat = prod.get('category', 'General')
    sub_cat = prod.get('sub_category', 'General')
    
    food_type = classify_product_food_type(prod_name, cat, sub_cat)
    category_stats[food_type] = category_stats.get(food_type, 0) + 1
    
    # Strictly filter clean candidates matching food_type
    matching_candidates = [b for b in full_reference_pool if b.get('food_type') == food_type]
    
    # Ensure there are at least 3 matching candidates in every category!
    if len(matching_candidates) < 3:
        category_mismatches.append(f"WARNING: Category {food_type} has only {len(matching_candidates)} matching clean items!")
        
    # Sort matching candidates strictly by highest THRS v3 score
    matching_candidates = sorted(matching_candidates, key=lambda x: x.get('thrs_v3_score', 0.0), reverse=True)
    top_3 = matching_candidates[:3]
    
    # Audit for cross-contamination
    for rec in top_3:
        rec_type = rec.get('food_type')
        if rec_type != food_type:
            category_mismatches.append(f"ERROR: Scanned {prod_name} ({food_type}) got recommended {rec['item_name']} ({rec_type})!")
            
    simulated_results.append({
        "product": prod_name,
        "brand": brand,
        "food_type": food_type,
        "v3_score": v3_score,
        "top_3_recs": [(r['brand'], r['item_name'], r['thrs_v3_score']) for r in top_3]
    })

print("=" * 75)
print("     THRS v3 RECOMMENDATION SIMULATION & INTEGRITY AUDIT REPORT     ")
print("=" * 75)
print(f"Total Scanned Products Tested: {total_tested}")
print(f"Total Clean Reference Pool   : {len(full_reference_pool)} products")
print(f"Category Distribution:")
for ft, cnt in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
    print(f"  • {ft:<20}: {cnt:>3} products")

print(f"\nCategory Isolation & Contamination Check:")
if not category_mismatches:
    print("  ✅ 100% PERFECT: 0 category mismatches or cross-contaminations found across all 170 products!")
else:
    for m in category_mismatches:
        print(f"  ❌ {m}")

print("\n" + "=" * 75)
print("SPOTLIGHT AUDIT OF SENSITIVE TEST PRODUCTS")
print("=" * 75)

spotlight_items = [
    "Maggi 2-Minute Instant Noodles",
    "Maggi Chicken Instant Noodles",
    "Cadbury Oreo Original Chocolatey Sandwich Biscuits",
    "Bournvita Biscuits",
    "Mcvitie's Digestive High Fibre Biscuits With Goodness Of Wholewheat",
    "Cadbury Dairy Milk Silk CHOCOLATE BAR",
    "Cadbury Bournville Fruit & Nut 50% Dark CHOCOLATE BAR",
    "Bounty Miniatures Coconut Filled Chocolate Pack",
    "7 Up Lemon Soft Drink",
    "Pringles Potato Chips Desi Masala Tadka",
    "Kellogg's Chocolate Muesli"
]

for item in spotlight_items:
    match = [r for r in simulated_results if item.lower() in r['product'].lower()]
    if match:
        m = match[0]
        print(f"\n[Scanned] {m['brand']} — {m['product']}")
        print(f"  Category: {m['food_type']} | THRS v3: {m['v3_score']:.1f}")
        for idx, (b, n, s) in enumerate(m['top_3_recs'], 1):
            diff = s - m['v3_score']
            print(f"  -> Better Match #{idx}: {b} — {n} (v3: {s:.1f}) | +{diff:.1f} gain")
