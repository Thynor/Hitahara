"""
Personal Allergen Scanner — backend
------------------------------------
FastAPI service that:
  1. Accepts a photo of a food label
  2. Runs OCR to extract raw text
  3. Cleans + splits the text into individual ingredients
  4. Fuzzy-matches each ingredient against a known allergen/additive database
  5. Cross-checks matches against the user's stated allergy profile
  6. Returns a structured, color-codable result

Run locally:
    pip install -r requirements.txt
    # Tesseract OCR engine must also be installed on the OS, e.g.:
    #   Ubuntu/Debian:  sudo apt-get install tesseract-ocr
    #   macOS:          brew install tesseract
    #   Windows:        https://github.com/UB-Mannheim/tesseract/wiki
    uvicorn main:app --reload --port 8000
"""

import io
import re
from typing import List, Optional

import pytesseract
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageOps
from pydantic import BaseModel
from rapidfuzz import fuzz

from allergen_data import ALLERGENS, SYNONYM_INDEX

app = FastAPI(title="Personal Allergen Scanner API")

# Allow the Vite dev server (and any frontend) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FUZZY_MATCH_THRESHOLD = 87  # 0-100, higher = stricter match


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def preprocess_image(raw_bytes: bytes) -> Image.Image:
    """Improve OCR odds on real-world label photos: grayscale + autocontrast."""
    img = Image.open(io.BytesIO(raw_bytes))
    img = ImageOps.exif_transpose(img)  # respect phone camera orientation
    img = img.convert("L")  # grayscale
    img = ImageOps.autocontrast(img)
    return img


def clean_ocr_text(raw_text: str) -> str:
    """Normalize common OCR noise before splitting into ingredients."""
    text = raw_text.replace("\n", " ")
    text = re.sub(r"[^a-zA-Z0-9,;()%.\-\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_ingredients_block(text: str) -> str:
    """
    Try to isolate the actual "Ingredients: ..." section if present,
    otherwise fall back to using the whole cleaned text.
    """
    match = re.search(r"ingredients\s*[:\-]?\s*(.*)", text, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    return text


def split_ingredients(block: str) -> List[str]:
    """Split on common ingredient-list delimiters and drop empties."""
    # Remove parenthetical sub-lists' brackets but keep their content
    block = block.replace("(", ", ").replace(")", ", ")
    parts = re.split(r"[,;]", block)
    cleaned = []
    for p in parts:
        p = p.strip(" .")
        if len(p) >= 2:
            cleaned.append(p)
    return cleaned


def match_ingredient(ingredient: str):
    """
    Fuzzy-match a single ingredient string against the synonym index.
    Returns the best matching allergen key + score, or None.
    """
    best_key = None
    best_score = 0
    ingredient_lower = ingredient.lower()

    for synonym, key in SYNONYM_INDEX:
        score = fuzz.partial_ratio(ingredient_lower, synonym)
        if score > best_score:
            best_score = score
            best_key = key

    if best_score >= FUZZY_MATCH_THRESHOLD:
        return best_key, best_score
    return None, best_score


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ScanResultIngredient(BaseModel):
    text: str
    status: str  # "unsafe" | "caution" | "safe"
    matched_allergen: Optional[str] = None
    matched_label: Optional[str] = None
    match_confidence: Optional[int] = None


class ScanResult(BaseModel):
    verdict: str  # "unsafe" | "caution" | "safe"
    summary: str
    ingredients: List[ScanResultIngredient]
    raw_text: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/allergens")
def list_allergens():
    """Return the full known allergen/additive catalog, for the profile UI."""
    return {
        key: {"label": entry["label"], "severity": entry["severity"]}
        for key, entry in ALLERGENS.items()
    }


@app.post("/api/scan", response_model=ScanResult)
async def scan_label(
    image: UploadFile = File(...),
    allergies: str = Form(...),  # comma-separated allergen keys, e.g. "milk,peanuts"
):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    user_allergies = {a.strip() for a in allergies.split(",") if a.strip()}

    raw_bytes = await image.read()
    try:
        img = preprocess_image(raw_bytes)
        raw_text = pytesseract.image_to_string(img)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OCR failed: {exc}")

    cleaned = clean_ocr_text(raw_text)
    ingredients_block = extract_ingredients_block(cleaned)
    ingredients = split_ingredients(ingredients_block)

    if not ingredients:
        raise HTTPException(
            status_code=422,
            detail="Couldn't read an ingredients list from this photo. Try a clearer, closer shot.",
        )

    results: List[ScanResultIngredient] = []
    has_unsafe = False
    has_caution = False

    for ing in ingredients:
        key, score = match_ingredient(ing)
        if key is None:
            results.append(ScanResultIngredient(text=ing, status="safe"))
            continue

        entry = ALLERGENS[key]
        if key in user_allergies:
            status = "unsafe"
            has_unsafe = True
        elif entry["severity"] == "additive":
            status = "caution"
            has_caution = True
        else:
            # It's a known allergen but not one the user flagged — still
            # worth a caution note rather than a silent pass.
            status = "caution"
            has_caution = True

        results.append(
            ScanResultIngredient(
                text=ing,
                status=status,
                matched_allergen=key,
                matched_label=entry["label"],
                match_confidence=score,
            )
        )

    if has_unsafe:
        verdict = "unsafe"
        summary = "Contains ingredients matching your allergy profile."
    elif has_caution:
        verdict = "caution"
        summary = "No profile allergens found, but some additives or unflagged allergens were detected."
    else:
        verdict = "safe"
        summary = "No allergens or flagged additives detected for your profile."

    return ScanResult(
        verdict=verdict,
        summary=summary,
        ingredients=results,
        raw_text=raw_text.strip(),
    )


@app.get("/")
def root():
    return {"status": "ok", "service": "Personal Allergen Scanner API"}
