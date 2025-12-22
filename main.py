from generate import generate_pdf
from llm import llm_query, llm_structured


# Here are the details we designers usually get-
# 1. Style details and Season
#   Brand - Grandiose
#   Collection Name - JC & Co
#   Season- Fall/Winter 25
#   Trench Coat- TRC
#   FOR EXAMPLE- The product code BC-A-FA25 refers to the 'Arena' item from the Broadway Collection, released for the Fall 2025 season.
#   use a Abbreviation Full name to designate the techpack, e.g. BC-A-FA25-3PS
#   3PS=3-piece suit
#   SPRING =SP
#   SUMMER=SU
#   FALL=FA
#   WINTER=WI

# 2. Fabric Direction-
#    TRENCH COAT- Gabardine, Wool, Cotton Blends

# 3. Measurements
#    US Women's Size

# 4. Sample Size - Small and Size Range - Small to Extra Large
# Now we expect AI to follow our designer's workflow and use these basic inputs to develop a comprehensive tech pack as per our layout.
# Let me know if you have any questions
# Regards,


# prompt will have = instruction + input_context + model_to fill + example filled model + web search if required

import json
import datetime
from models import *
from llm import analyze_images, llm_structured

import json

def extract_json_from_string(s: str) -> dict:
    start = s.find('{')
    end = s.rfind('}')
    if start == -1 or end == -1 or start > end:
        raise ValueError("No valid JSON object found in the string.")
    
    json_str = s[start:end+1]
    return json.loads(json_str)


def main(input_images,input_context):
    master_json = json.loads("data/master.json")
    

    # filling header
    header_filler_prompt = f"""
    You are an expert fashion tech pack designer. Based on the following input context, fill in the tech pack header details in JSON format.
    Input Context: {input_context}

    if input context doesn't have any info either keep it blank or if its general info then fill it accordingly.
    date is : {datetime.datetime.now().strftime("%d/%m/%Y")}"""
    tech_pack_header = llm_structured(header_filler_prompt, TechPackHeader)
    master_json['header'] = tech_pack_header.dict()

    
    # filling page 1
    page_1 = master_json['page_1']
    page_1['garment_back_view_url'] = ""
    page_1['garment_front_view_url'] = ""
    page_1['style_number'] = tech_pack_header.style_name
    page_1['date'] = tech_pack_header.date
    page_1['season'] = tech_pack_header.season
    page_1['brand_name']  = tech_pack_header.brand
    page_1['collection_name'] = tech_pack_header.collection


    # filling page 2

    # filling page 3


    # filling page 4
    #   "page_4" : {
    #     "accessories": [
    #         {
    #         "description": "Concealed/Invisible Zipper (22–24 cm)",
    #         "qty": "1 pc",
    #         "color": "Black",
    #         "position": "Center Back"
    #         }
    #     ]
    # },
    page_4 = master_json['page_4']
    accesories = page_4['accessories']


    # call vision 

    accessories_prompt = f"""Task: Generate a comprehensive Bill of Materials (BOM) for Accessories/Trims in JSON format for the attached style.

Contextual Inputs: * Brand & Style: Brand is "Grandiose". The style is a "Trench Coat - TRC" from the "JC & Co" Collection for "Fall/Winter 25". * Fabric: The garment is constructed from "Gabardine, Wool, or Cotton Blends". * Size Range: S–XL.
{input_context}



Instructional Constraints (The "Think" Step):

Visual Analysis vs. Text: Carefully look at the front and back images. Note the wrap-style closure and lack of external buttons. Infer the need for internal closures (like snaps or a jigger button) to maintain the wrap shape, even if not explicitly listed in the brief. 2. Structural Inference: Based on the "Gabardine/Wool" fabric  and the sharp shoulder lines in the image, include structural trims like "Shoulder Pads" and "Mid-weight Fusible Interfacing." 3. Sustainability Logic: Use the "100% recycled polyester core spun sewing thread" requirement mentioned in the brand's technical standards. 4. Standard Requirements: Include mandatory labels (Main, Size, Care) and a "Hanger Loop," which is essential for heavy trench coats (Style TRC).


Output Format: Provide ONLY a JSON array of objects with the following keys: description, qty, color, and position."""
    accessories = analyze_images(
        image_paths=input_images,
        prompt=accessories_prompt
    )
    try:
        accessories = extract_json_from_string(accessories)
    except ValueError as e:
        print(f"Error extracting JSON: {e}")
        accessories = llm_structured(accessories, accoriesModel).dict()

    page_4['accessories'] = accessories


    # page 5
    seams_prompt = """

System Role: Act as a Senior Apparel Production Engineer and Garment Technologist.

Task: Generate a technical "Seam & Stitch Specification" table in JSON format for the provided garment.

Inputs Provided:Images: [Attach Front/Back Images]* 

Context: {input_context}


Instructional Logic (The "Think" Step):Fabric Performance Inference: Determine if the garment is a knit (stretch) or woven.
For a stretch garment like this dress, ensure construction seams (Side Seams, Shoulders) use Overlock (504/514) to prevent thread breakage during wear.
Seam Position Mapping: Analyze the image to identify every junction:Structural: Shoulder, Side, Armhole, Center Back.* 
Functional: Zipper insertion (Center Back).Finishing: Neckline edge, Sleeve Hem, Bottom Hem, High Slit edge.
Technical Standardization: Assign industry-standard ISO symbols:* Seam Symbols: (e.g., SSa, LSb, EFa).
Stitch Symbols: (e.g., 301 Lockstitch, 504 Overlock, 406 Coverstitch).
Tolerance Logic: Assign appropriate Seam Allowances ($SA$). For example, use $6\text{--}8\text{ mm}$ for overlocked seams and $10\text{--}12\text{ mm}$ for zipper insertions or turned hems.
Required Output Fields:seam_type: (e.g., Superimposed Seam)seam_symbol: (e.g., SSa-1)seam_allowance_mm: (Number value)position: (e.g., Side Seams)stitch_type: (e.g., 4-Thread Overlock)stitch_symbol: (e.g., 514)stitch_size: (e.g., $3\text{ mm}$ or $10\text{--}12\text{ SPI}$)machine_type: (e.g., Overlock Machine)
"""
    seams = analyze_images(
        image_paths=input_images,
        prompt=seams_prompt
    )
    try:
        seams = extract_json_from_string(accessories)
    except ValueError as e:
        print(f"Error extracting JSON: {e}")
        seams = llm_structured(seams, SeamsModel).dict()

    master_json['page_5']['seams'] = seams



    # page 6

    measurements_prompt = f"""The Ideal "Measurement & Grading" Prompt
System Role: Act as a Senior Apparel Pattern Maker and Technical Designer.

Task: Generate a complete "Measurement Specification & Grading Table" in JSON format.

Inputs Provided:

Images: [Attach Front/Back Images of the Black Dress]

Context and measurement context: Brand: {input_context}

Instructional Logic (The "Think" Step):

POM Verification: Review the provided "Point of Measurement" (POM) list. Cross-reference with the product image to ensure no critical measurements are missing (e.g., if the dress has a high neck, is the neck width/height included?).

Visual Inference: Look at the "Asymmetrical" nature of the dress. Ensure the description field for measurements like "Slit Length" or "Dress Length" correctly reflects which side (Left or Right) or position (High Point Shoulder) the measurement starts from.

Grading Logic: Based on the Size Range (S–XL), derive the measurements for sizes M, L, and XL using standard industry grading rules for women's stretch-woven or knit wear (e.g., +4cm or +5cm circumference jump per size).

Tolerance Sanity Check: Ensure the tolerance_cm is realistic for the fabric type. (Knit fabrics usually allow for slightly higher tolerances than rigid wovens).

Required Output Fields for each JSON object:

code: (e.g., A, B, C)

point_of_measurement: (e.g., Chest)

description: (How to measure instructions)

size_s: (Base size provided)

size_m: (Derived)

size_l: (Derived)

size_xl: (Derived)

tolerance_plus_minus: (e.g., 1.27)"""
    
    measurements = analyze_images(
        image_paths=input_images,
        prompt=measurements_prompt
    )

    try:
        measurements = extract_json_from_string(measurements)
    except ValueError as e:
        print(f"Error extracting JSON: {e}")
        measurements = llm_structured(measurements, MeasurementsModel).dict()

    master_json['page_6']['measurements'] = measurements
    

    # page 7 

    color = page3.color

    fabrics_prompt = f"""Role: Act as a Senior Textile Sourcing Manager.

Task: Generate a detailed Fabric Bill of Materials (BOM) in JSON format for the attached garment images.

color pantone : {color}

Context Info: -> {input_context}

Visual Observation: [e.g., One-sleeve design, High-neck, Form-fitting silhouette].

Technical Requirements (Think & Infer):

Shell Fabric: Based on the drape in the photo, suggest a specific Composition (e.g., Cotton/Spandex blend for stretch or Gabardine for structure) and a GSM weight appropriate for this type of garment.

Internal Support: This is a high-neck/asymmetrical design. You must include:

Fusible Interfacing: Specify type and position for the collar and zipper area.

Clear Elastic / Stay Tape: Specify placement on the asymmetrical shoulder seam to prevent sagging.

Dye & Finish: Suggest a finish (e.g., "Matte Soft-touch" or "High-density weave") to match the visual texture in the photo.

JSON Output Format: Provide an array with: fabric_type, description (include composition/weight/stretch), color, and position."""

    fabrics = analyze_images(
        image_paths=input_images,
        prompt=fabrics_prompt
    )
    try:
        fabrics = extract_json_from_string(fabrics)
    except ValueError as e:
        print(f"Error extracting JSON: {e}")
        fabrics = llm_structured(fabrics, FabricQualityStandardModel).dict()

    master_json['page_7']['fabrics'] = fabrics


    quality_output_formate = """
{
  "test": "Name of the test",
  "method": "Standard test code (e.g., ISO 105-X12)",
  "requirements": "Numerical or Grade pass/fail criteria",
  "comments": "Contextual reasoning for the garment"
}"""
    quality_prompt = f"""System Role: Act as a Senior Quality Assurance (QA) Manager and Textile Laboratory Specialist.

Task: Generate a list of critical quality tests for a garment's technical pack. Your output must strictly follow the FabricQualityStandardModel (JSON format).

Inputs Provided:

Images: [Attach Garment Images]

Fabric Composition: [e.g., Gabardine Wool Blend / 100% Cotton Jersey]

Garment Category: [e.g., Outerwear - Trench Coat / Activewear - Leggings]

Instructional Logic (The "Think" Step):

Risk Assessment: Identify the primary "failure points" for this specific garment.

Example: For a Trench Coat, water repellency and pilling are critical.

Example: For a Black Dress, color fastness and shrinkage are critical.

Method Selection: Use only industry-recognized testing methods (e.g., ISO, ASTM, or AATCC). Ensure the method matches the global market standard (ISO is preferred for international production).

Setting Requirements: Define pass/fail criteria that are realistic for high-end retail (e.g., Grade 4 for color fastness, ±2% for shrinkage).

Professional Comments: Explain why the test is being performed in the context of this specific garment style.

Output Specification: Return a JSON array of objects following this Pydantic model:

Python
{quality_output_formate}"""

    quality_standards = analyze_images(
        image_paths=input_images,
        prompt=quality_prompt
    )
    try:
        quality_standards = extract_json_from_string(quality_standards)
    except ValueError as e:
        print(f"Error extracting JSON: {e}")
        quality_standards = llm_structured(quality_standards, FabricQualityStandardModel).dict()    
    master_json['page_7']['quality_standards'] = quality_standards



    # page 8 - meaurements
    measurement_decided = measurements
    

    size_chart = analyze_images(
        f"""Based on the following measurement specifications for size S, generate a complete Size Chart for sizes M, L, and XL using standard industry grading rules for women's stretch-woven or knit wear (e.g., +4cm or +5cm circumference jump per size)
         System Role: Act as a Senior Apparel Pattern Technologist and Grading Specialist.
         Task: Generate a graded "Size Chart" in JSON format based on a provided base size.
         Inputs Provided:Garment Image: [Attach Image]
         Base Size Data (Size S):  {measurement_decided}
         context : {input_context}
         clothes detailed desc = {page3.details}
         Instructional Logic (The "Think" Step):Identify Fabric Type: Based on the fabric description (e.g., "90% Cotton / 10% Spandex"), 
         determine the appropriate "Grading Jump."Logic: For knits, use a $4\text cm$ jump for circumference. For heavy woven outerwear, use a $5\text--6\text cm$ jump.
         Calculate Length Grading: Grade vertical lengths (Total Length, Sleeve Length) at a standard interval (e.g., $1.5\\text--2\\text cm$ per size) to maintain the silhouette's proportion.
         Proportional Shoulder Grading: Check the image—if it’s a tailored shoulder, grade by $1\textcm$ increments. If it’s a raglan/drop shoulder, grade by $1.5\textcm$.
         Consistency Check: Ensure the "Hips" always maintain a proportional ratio to the "Waist" across all sizes.
         Output Specification:Return a JSON array called size_chart where each object contains:pom (Point of Measurement), s (Base), m, l, and xl.
          
            Provide the output in JSON format following the SizeChartModel.
            {SizeChartModel}

""")
    try:
        size_chart = extract_json_from_string(size_chart)
    except ValueError as e:
        print(f"Error extracting JSON: {e}")
        size_chart = llm_structured(size_chart, SizeChartModel).dict()
    
    

    # page 9 
    




    # finally write updated master json
    with open("data/master_filled.json","w") as f:
        json.dump(master_json,f,indent=4)

    # generate pdf
    final_pdf_path = generate_pdf()
    return final_pdf_path