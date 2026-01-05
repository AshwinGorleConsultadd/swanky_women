
# manufacturing_logic.py

import json
from llm import analyze_images, llm_structured
from models import (
    GarmentStructureModel, 
    AccessoriesList, AccessoryModel,
    FabricsList, FabricModel,
    SeamsList, SeamModel,
    MeasurementsList, MeasurementModel
)

# =========================================================
# STEP 1 — STRUCTURE EXTRACTION (BINARY DATA)
# =========================================================

def extract_structure_strict(images) -> dict:
    prompt = """
    ROLE: Technical Garment Analyst.
    GOAL: Extract BINARY structural data only.
    
    Analyze the image and determine the following boolean/enum values.
    
    STRICT RULES:
    - garment_type: Choose best fit (outerwear, dress, top, bottom, skirt, pant).
    - length: short, midi, long, cropped, regular.
    - front_closure: Is there a visible opening at the front (buttons, zip, wrap, etc whatever possible and we write in a techapack)?
    - belt_present: Is there a belt or belt loops visible?
    - lapel_present: Are there lapels (like on a blazer or coat)?
    - pockets_present: Are there visible pockets?
    - sleeves: long, short, sleeveless, 3/4.
    - slit_present: Is there a slit?
    
    OUTPUT: JSON only matching GarmentStructureModel.
    """
    
    structure_obj = llm_structured(
        analyze_images(images, prompt),
        GarmentStructureModel
    )
    return structure_obj.model_dump()


# =========================================================
# STEP 2 — ACCESSORIES (LOGIC DERIVED)
# =========================================================

def derive_accessories_strict(structure: dict, images) -> list:
    """
    Derives accessories based on structure + visual confirmation.
    Uses 'Swanky Women Dress' logic: Item, Qty, Material, Dims, Finish, Placement.
    """
    
    prompt = f"""
    ROLE: Manufacturing Engineer.
    GOAL: List 'hard' accessories required to assemble this structure.
    
    STRUCTURE DETECTED:
    {json.dumps(structure, indent=2)}
    
    FEW-SHOT EXAMPLE (Swanky Women Dress):
    Structure: {{ "front_closure": true, "belt_present": false, "pockets_present": false }}
    Output: [
      {{
        "item": "Concealed/Invisible Zipper",
        "quantity": "1 pc",
        "material": "Nylon Coil", 
        "dimensions_mm": "22-24 cm",
        "finish": "Matte",
        "placement": "Center Back"
      }}
    ]

    LOGIC MAP:
    - Front/Back closure = True -> Needs Buttons OR Zipper OR Snaps (Look at image).
    - Belt present = True -> Needs Belt Buckle (if visible) or D-rings.
    - Lapel present = True -> (No accessory, but implies interfacing which is fabric).
    - Sleeves = long -> Might need cuff buttons?
    
    QUANTITY LOGIC:
    - Count visible buttons.
    - If unknown, default to 1 for zipper, 1 for buckle.
    
    STRICT EXCLUSIONS:
    - NO Fabrics (Shell, Lining).
    - NO Interfacing here (that goes to fabrics).
    - NO Thread.
    - NO Jewelry (Earrings, Necklaces, Bracelets) - these are styling, NOT part of the garment BOM.
    - NO Shoes, Bags, or Human accessories.
    - ONLY items physically attached to the garment during manufacturing.
    
    RETURN: JSON list of AccessoryModel.
    """
    
    result = llm_structured(
        analyze_images(images, prompt),
        AccessoriesList
    )
    
    accessories = result.model_dump()['accessories']
    
    # Post-processing to fill the HTML-safe fields for legacy compatibility
    for acc in accessories:
        acc['description'] = f"{acc['item']} ({acc['dimensions_mm']})"
        acc['qty'] = acc['quantity']
        acc['color'] = "Match Shell" 
        acc['position'] = acc['placement']
        
    return accessories


# =========================================================
# STEP 3 — FABRICS (CUTTABLE ONLY)
# =========================================================

def derive_fabrics_strict(structure: dict, images, context_text: str) -> list:
    prompt = f"""
    ROLE: Fabric Cutter.
    GOAL: List all CUTTABLE materials.
    
    CONTEXT: {context_text}
    STRUCTURE: {json.dumps(structure)}
    
    FEW-SHOT EXAMPLE (Swanky Women Dress):
    Output: [
      {{
        "usage": "Shell Fabric",
        "composition": "90% Cotton / 10% Spandex",
        "construction": "Woven",
        "weight_gsm": "220-260 GSM",
        "finish": "Matte surface",
        "color_pantone": "Black",
        "care": "Dry Clean"
      }}
    ]

    VALID USAGE TYPES (STRICT):
    - "Shell"
    - "Lining" (Only if visible or standard for this outerwear type)
    - "Pocketing" (If pockets_present=True)
    - "Belt Fabric" (If belt_present=True)
    - "Fusible Interfacing" (If lapel_present=True or needed for structure)
    
    INVALID:
    - Thread, Buttons, Zippers, Elastic (unless wide waistband fabric).
    
    OUTPUT: JSON list of FabricModel.
    """
    
    result = llm_structured(
        analyze_images(images, prompt),
        FabricsList
    )
    fabrics = result.model_dump()['fabrics']
    
    # Post-processing for legacy fields
    for f in fabrics:
        f['description'] = f"{f['usage']}, {f['composition']}, {f['weight_gsm']}, {f['construction']}, {f['finish']}"
        f['color'] = f['color_pantone']
        f['position'] = f['usage']
        
    return fabrics


# =========================================================
# STEP 4 — SEAMS (FUNCTION BASED)
# =========================================================

def derive_seams_strict(structure: dict, images) -> list:
    prompt = f"""
    ROLE: Garment Technician.
    GOAL: Define construction seams based on function.
    
    STRUCTURE: {json.dumps(structure)}
    
    FEW-SHOT EXAMPLE (Swanky Women Dress):
    Output: [
      {{
        "seam_location": "Shoulder Seam",
        "seam_function": "Load bearing",
        "seam_type": "Superimposed Seam",
        "stitch_type": "Lockstitch (301)",
        "allowance_mm": "10",
        "machine": "Single needle machine"
      }},
      {{
        "seam_location": "Side Seam",
        "seam_function": "Structural",
        "seam_type": "Superimposed Seam",
        "stitch_type": "Lockstitch (301)",
        "allowance_mm": "6",
        "machine": "Single needle machine"
      }},
      {{
         "seam_location": "Hem",
         "seam_function": "Finish",
         "seam_type": "Edge Finish",
         "stitch_type": "Lockstitch (301)",
         "allowance_mm": "10",
         "machine": "Lockstitch Machine"
      }}
    ]

    LOGIC:
    - Shoulder -> Load bearing -> Lockstitch or Chainstitch with tape?
    - Side seam -> Structural -> Safety Stitch or 5-thread Overlock?
    - Hem -> Finish -> Blind stitch or Topstitch?
    
    OUTPUT: JSON list of SeamModel.
    """
    
    result = llm_structured(
        analyze_images(images, prompt),
        SeamsList
    )
    
    seams = result.model_dump()['seams']
    
    # Post-processing for legacy fields
    for s in seams:
        s['type'] = s['seam_type']
        s['symbol'] = "SSa-1" # Generic placeholder
        s['allowance'] = s['allowance_mm']
        s['description'] = s['seam_location']
        s['stitch_symbol'] = s['stitch_type'].split('(')[-1].replace(')', '') if '(' in s['stitch_type'] else "301"
        s['stitch_size'] = "3 mm"
        
    return seams


# =========================================================
# STEP 5 — MEASUREMENTS (POMs)
# =========================================================

def derive_measurements_strict(structure: dict, images) -> list:
    prompt = f"""
    ROLE: Pattern Maker.
    GOAL: List critical Point of Measures (POMs).
    
    STRUCTURE: {json.dumps(structure)}
    
    FEW-SHOT EXAMPLE (Swanky Women Dress):
    [
      {{ "pom_name": "Chest", "code": "A", "description": "1 inch below armhole", "sample_size_value": 84, "tolerance_cm": "+/- 1.27" }},
      {{ "pom_name": "Waist", "code": "B", "description": "Narrowest part", "sample_size_value": 68, "tolerance_cm": "+/- 1.27" }},
      {{ "pom_name": "Shoulder to Shoulder", "code": "C", "description": "Across back", "sample_size_value": 37, "tolerance_cm": "+/- 0.64" }},
      {{ "pom_name": "Dress Length (back)", "code": "D", "description": "Center back length", "sample_size_value": 135, "tolerance_cm": "+/- 0.67" }}
    ]

    REQUIREMENTS:
    - Minimum 15 POMs for outerwear/complex garments.
    - Must include: Bust, Waist, sweep/hem, shoulder, armhole, sleeve length, bicep, cuff, neck width, front length, back length.
    
    OUTPUT: JSON list of MeasurementModel.
    """
    
    result = llm_structured(
        analyze_images(images, prompt),
        MeasurementsList
    )
    
    measurements = result.model_dump()['measurements']
    
    # Legacy fields
    for m in measurements:
        m['point_of_measurement'] = m['pom_name']
        m['measurement_cm'] = m['sample_size_value']
        
    return measurements


# =========================================================
# STEP 6 — WASH & CARE (DERIVED)
# =========================================================

def derive_care_instructions(fabrics: list) -> dict:
    # Logic: Look at Shell composition.
    # Default to "Dry Clean Only" for complex outerwear/wool.
    
    shell = next((f for f in fabrics if f['usage'] == 'Shell'), None)
    
    if not shell:
        return {
            "washing_instructions": "Dry Clean Only",
            "composition": "Refer fabric composition"
        }
        
    comp = shell['composition'].lower()
    
    is_delicate = any(x in comp for x in ['wool', 'silk', 'cashmere', 'viscose', 'rayon', 'linen'])
    
    instructions = {
        "composition": shell['composition'],
        "washing_instructions": "Dry Clean Only" if is_delicate else "Machine Wash Cold",
        "bleaching": "Do Not Bleach",
        "drying_instructions": "Line Dry can be done" if is_delicate else "Tumble Dry Low",
        "ironing_instructions": "Cool Iron",
        "dry_cleaning": {
             "line_1": "Dry Clean with Any Solvent",
             "line_2": "Except Trichloroethylene"
        } if is_delicate else {},
        "label_colors": "Black on White"
    }
    
    return instructions


# =========================================================
# STEP 7 — CROSS-VALIDATION
# =========================================================

def cross_validate(structure, accessories, fabrics, measurements):
    """
    Checks consistency and returns warnings.
    """
    warnings = []
    
    # Check 1: Belt
    if structure.get('belt_present'):
        has_buckle = any('buckle' in a['item'].lower() for a in accessories)
        has_belt_fabric = any(f['usage'] == 'Belt Fabric' for f in fabrics)
        
        if not has_buckle and not has_belt_fabric:
            pass 
        elif not has_belt_fabric:
            warnings.append("Structure has Belt, but no 'Belt Fabric' listed.")

    # Check 2: Pockets
    if structure.get('pockets_present'):
        has_pocketing = any(f['usage'] == 'Pocketing' for f in fabrics)
        if not has_pocketing:
            warnings.append("Structure has Pockets, but no 'Pocketing' fabric listed.")
            
    return warnings
