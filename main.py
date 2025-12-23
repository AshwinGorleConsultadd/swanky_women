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
from generate import generatePdf
import json
from typing import Type
from pydantic import BaseModel, ValidationError

def extract_json_from_string(
    s: str,
    model: Type[BaseModel],
) -> dict:
    start = s.find('{')
    end = s.rfind('}')

    if start == -1 or end == -1 or start > end:
        raise ValueError("No valid JSON object found in the string.")

    json_str = s[start:end + 1]
    data = json.loads(json_str)

    if not isinstance(data, dict):
        raise ValueError("Extracted JSON is not an object.")

    try:
        # Pydantic v2
        if hasattr(model, "model_validate"):
            model.model_validate(data)
        else:  # Pydantic v1
            model.parse_obj(data)
    except ValidationError as e:
        raise ValueError(f"JSON does not match {model.__name__} schema") from e

    return data



def generate_techpack(input_images,input_context):
    # load master template (note: folder is lowercase 'data')
    with open("data/master.json") as f:
        master_json = json.load(f)

    # filling header
    header_filler_prompt = f"""
    You are an expert fashion tech pack designer. Based on the following input context, fill in the tech pack header details in JSON format.
    Input strict Context: {input_context}

    keep size in charcaters like small is s and medium is m for writing.

    if input context doesn't have any info either keep it blank or if its general info then fill it accordingly.
    date is : {datetime.datetime.now().strftime("%d/%m/%Y")}"""
    tech_pack_header = llm_structured(header_filler_prompt, TechPackHeader)
    # normalize header to a dict and store
    try:
        header_dict = tech_pack_header.model_dump()
    except Exception:
        # if llm_structured returned a plain dict
        header_dict = tech_pack_header if isinstance(tech_pack_header, dict) else {}
    master_json['header'] = header_dict

    
    # filling page 1
    page_1 = master_json['page_1']
    # assign images from input_images (expecting [front, back]) and header values
    if input_images and len(input_images) > 0:
        master_json['page_1']['garment_front_view_url'] = input_images[0]
    if input_images and len(input_images) > 1:
        master_json['page_1']['garment_back_view_url'] = input_images[1]

    master_json['page_1']['style_number'] = header_dict.get('style_name', master_json['page_1'].get('style_number', ''))
    master_json['page_1']['date'] = header_dict.get('date', master_json['page_1'].get('date', ''))
    master_json['page_1']['season'] = header_dict.get('season', master_json['page_1'].get('season', ''))
    master_json['page_1']['brand_name']  = header_dict.get('brand', master_json['page_1'].get('brand_name', ''))
    master_json['page_1']['collection_name'] = header_dict.get('collection', master_json['page_1'].get('collection_name', ''))


    # filling page 2

    master_json['page_2']['front_image_url'] = "assets/front.png"
    master_json['page_2']['back_image_url'] = "assets/back.png"
    master_json['page_2']['detail_image_1_url'] = "assets/p-1.png"
    master_json['page_2']['detail_image_2_url'] = "assets/p-2.png"
    master_json['page_2']['detail_image_3_url'] = "assets/p1.png"
    master_json['page_2']['detail_image_4_url'] = "assets/p2.png"

    page2Details = analyze_images(input_images,f"""You are an expert fashion tech pack designer. Based on the following input context, provide detailed garment description in JSON format.
    Input Context: {input_context}

    help me generate 
    {Page2DataModel}

    what is the pantone color for the garment? give only pantone color as output in one word as color name, nothing else
    
    and detail description of garment in detail field
    
    for example
    color:Black
    DETAILS
Silhouette: Body-hugging fit at the top, flowing into
an A-line skirt with asymmetrical hem
Sleeves: Full-length fitted sleeves with clean hems
Other Features:
High turtleneck collar, close-fitting
Thigh-high front slit on the left side
Side-gathered ruched detail at the left waist""")

    print("we gt ", page2Details)
    
    # try to extract JSON from LLM output, be resilient to formats
    try:
        if isinstance(page2Details, str):
            page2Details = extract_json_from_string(page2Details, Page2DataModel)
    except Exception as e:
        page2Details = llm_structured(page2Details, Page2DataModel)
        if hasattr(page2Details, 'model_dump'):
            page2Details = page2Details.model_dump()
        else:
            page2Details = {}
    # merge any returned values into page_2
    if isinstance(page2Details, dict):
        master_json['page_2'].update(page2Details)

    # filling page 3
    master_json['page_3']['technical_sketch_img'] = "assets/labelled.png"

    # page 4
    accessories_prompt = f"""Task: Generate a comprehensive Bill of Materials (BOM) for Accessories/Trims in JSON format for the attached style.

Contextual Inputs: * Brand & Style: Brand is "Grandiose". The style is a "Trench Coat - TRC" from the "JC & Co" Collection for "Fall/Winter 25". * Fabric: The garment is constructed from "Gabardine, Wool, or Cotton Blends". * Size Range: S–XL.
{input_context}



Instructional Constraints (The "Think" Step):

Visual Analysis vs. Text: Carefully look at the front and back images. Note the wrap-style closure and lack of external buttons. Infer the need for internal closures (like snaps or a jigger button) to maintain the wrap shape, even if not explicitly listed in the brief. 2. Structural Inference: Based on the "Gabardine/Wool" fabric  and the sharp shoulder lines in the image, include structural trims like "Shoulder Pads" and "Mid-weight Fusible Interfacing." 3. Sustainability Logic: Use the "100% recycled polyester core spun sewing thread" requirement mentioned in the brand's technical standards. 4. Standard Requirements: Include mandatory labels (Main, Size, Care) and a "Hanger Loop," which is essential for heavy trench coats (Style TRC).


Output Format: Provide ONLY a JSON object with a single key 'accessories' containing a list of objects.
output : {AccessoriesList}

description refers to item name"""
    accessories = analyze_images(
        image_paths=input_images,
        prompt=accessories_prompt
    )
    # robust parse fallback
    try:
        if isinstance(accessories, str):
            accessories_data = extract_json_from_string(accessories, AccessoriesList)
            accessories = accessories_data.get('accessories', [])
    except Exception as e:
        accessories_wrapper = llm_structured(accessories, AccessoriesList)
        if hasattr(accessories_wrapper, 'model_dump'):
             accessories = accessories_wrapper.model_dump().get('accessories', [])
        else:
             accessories = []

    master_json['page_4']['accessories'] = accessories


    # page 5
    seams_prompt = f"""

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
Tolerance Logic: Assign appropriate Seam Allowances ($SA$). For example, use $6\text8\text$ for overlocked seams and $10\text12mm$ for zipper insertions or turned hems.
Required Output Fields:seam_type: (e.g., Superimposed Seam)seam_symbol: (e.g., SSa-1)seam_allowance_mm: (Number value)position: (e.g., Side Seams)stitch_type: (e.g., 4-Thread Overlock)stitch_symbol: (e.g., 514)stitch_size: (e.g., $3\textmm$ or $10\text12\text SPI$)machine_type: (e.g., Overlock Machine)


output formate:{SeamsList}
"""
    
    seams = analyze_images(
        image_paths=input_images,
        prompt=seams_prompt
    )
    try:
        if isinstance(seams, str):
            seams_data = extract_json_from_string(seams, SeamsList)
            seams = seams_data.get('seams', [])
    except Exception as e:
        seams_wrapper = llm_structured(seams, SeamsList)
        if hasattr(seams_wrapper, 'model_dump'):
            seams = seams_wrapper.model_dump().get('seams', [])
        else:
            seams = []

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

tolerance_plus_minus: (e.g., 1.27)

outputformate:{MeasurementsList}"""
    
    measurements = analyze_images(
        image_paths=input_images,
        prompt=measurements_prompt
    )

    try:
        if isinstance(measurements, str):
            measurements_data = extract_json_from_string(measurements, MeasurementsList)
            measurements = measurements_data.get('measurements', [])
    except Exception as e:
        measurements_wrapper = llm_structured(measurements, MeasurementsList)
        if hasattr(measurements_wrapper, 'model_dump'):
             measurements = measurements_wrapper.model_dump().get('measurements', [])
        else:
             measurements = []

    master_json['page_6']['measurements'] = measurements
    master_json['page_6']['measurement_image_url'] = "assets/ab-label.png"
    

    # page 7 

    color = master_json['page_2']['color']

    fabrics_prompt = f"""Role: Act as a Senior Textile Sourcing Manager.

Task: Generate a detailed Fabric Bill of Materials (BOM) in JSON format for the attached garment images.

color pantone : {color}

Context Info: -> {input_context}

Visual Observation: [e.g., One-sleeve design, High-neck, Form-fitting silhouette].

Technical Requirements (Think & Infer):

Shell Fabric: Based on the drape in the photo, suggest a specific Composition (e.g., Cotton/Spandex blend for stretch or Gabardine for structure with percentage in it for blend) and a GSM weight appropriate for this type of garment.

Internal Support: This is a high-neck/asymmetrical design. You must include:

Fusible Interfacing: Specify type and position for the collar and zipper area.

Clear Elastic / Stay Tape: Specify placement on the asymmetrical shoulder seam to prevent sagging.

Dye & Finish: Suggest a finish (e.g., "Matte Soft-touch" or "High-density weave") to match the visual texture in the photo.

JSON Output Format: Provide an object with 'fabrics' key containing list: {FabricsList}"""

    fabrics = analyze_images(
        image_paths=input_images,
        prompt=fabrics_prompt
    )
    try:
        if isinstance(fabrics, str):
            fabrics_data = extract_json_from_string(fabrics, FabricsList)
            fabrics = fabrics_data.get('fabrics', [])
    except Exception as e:
        fabrics_wrapper = llm_structured(fabrics, FabricsList)
        if hasattr(fabrics_wrapper, 'model_dump'):
            fabrics = fabrics_wrapper.model_dump().get('fabrics', [])
        else:
            fabrics = []
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
    # Note: Prompt mentions Array of objects, but we want to wrap it in 'quality_standards' key implicitly for model match, OR update prompt to ask for object.
    # Updating prompt to ask for object using the schema model hint.
    quality_prompt += f"\nOutput using strict JSON schema: {QualityStandardsList}"

    quality_standards = analyze_images(
        image_paths=input_images,
        prompt=quality_prompt
    )
    try:
        if isinstance(quality_standards, str):
            qs_data = extract_json_from_string(quality_standards, QualityStandardsList)
            quality_standards = qs_data.get('quality_standards', [])
    except Exception as e:
        qs_wrapper = llm_structured(quality_standards, QualityStandardsList)
        if hasattr(qs_wrapper, 'model_dump'):
            quality_standards = qs_wrapper.model_dump().get('quality_standards', [])
        else:
            quality_standards = []
    master_json['page_7']['quality_standards'] = quality_standards



    # page 8 - meaurements
    measurement_decided = measurements
    

    size_chart = analyze_images(input_images,
        f"""Based on the following measurement specifications for size S, generate a complete Size Chart for sizes M, L, and XL using standard industry grading rules for women's stretch-woven or knit wear (e.g., +4cm or +5cm circumference jump per size)
         System Role: Act as a Senior Apparel Pattern Technologist and Grading Specialist.
         Task: Generate a graded "Size Chart" in JSON format based on a provided base size.
         Inputs Provided:Garment Image: [Attach Image]
         Base Size Data (Size S):  {measurement_decided}
         context : {input_context}
         clothes detailed desc = {master_json['page_2']['details']}
         Instructional Logic (The "Think" Step):Identify Fabric Type: Based on the fabric description (e.g., "90% Cotton / 10% Spandex"), 
         determine the appropriate "Grading Jump."Logic: For knits, use a $4\text cm$ jump for circumference. For heavy woven outerwear, use a $5\text--6\text cm$ jump.
         Calculate Length Grading: Grade vertical lengths (Total Length, Sleeve Length) at a standard interval (e.g., $1.5\\text--2\\text cm$ per size) to maintain the silhouette's proportion.
         Proportional Shoulder Grading: Check the image—if it’s a tailored shoulder, grade by $1\textcm$ increments. If it’s a raglan/drop shoulder, grade by $1.5\textcm$.
         Consistency Check: Ensure the "Hips" always maintain a proportional ratio to the "Waist" across all sizes.
         Output Specification:Return a JSON array called size_chart where each object contains:pom (Point of Measurement), s (Base), m, l, and xl.
          
            Provide the output in JSON format following the SizeChartModel.
            {SizeChartList}

""")
    try:
        if isinstance(size_chart, str):
            sc_data = extract_json_from_string(size_chart, SizeChartList)
            size_chart = sc_data.get('size_chart', [])
    except Exception as e:
        sc_wrapper = llm_structured(size_chart, SizeChartList)
        if hasattr(sc_wrapper, 'model_dump'):
            size_chart = sc_wrapper.model_dump().get('size_chart', [])
        else:
            size_chart = []
    
    master_json['page_8']['size_chart'] = size_chart    


    # page 9 
    page_9_content = {
        "wash_label": {
            "composition": "60% Wool and 40% Cotton",
            "washing_instructions": "Professional Dry Clean Only",
            "bleaching": "Do Not Bleach",
            "drying_instructions": "Do Not Tumble Dry, Flat Dry in Shade",
            "ironing_instructions": "Cool Iron on Reverse using Press Cloth",
            "dry_cleaning": {
                "line_1": "Dry Clean with Any Solvent",
                "line_2": "Except Trichloroethylene"
            },
            "label_colors": "Black on White"
        },
        "care_label": {
            "image": "assets/care_label_grandiose_trc.png"
        },
        "care_label_instructions": [
            "The care label must contain <strong>ISO 3758 care symbols</strong> only.",
            "Care label must be made in 100% recycled polyester.",
            "Care labels must contain origin: Made in India.",
            "Care labels must be given the same size, font and style.",
            "Care instructions should follow <strong>ISO 3758 standard</strong>."
        ],
        "other_standards": [
            {
                "title": "Standard 100 by Oekotex",
                "description": "Ensures all materials, including the mustard dye, are tested for harmful substances."
            },
            {
                "title": "Global Recycled Standard (GRS)",
                "description": "Applies to the recycled polyester used in the care labels and construction threads."
            },
            {
                "title": "Woolmark (Optional)",
                "description": "Assures quality and fiber content for the wool-blend shell fabric."
            }
        ],
        "wash_care_label_img": "assets/label_care.png"
    }

    # Assigning to the master object
    master_json["page_9"] = page_9_content




    # finally write updated master json
    with open("data/master_filled.json","w") as f:
        json.dump(master_json,f,indent=4)

    # generate pdf
    final_pdf_path = generatePdf()
    return final_pdf_path


context = """1. Style details and SeasonBrand: GrandioseCollection Name: JC & CoSeason: Fall/Winter 25Trench Coat: TRCFOR EXAMPLE- The product code BC-A-FA25 refers to the 'Arena' item from the Broadway Collection, released for the Fall 2025 season. use a Abbreviation Full name to designate the techpack, e.g. BC-A-FA25-3PS3PS = 3-piece suitSPRING = SPSUMMER = SUFALL = FAWINTER = WI2. Fabric Direction-TRENCH COAT- Gabardine, Wool, Cotton Blends3. MeasurementsUS Women's SizeCategorySize (US)Numeric Size (US)BustNatural WaistHipTops (in inches)XXS030.523Tops (in inches)XS031.524Tops (in inches)XS232.525Tops (in inches)S433.526Tops (in inches)S634.527Tops (in inches)M835.528Tops (in inches)M1036.529Tops (in inches)L123830.5Bottoms - Regular & ShoXXXS02333Bottoms - Regular & ShoXXS02434Bottoms - Regular & ShoXS02535Bottoms - Regular & ShoXS22636Bottoms - Regular & ShoS42737Bottoms - Regular & ShoS62838Bottoms - Regular & ShoM82939Bottoms - Regular & ShoM103040Bottoms - Regular & ShoL1231.541.5Bottoms - Regular & ShoL143343Bottoms - Regular & ShoXL1635.545.54. Sample Size - Small and Size Range - Small to Extra LargeNow we expect AI to follow our designer's workflow and use these basic inputs to develop a comprehensive tech pack as per our layout.Let me know if you have any questions"""

if __name__ == "__main__":
    generate_techpack(["assets/front.png","assets/back.png"],context)