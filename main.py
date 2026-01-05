import json
import datetime
from copy import deepcopy

from llm import analyze_images, llm_structured
from generate import generatePdf
from utils import extract_clothing_palette

from models import (
    TechPackHeader,
    GarmentColorModel,
    GarmentStructureModel,
    Page2DataModel,
    AccessoriesList,
    SeamsList,
    MeasurementsList,
    FabricsList,
    QualityStandardsList,
    SizeChartList
)

# NEW: Import the strict logic
from manufacturing_logic import (
    extract_structure_strict,
    derive_accessories_strict,
    derive_fabrics_strict,
    derive_seams_strict,
    derive_measurements_strict,
    derive_care_instructions,
    cross_validate
)

# =========================================================
# SAFETY HELPERS (HTML CONTRACT)
# =========================================================

def ensure_page(master, key):
    if key not in master or not isinstance(master[key], dict):
        master[key] = {}
    return master[key]


def ensure_page_9_contract(page_9: dict) -> dict:
    page_9.setdefault("wash_label", {})
    page_9.setdefault("care_label", {"image": "assets/care_label.png"})
    page_9.setdefault("care_label_instructions", [])
    page_9.setdefault("other_standards", [])
    page_9.setdefault("wash_care_label_img", "assets/care_label.png")
    return page_9


# =========================================================
# STEP 0.5 — COLOR (SINGLE SOURCE OF TRUTH)
# =========================================================

def extract_garment_color(images):
    palette = extract_clothing_palette(images[0])

    prompt = f"""
    You are a fashion color expert.

    Task:
    - Select the SINGLE main garment color
    - Ignore shadows, folds, lighting
    - Suggest closest Pantone TCX (mark as SUGGESTED)

    Rules:
    - Do NOT guarantee Pantone accuracy
    - Output JSON only

    HEX OPTIONS:
    {palette}
    """

    return llm_structured(
        analyze_images(images, prompt),
        GarmentColorModel
    ).model_dump()


# =========================================================
# MAIN PIPELINE
# =========================================================

def generate_techpack(input_images, input_context):
    
    # -----------------------------------------------------
    # 1. LOAD MASTER TEMPLATE
    # -----------------------------------------------------
    with open("data/master.json") as f:
        base_master = json.load(f)

    master = deepcopy(base_master)
    for i in range(1, 10):
        ensure_page(master, f"page_{i}")

    # -----------------------------------------------------
    # 2. HEADER (STYLE CODE)
    # -----------------------------------------------------
    header_prompt = f"""
    Generate FACTORY tech pack header.

    Few-shot:
    Brand: JC & Co
    Collection: Grandiose
    Garment: Trench Coat
    Season: Fall/Winter 25

    → style_name: JC-GR-TRC-FA25

    Context:
    {input_context}

    Date: {datetime.datetime.now().strftime("%d/%m/%Y")}

    Return JSON only:
    """
    
    # Note: passing type to llm_structured implicitly provides the schema
    header = llm_structured(header_prompt, TechPackHeader).model_dump()

    if not header.get("style_name"):
        raise ValueError("style_name (style code) missing in header")

    master["header"] = header

    # -----------------------------------------------------
    # 3. PAGE 1 — STATIC ASSETS + HEADER INFO
    # -----------------------------------------------------
    p1 = master["page_1"]
    p1["garment_front_view_url"] = input_images[0]
    p1["garment_back_view_url"] = input_images[1] if len(input_images) > 1 else input_images[0]
    p1["style_number"] = header["style_name"]
    p1["date"] = header["date"]
    p1["brand_name"] = header["brand"]
    p1["collection_name"] = header["collection"]
    p1["season"] = header["season"]
    p1.setdefault("brand_logo", "assets/brand_logo.png")

    # -----------------------------------------------------
    # 4. COLOR
    # -----------------------------------------------------
    color = extract_garment_color(input_images)

    # -----------------------------------------------------
    # 5. PAGE 2 — VISUAL DETAILS (LEGACY COMPATIBLE)
    # -----------------------------------------------------
    # Keeping the legacy prompt for "details" text as it's just a text block
    page2_prompt = f"""
    Use EXACT format:
    
    Silhouette:
    Sleeves:
    Closure:
    Other Features:
    
    Rules:
    - Closure = wrap with self-fabric belt if no buttons/zippers visible
    - NEVER mention lining unless visible
    - NO hidden construction
    
    Return JSON only:
    """
    page2 = llm_structured(
        analyze_images(input_images, page2_prompt),
        Page2DataModel
    ).model_dump()

    master["page_2"].update({
        "color_name": color["color_name"],
        "color_hex": color["color_hex"],
        "pantone_tcx": f'{color["pantone_tcx"]} (SUGGESTED)',
        "details": page2["details"],
        # STATIC ASSETS PRESERVED
        "front_image_url": "assets/front.png",
        "back_image_url": "assets/back.png",
        "detail_image_1_url": "assets/p-1.png",
        "detail_image_2_url": "assets/p-2.png",
        "detail_image_3_url": "assets/p1.png",
        "detail_image_4_url": "assets/p2.png",
    })

    # =========================================================
    # CORE: NEW STRICT MANUFACTURING LOGIC
    # =========================================================
    
    # Step 1: Structure Extraction
    structure = extract_structure_strict(input_images)
    print("DEBUG Structure:", structure) # Helpful for server logs

    # Step 2: Accessories (Derived from Structure + Image)
    accessories = derive_accessories_strict(structure, input_images)
    master["page_4"]["accessories"] = accessories

    # Step 3: Fabrics (Cuttable Only)
    fabrics = derive_fabrics_strict(structure, input_images, input_context)
    master["page_7"]["fabrics"] = fabrics

    # Step 4: Seams (Function Based)
    seams = derive_seams_strict(structure, input_images)
    master["page_5"]["seams"] = seams

    # Step 5: Measurements (POMs)
    measurements = derive_measurements_strict(structure, input_images)
    master["page_6"]["measurements"] = measurements
    master["page_6"]["measurement_image_url"] = "assets/ab-label.png"

    # Step 6: Wash & Care (Derived from Fabrics)
    care_info = derive_care_instructions(fabrics)
    
    # Update Page 9 with derived care logic
    master["page_9"]["wash_label"] = care_info # This replaces the static structure partially
    # Ensure contracts for Page 9 exist
    master["page_9"] = ensure_page_9_contract(master["page_9"])
    
    # Step 7: Cross Validation (Logging only for now)
    warnings = cross_validate(structure, accessories, fabrics, measurements)
    if warnings:
        print("CROSS VALIDATION WARNINGS:", warnings)
    
    # -----------------------------------------------------
    # PAGE 7 — QUALITY (Keep logic, just structure update)
    # -----------------------------------------------------
    master["page_7"]["quality_standards"] = llm_structured(
        analyze_images(input_images, f"Return JSON only: {QualityStandardsList}"),
        QualityStandardsList
    ).model_dump()["quality_standards"]

    # -----------------------------------------------------
    # PAGE 8 — SIZE CHART
    # -----------------------------------------------------
    master["page_8"]["size_chart"] = llm_structured(
        analyze_images(input_images, f"Return JSON only: {SizeChartList}"),
        SizeChartList
    ).model_dump()["size_chart"]

    # -----------------------------------------------------
    # SAVE + PDF
    # -----------------------------------------------------
    with open("data/master_filled.json", "w") as f:
        json.dump(master, f, indent=4)

    return generatePdf()
if __name__ == "__main__":
    context = """
Brand: JC & Co
Collection: Grandiose
Season: Fall/Winter 25
Garment: Wrap coat dress
Fabric Direction: Gabardine / Wool blends
Size Range: S–XL
"""

    generate_techpack(
        ["assets/front.png", "assets/back.png"],
        context
    )