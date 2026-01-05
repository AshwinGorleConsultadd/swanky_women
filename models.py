from pydantic import BaseModel, Field
from typing import Optional, List, Literal

# ---------------- HEADER ----------------

class TechPackHeader(BaseModel):
    date: str
    season: str
    collection: str
    style_name: str   # STYLE CODE (single source of truth)
    description: str
    category: str
    brand: str
    size_range: str
    total_order_quantity: Optional[str]
    sample_size_1st: str
    sample_pre_production: Optional[str]
    sample_production: Optional[str]


# ---------------- COLOR ----------------

class GarmentColorModel(BaseModel):
    color_name: str
    color_hex: str
    pantone_tcx: str   # MUST be marked SUGGESTED


# ---------------- STRUCTURE (STEP 1) ----------------

class GarmentStructureModel(BaseModel):
    garment_type: Literal["outerwear", "dress", "top", "bottom", "skirt", "pant"] = Field(..., description="General category of the garment")
    length: Literal["short", "midi", "long", "cropped", "regular"]
    front_closure: bool
    belt_present: bool
    lapel_present: bool
    pockets_present: bool
    sleeves: Literal["long", "short", "sleeveless", "3/4"]
    slit_present: bool
    lining_visible: bool # Kept for backward compatibility logic
    visible_buttons: bool # Kept for backward compatibility logic
    visible_zipper: bool # Kept for backward compatibility logic


# ---------------- PAGE 2 ----------------

class Page2DataModel(BaseModel):
    details: str


# ---------------- ACCESSORIES (STEP 2) ----------------

class AccessoryModel(BaseModel):
    item: str                       # Button, Snap, Belt Buckle
    quantity: str                   # "5 pcs", "1.2 m"
    material: str                   # Metal, Plastic, Polyester
    dimensions_mm: str              # e.g. "25mm diameter"
    finish: str                     # Matte, Polished, Antique Brass
    placement: str                  # Front closure, Shoulder
    
    # HTML safe fields for backward compatibility view
    description: Optional[str] = None 
    qty: Optional[str] = None
    color: Optional[str] = None
    position: Optional[str] = None

class AccessoriesList(BaseModel):
    accessories: List[AccessoryModel]


# ---------------- SEAMS (STEP 4) ----------------

class SeamModel(BaseModel):
    seam_location: str              # Side seam, Shoulder, Armhole
    seam_function: Literal["Load bearing", "Structural", "Finish", "Reinforced finish", "Decorative"]
    seam_type: str                  # Superimposed, Lapped, Bound
    stitch_type: str                # Lockstitch (301), Overlock (504)
    allowance_mm: str               # "10mm", "1cm"
    machine: str                    # Single Needle, 5-Thread Overlock
    
    # Mapping to existing JSON format for compatibility
    type: Optional[str] = None
    symbol: Optional[str] = None
    allowance: Optional[str] = None
    title: Optional[str] = None # Some templates might use title/description
    description: Optional[str] = None 
    stitch_symbol: Optional[str] = None
    stitch_size: Optional[str] = None

class SeamsList(BaseModel):
    seams: List[SeamModel]


# ---------------- MEASUREMENTS (STEP 5) ----------------

class MeasurementModel(BaseModel):
    pom_name: str                   # Bust, Sleeve Length
    code: str                       # A, B, C
    description: str                # How to measure
    sample_size_value: float        # Base size value
    tolerance_cm: str               # "+/- 0.5"
    
    # Aliases to match existing JSON if needed, though exact match is better
    point_of_measurement: Optional[str] = None
    measurement_cm: Optional[float] = None

class MeasurementsList(BaseModel):
    measurements: List[MeasurementModel]


# ---------------- FABRICS (STEP 3) ----------------

class FabricModel(BaseModel):
    usage: Literal[
        "Shell",
        "Lining",
        "Pocketing",
        "Belt Fabric",
        "Fusible Interfacing"
    ]
    composition: str                # e.g. "60% Wool / 40% Cotton"
    construction: str               # Woven / Knit / Gabardine
    weight_gsm: str                 # "250 GSM"
    finish: str                     # "Brushed", "None"
    color_pantone: str
    care: str
    
    # HTML safe fields
    description: Optional[str] = None
    color: Optional[str] = None
    position: Optional[str] = None

class FabricsList(BaseModel):
    fabrics: List[FabricModel]


# ---------------- QUALITY ----------------

class FabricQualityStandardModel(BaseModel):
    test: str
    method: str
    requirements: str
    comments: str

class QualityStandardsList(BaseModel):
    quality_standards: List[FabricQualityStandardModel]


# ---------------- SIZE CHART ----------------

class SizeChartModel(BaseModel):
    pom: str
    s: float
    m: float
    l: float
    xl: float

class SizeChartList(BaseModel):
    size_chart: List[SizeChartModel]

# ---------------- LEGACY / EXTRA MODELS ----------------
class accoriesModel(BaseModel):
    description: str
    qty: str
    color: str
    position: str
