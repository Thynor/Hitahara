# allergen_data.py
# Reference database of allergens and additives, each with a list of
# synonyms / derivative ingredient names that OCR'd labels commonly use.
# This is intentionally simple (dictionary + fuzzy match) rather than a
# heavyweight NLP model — ingredient lists are semi-structured, so this
# approach is fast, explainable, and easy to extend.

ALLERGENS = {
    "milk": {
        "label": "Milk / Dairy",
        "severity": "allergen",
        "synonyms": [
            "milk", "milk powder", "milk solids", "skim milk", "whole milk",
            "casein", "caseinate", "sodium caseinate", "whey", "whey protein",
            "lactose", "butter", "ghee", "cream", "curd", "yogurt", "cheese",
            "milk fat", "buttermilk", "lactalbumin", "lactoglobulin",
        ],
    },
    "eggs": {
        "label": "Eggs",
        "severity": "allergen",
        "synonyms": [
            "egg", "eggs", "egg white", "egg yolk", "albumin", "ovalbumin",
            "egg powder", "dried egg", "mayonnaise", "lysozyme",
        ],
    },
    "peanuts": {
        "label": "Peanuts",
        "severity": "allergen",
        "synonyms": [
            "peanut", "peanuts", "peanut oil", "groundnut", "groundnut oil",
            "arachis oil", "peanut flour", "peanut butter",
        ],
    },
    "tree_nuts": {
        "label": "Tree Nuts",
        "severity": "allergen",
        "synonyms": [
            "almond", "cashew", "walnut", "pistachio", "hazelnut",
            "macadamia", "brazil nut", "pecan", "pine nut", "chestnut",
            "nut paste", "nut oil",
        ],
    },
    "soy": {
        "label": "Soy",
        "severity": "allergen",
        "synonyms": [
            "soy", "soya", "soybean", "soy lecithin", "soy protein",
            "textured vegetable protein", "tvp", "edamame", "tofu",
            "hydrolyzed soy protein",
        ],
    },
    "wheat_gluten": {
        "label": "Wheat / Gluten",
        "severity": "allergen",
        "synonyms": [
            "wheat", "wheat flour", "maida", "gluten", "wheat gluten",
            "vital wheat gluten", "semolina", "durum", "barley", "rye",
            "malt", "malt extract", "wheat starch", "atta",
        ],
    },
    "fish": {
        "label": "Fish",
        "severity": "allergen",
        "synonyms": [
            "fish", "fish oil", "fish extract", "anchovy", "cod", "salmon",
            "tuna", "surimi", "fish sauce", "gelatin (fish)",
        ],
    },
    "shellfish": {
        "label": "Shellfish",
        "severity": "allergen",
        "synonyms": [
            "shrimp", "prawn", "crab", "lobster", "shellfish", "crustacean",
            "oyster", "mussel", "clam", "squid", "octopus",
        ],
    },
    "sesame": {
        "label": "Sesame",
        "severity": "allergen",
        "synonyms": [
            "sesame", "sesame seed", "sesame oil", "tahini", "til",
        ],
    },
    # --- Additives (flagged as "caution", not a true allergen) ---
    "msg": {
        "label": "MSG (flavor enhancer)",
        "severity": "additive",
        "synonyms": [
            "msg", "monosodium glutamate", "e621", "hydrolyzed vegetable protein",
            "yeast extract", "autolyzed yeast",
        ],
    },
    "artificial_color": {
        "label": "Artificial Color",
        "severity": "additive",
        "synonyms": [
            "tartrazine", "e102", "sunset yellow", "e110", "carmoisine",
            "e122", "allura red", "e129", "brilliant blue", "e133",
            "artificial color", "fd&c", "food color",
        ],
    },
    "preservatives": {
        "label": "Preservative",
        "severity": "additive",
        "synonyms": [
            "sodium benzoate", "e211", "potassium sorbate", "e202",
            "sodium nitrite", "e250", "sulphur dioxide", "e220", "bha", "bht",
            "sodium metabisulphite",
        ],
    },
    "artificial_sweetener": {
        "label": "Artificial Sweetener",
        "severity": "additive",
        "synonyms": [
            "aspartame", "e951", "saccharin", "e954", "sucralose", "e955",
            "acesulfame potassium", "e950",
        ],
    },
    "trans_fat": {
        "label": "Trans Fat / Hydrogenated Oil",
        "severity": "additive",
        "synonyms": [
            "hydrogenated oil", "partially hydrogenated", "vanaspati",
            "trans fat", "shortening",
        ],
    },
}

# Flatten into a single lookup list for fuzzy matching:
# [(synonym_text, allergen_key), ...]
def build_synonym_index():
    index = []
    for key, entry in ALLERGENS.items():
        for syn in entry["synonyms"]:
            index.append((syn.lower(), key))
    return index


SYNONYM_INDEX = build_synonym_index()
