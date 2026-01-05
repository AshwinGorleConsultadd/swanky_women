import json
import datetime
from typing import Type
from pydantic import BaseModel, ValidationError

from models import *
from llm import analyze_images, llm_structured
from generate import generatePdf
from utils import extract_clothing_palette


# -------------------------------------------------
# UTILITIES
# -------------------------------------------------

def generate_style_code(
    brand_abbr: str,
    collection_abbr: str,
    garment_abbr: str,
    season: str,
    year: str = "25"
) -> str:
    season_map = {
        "Spring": "SP",
        "Summer": "SU",
        "Fall": "FA",
        "Fall/Winter": "FA",
        "Winter": "WI"
    }
    season_code = season_map.get(season, "")
    return f"{brand_abbr}-{collection_abbr}-{garment_abbr}-{season_code}{year}"


def safe_model_dump(obj):
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    return obj if isinstance(obj, dict) else {}


# -------------------------------------------------
# MAIN PIPELINE
# -------------------------------------------------

def generate_techpack(input_images, input_context):

    # -----------------------------
    # LOAD MASTER TEMPLATE
    # -----------------------------
    with open("data/master.json") as f:
        master_json = json.load(f)

    # =================================================
    # PAGE 1 — HEADER (NO LLM GUESSING)
    # =================================================
    header = {
        "brand": "JC & Co",
        "collection": "Grandiose Collection",
        "season": "Fall/Winter 25",
        "garment": "Trench Coat",
        "size_range": "S-XL",
        "sample_size": "S",
        "date": datetime.datetime.now().strftime("%d/%m/%Y")
    }

    header["style_name"] = generate_style_code(
        brand_abbr="JC",
        collection_abbr="GR",
        garment_abbr="TRC",
        season="Fall/Winter",
        year="25"
    )

    master_json["header"] = header

    master_json["page_1"].update({
        "style_number": header["style_name"],
        "date": header["date"],
        "season": header["season"],
        "brand_name": header["brand"],
        "collection_name": header["collection"],
        "garment_front_view_url": input_images[0],
        "garment_back_view_url": input_images[1]
    })

    # =================================================
    # PAGE 2 — DETAILS + COLOR (FEW SHOT)
    # =================================================

    palette = extract_clothing_palette(input_images[0])

    page2_prompt = f"""
SYSTEM ROLE:
You are a Senior Apparel Factory Merchandiser.

CRITICAL RULES:
- Describe ONLY what is visible in the images.
- Do NOT assume construction or trims.
- Follow the exact writing style of the example.

FEW-SHOT EXAMPLE (STYLE REFERENCE):
Silhouette: Body-hugging fit at the top, flowing into an A-line skirt with asymmetrical hem
Sleeves: Full-length fitted sleeves with clean hems
Other Features:
High turtleneck collar, close-fitting
Thigh-high front slit on the left side
Side-gathered ruched detail at the left waist

TASK:
1. Write garment DETAILS in the SAME format:
   - Silhouette:
   - Sleeves:
   - Other Features:
   Use <br> for line breaks.

2. Determine main garment color:
   - Select ONE hex from provided options.
   - Suggest closest Pantone TCX as "SUGGESTED".
   - Do NOT guarantee accuracy.

HEX OPTIONS:
{palette}

OUTPUT:
Strict JSON matching schema {Page2DataModel}
"""

    page2_raw = analyze_images(input_images, page2_prompt)
    page2 = llm_structured(page2_raw, Page2DataModel)
    page2 = safe_model_dump(page2)

    master_json["page_2"].update(page2)

    # =================================================
    # PAGE 4 — ACCESSORIES (FEW SHOT, NO ASSUMPTIONS)
    # =================================================

    accessories_prompt = f"""
SYSTEM ROLE:
You are a Senior Factory Merchandiser.

RULES:
- Accessories = physical non-fabric items.
- Do NOT infer internal components.
- Quantity must be realistic or left blank.

FEW-SHOT ACCESSORIES (REFERENCE):
- Concealed Invisible Zipper (22–24 cm), 1 pc, Center Back
- Brand Label, 1 pc, Inner Back Neck
- Size Label, 1 pc, Below Brand Label
- Care Label, 1 pc, Side Seam
- Thread, 100% Recycled Polyester Core Spun

TASK:
Generate Accessories table ONLY from what is visible in the trench coat images.

OUTPUT:
Strict JSON using schema {AccessoriesList}
"""

    accessories_raw = analyze_images(input_images, accessories_prompt)
    accessories = llm_structured(accessories_raw, AccessoriesList)
    accessories = safe_model_dump(accessories).get("accessories", [])

    master_json["page_4"]["accessories"] = accessories

    # =================================================
    # PAGE 5 — PRODUCT CONSTRUCTION (SAFE OUTERWEAR)
    # =================================================

    seams_prompt = f"""
SYSTEM ROLE:
Senior Apparel Production Engineer.

RULES:
- Garment is woven outerwear (Trench Coat).
- Avoid knit-only stitches unless visible.
- No decorative stitches.

FEW-SHOT (REFERENCE):
Superimposed Seam | Shoulder | Lockstitch 301 | Single Needle Machine
Superimposed Seam | Side Seam | Lockstitch 301 | Single Needle Machine

TASK:
Generate Product Construction table.

OUTPUT:
Strict JSON using schema {SeamsList}
"""

    seams_raw = analyze_images(input_images, seams_prompt)
    seams = llm_structured(seams_raw, SeamsList)
    seams = safe_model_dump(seams).get("seams", [])

    master_json["page_5"]["seams"] = seams

    # =================================================
    # PAGE 6 — MEASUREMENTS (POM, FEW SHOT)
    # =================================================

    measurements_prompt = f"""
SYSTEM ROLE:
Senior Pattern Maker.

RULES:
- Measurements must be manufacturable.
- Include functional POMs (pocket, sleeve opening, lapel, armhole).
- Follow factory measurement language.

FEW-SHOT POM STYLE:
Code: A
Point: Chest
Description: Measure 1\" below armhole across front & back
Tolerance: ±1.27 cm

TASK:
Generate Measurement table.

OUTPUT:
Strict JSON using schema {MeasurementsList}
"""

    measurements_raw = analyze_images(input_images, measurements_prompt)
    measurements = llm_structured(measurements_raw, MeasurementsList)
    measurements = safe_model_dump(measurements).get("measurements", [])

    master_json["page_6"]["measurements"] = measurements

    # =================================================
    # PAGE 7 — FABRICS & QUALITY (NO MIXING)
    # =================================================

    fabrics_prompt = f"""
SYSTEM ROLE:
Senior Textile Sourcing Manager.

RULES:
- Fabrics = cuttable materials ONLY.
- Do NOT include elastic, stay tape, or thread.
- Follow example wording style.

FEW-SHOT FABRIC STYLE:
Shell Fabric, 90% Cotton / 10% Spandex, 220–260 GSM, Matte finish

TASK:
Generate Fabric table.

OUTPUT:
Strict JSON using schema {FabricsList}
"""

    fabrics_raw = analyze_images(input_images, fabrics_prompt)
    fabrics = llm_structured(fabrics_raw, FabricsList)
    fabrics = safe_model_dump(fabrics).get("fabrics", [])

    master_json["page_7"]["fabrics"] = fabrics

    # =================================================
    # QUALITY STANDARDS
    # =================================================

    quality_prompt = f"""
SYSTEM ROLE:
Senior QA Manager.

RULES:
- Use ISO standards only.
- Tests must match outerwear risks.
- Follow Swanky Dress example tone.

TASK:
Generate Quality Standards.

OUTPUT:
Strict JSON using schema {QualityStandardsList}
"""

    quality_raw = analyze_images(input_images, quality_prompt)
    quality = llm_structured(quality_raw, QualityStandardsList)
    quality = safe_model_dump(quality).get("quality_standards", [])

    master_json["page_7"]["quality_standards"] = quality

    # =================================================
    # PAGE 9 — WASH & CARE (DERIVED, NOT GUESSED)
    # =================================================

    master_json["page_9"] = {
        "wash_label": {
            "composition": "As per fabric table",
            "washing_instructions": "Professional Dry Clean Only",
            "bleaching": "Do Not Bleach",
            "drying_instructions": "Do Not Tumble Dry, Flat Dry in Shade",
            "ironing_instructions": "Cool Iron on Reverse",
            "dry_cleaning": {
                "line_1": "Dry Clean with Any Solvent",
                "line_2": "Except Trichloroethylene"
            },
            "label_colors": "Black on White"
        },
        "care_label_instructions": [
            "Follow ISO 3758 care symbols only",
            "Made in India",
            "Uniform label size and font"
        ]
    }

    # =================================================
    # WRITE + PDF
    # =================================================

    with open("data/master_filled.json", "w") as f:
        json.dump(master_json, f, indent=2)

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