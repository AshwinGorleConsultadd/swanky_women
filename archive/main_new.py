import json
import datetime
from copy import deepcopy

from llm import analyze_images, llm_structured, llm_query
from generate import generatePdf
from utils import extract_clothing_palette

from models import (
    TechPackHeader,
    GarmentColorModel,
    GarmentStructureModel,
    GarmentClassificationModel,
    FabricDecisionModel,
    ConstructionDecisionModel,
    MeasurementDecisionModel,
    FactoryInstructionModel,
    VerificationResult,
    QualityStandardsList,
    SizeChartList
)

# =========================================================
# SAFETY HELPERS
# =========================================================

def ensure_page(master, key):
    master.setdefault(key, {})
    return master[key]

def ensure_page_9_contract(page_9: dict) -> dict:
    page_9.setdefault("wash_label", {})
    page_9.setdefault("care_label", {"image": "assets/care_label.png"})
    page_9.setdefault("care_label_instructions", [])
    page_9.setdefault("other_standards", [])
    return page_9


# =========================================================
# AGENT 0 — COLOR (SINGLE SOURCE OF TRUTH)
# =========================================================

def extract_garment_color(images):
    palette = extract_clothing_palette(images[0])

    prompt = f"""
ROLE: Color Specialist (Tech Pack)

TASK:
- Select the SINGLE dominant garment color
- Ignore lighting/shadows
- Suggest closest Pantone TCX (mark as SUGGESTED)

HEX OPTIONS:
{palette}

OUTPUT JSON ONLY
"""
    return llm_structured(
        analyze_images(images, prompt),
        GarmentColorModel
    ).model_dump()


# =========================================================
# AGENT 1 — VISION (OBSERVE ONLY)
# =========================================================

def vision_agent(images):
    prompt = """
ROLE: Senior Technical Designer (Vision Only)

TASK:
Extract ONLY observable garment facts.

OUTPUT:
- garment_category
- garment_type
- length
- sleeves
- fit_impression
- closure_visibility
- visible_features
- hem_type
- complexity

RULES:
- No fabric assumptions
- No construction assumptions
- No marketing language
"""

    vision_text = analyze_images(images, prompt)

    return {
        "raw_observation": vision_text,
        "structure": llm_structured(vision_text, GarmentStructureModel).model_dump()
    }


# =========================================================
# AGENT 2 — GARMENT CLASSIFICATION
# =========================================================

def garment_identifier_agent(structure):
    prompt = f"""
ROLE: Garment Classification Agent

INPUT:
{json.dumps(structure, indent=2)}

TASK:
Classify garment using decision tree:
Womenswear → Dress → Length / Sleeves / Fit / Complexity

OUTPUT:
- classification
- downstream_implications
- reason
- confidence
"""
    return llm_structured(prompt, GarmentClassificationModel).model_dump()


# =========================================================
# AGENT 3 — FABRIC DECISION (PROPERTIES ONLY)
# =========================================================

def fabric_decision_agent(classification, structure, brand_context):
    prompt = f"""
ROLE: Fabric Decision Agent

INPUTS:
Classification:
{classification}

Structure:
{structure}

Brand Context:
{brand_context}

TASK:
Decide FABRIC PROPERTIES only (no final materials).

OUTPUT:
- stretch_required (none/low/high)
- drape_required (yes/no)
- gsm_range
- fabric_family (woven/knit)
- elastane_range
- reason
- confidence
"""
    return llm_structured(prompt, FabricDecisionModel).model_dump()


# =========================================================
# AGENT 4 — CONSTRUCTION DECISION (NO STITCH CODES)
# =========================================================

def construction_decision_agent(classification, fabric_decision, structure):
    prompt = f"""
ROLE: Construction Decision Agent

INPUTS:
Classification:
{classification}

Fabric Decision:
{fabric_decision}

Structure:
{structure}

TASK:
For each seam zone:
- Identify function
- Stress
- Stretch sensitivity
- Visibility

DO NOT specify stitch codes.

OUTPUT:
- seam_zone
- strategy
- reason
- confidence
"""
    return llm_structured(prompt, ConstructionDecisionModel).model_dump()


# =========================================================
# AGENT 5 — MEASUREMENT DECISION (WHAT TO MEASURE)
# =========================================================

def measurement_decision_agent(classification, sizing):
    prompt = f"""
ROLE: Measurement Planning Agent

INPUTS:
Classification:
{classification}

Sizing:
{sizing}

TASK:
Define WHAT must be measured and tolerance logic.

OUTPUT:
- pom_name
- pom_type (length/circumference)
- tolerance_range
- value_source (fit block / reference / TBD)
- reason
- confidence
"""
    return llm_structured(prompt, MeasurementDecisionModel).model_dump()


# =========================================================
# AGENT 6 — RESOLVER (FACTORY TRANSLATION)
# =========================================================

def resolver_agent(fabric_decision, construction_decisions, measurement_decisions):
    prompt = f"""
ROLE: Factory Translation Agent

INPUTS:
Fabric Decisions:
{fabric_decision}

Construction Decisions:
{construction_decisions}

Measurement Decisions:
{measurement_decisions}

TASK:
Translate decisions into factory-ready instructions.

RULES:
- Safest default if multiple options
- If confidence < 0.7 → mark requires_confirmation = true
- Every output MUST include justification

OUTPUT:
- fabrics
- seams
- measurements
"""
    return llm_structured(prompt, FactoryInstructionModel).model_dump()


# =========================================================
# AGENT 7 — VERIFIER (VETO POWER)
# =========================================================

def verifier_agent(factory_output, full_context):
    prompt = f"""
ROLE: Independent Technical Auditor

CONTEXT:
{json.dumps(full_context, indent=2)}

OUTPUT TO VERIFY:
{json.dumps(factory_output, indent=2)}

TASK:
- Validate correctness
- Identify assumptions
- Flag risks

OUTPUT:
- valid
- issues
- confidence
- fix_suggestions
"""
    return llm_structured(prompt, VerificationResult).model_dump()


# =========================================================
# MAIN PIPELINE
# =========================================================

def generate_techpack(images, context):

    # 1. Load master
    with open("data/master.json") as f:
        master = deepcopy(json.load(f))
    for i in range(1, 10):
        ensure_page(master, f"page_{i}")

    # 2. Header
    header = llm_structured(
        f"Generate tech pack header.\nContext:\n{context}",
        TechPackHeader
    ).model_dump()
    master["header"] = header

    # 3. Page 1
    master["page_1"].update({
        "garment_front_view_url": images[0],
        "garment_back_view_url": images[1] if len(images) > 1 else images[0],
        "style_number": header["style_name"],
        "date": header["date"],
        "brand_name": header["brand"],
        "collection_name": header["collection"],
        "season": header["season"],
    })

    # 4. Color
    color = extract_garment_color(images)
    master["page_2"].update(color)

    # 5. AGENTS
    vision = vision_agent(images)
    classification = garment_identifier_agent(vision["structure"])
    fabric_decision = fabric_decision_agent(classification, vision["structure"], context)
    construction_decisions = construction_decision_agent(classification, fabric_decision, vision["structure"])
    measurement_decisions = measurement_decision_agent(classification, {
        "market": "US Women",
        "sample_size": "S"
    })

    # 6. Resolver
    factory_output = resolver_agent(
        fabric_decision,
        construction_decisions,
        measurement_decisions
    )

    # 7. Verification
    verification = verifier_agent(factory_output, {
        "vision": vision,
        "classification": classification,
        "fabric": fabric_decision,
        "construction": construction_decisions,
        "measurements": measurement_decisions
    })

    if not verification["valid"]:
        print("⚠️ VERIFICATION FAILED:", verification)

    # 8. Fill pages
    master["page_4"]["accessories"] = factory_output.get("accessories", [])
    master["page_5"]["seams"] = factory_output.get("seams", [])
    master["page_6"]["measurements"] = factory_output.get("measurements", [])
    master["page_7"]["fabrics"] = factory_output.get("fabrics", [])
    master["page_9"]["wash_label"] = factory_output.get("care", {})
    ensure_page_9_contract(master["page_9"])

    # 9. Save
    with open("data/master_filled.json", "w") as f:
        json.dump(master, f, indent=4)

    return generatePdf()



generate_techpack(["assets/front.png","assets/back.png"],"""- —1. Style details and Season
-   Brand - Grandiose
-   Collection Name - JC & Co
-   Season- Fall/Winter 25
-   Trench Coat- TRC
-   FOR EXAMPLE- The product code BC-A-FA25 refers to the 'Arena' item from the Broadway Collection, released for the Fall 2025 season.
-   use a Abbreviation Full name to designate the techpack, e.g. BC-A-FA25-3PS
-   3PS=3-piece suit
-   SPRING =SP
-   SUMMER=SU
-   FALL=FA
-   WINTER=WI
- 2. Fabric Direction-
-    TRENCH COAT- Gabardine, Wool, Cotton Blends
- 3. Measurements
-    US Women's Size
- 4. Sample Size - Small and Size Range - Small to Extra Large
""")