import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

# ---------- Normal text output ----------
def llm_query(query: str):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
    # llm = llm.bind(tools=[{"type": "web_search"}])
    message = HumanMessage(content=f"Answer this question:\n{query}")
    return llm.invoke([message]).content


def llm_with_search(query:str):
    client = OpenAI()

    # prompt = f"""answer the query in concise manner keeping only important information Query: """+query 
    # if len(manuDetails) > 0:
    #     prompt = prompt +  f""" /n currently we have some details about product and there manufacturers might help if nay product in question matches , then search specifci website to that product from below, else search as per question directly"
    # Manufacturer details:
    # {manuDetails}"""
    prompt = ""

    response = client.responses.create(
    model="gpt-4o-mini",
    input=prompt,
    tools=[{"type": "web_search"}],
)
    return response.output_text

# ---------- Structured output with schema ----------
def llm_structured(query: str, output_schema: BaseModel):
    print("query is ", query)
    """
    query: str -> user question
    output_schema: pydantic BaseModel -> defines structured output
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
    
    # Bind the schema to the LLM
    llm_with_structure = llm.with_structured_output(output_schema)
    
    # Invoke the LLM
    return llm_with_structure.invoke(query)


# print("solution is ")
# print(llm_with_search("get me a troubleshooting example from agilant"))
# print(llm_with_search("latest pune news"))


# def llm_snapshot_handler(text,task):
#     if task == "handle_popup":
#         fieled_to_click = llm_structured("help me determine ",pydatnic model)
#     elif task == "fill_something":
#         field_to_fill = llm_structurd("help me ./.. if not avaikable then return scroll",pydatnic model)

from typing import List, Union
from pathlib import Path
import base64

from pydantic import BaseModel
from openai import OpenAI
from models import accoriesModel  # Your Pydantic schema

client = OpenAI(api_key="")


# def encode_image(path: Union[str, Path]) -> str:
#     """Encode an image file as base64 string."""
#     with open(path, "rb") as f:
#         return base64.b64encode(f.read()).decode("utf-8")
# from openai import OpenAI
# from typing import List
# from pydantic import BaseModel

# def analyze_images_with_prompt_and_schema(
#     image_urls: List[str],
#     prompt: str,
#     ImageAnalysisOutput: BaseModel,
# ) :
#     # Build the content list: prompt + all images
#     content = [{"type": "input_text", "text": prompt}]
#     content += [{"type": "input_image", "image_url": url} for url in image_urls]

#     response = client.responses.create(
#         model="gpt-4.1",  # or other vision capable model
#         input=[
#             {
#                 "role": "user",
#                 "content": content,
#             }
#         ],
#         # response_format="json_schema",  # instruct for structured output
#         # schema or other parameters to specify your Pydantic model can be passed here
#     )

#     # The API returns JSON, parse it with your pydantic schema
#     return ImageAnalysisOutput.parse_obj(response.choices[0].message)


# ans = analyze_images_with_prompt_and_schema(["assets/front.png"],"""think as an expert designer and tell acceories required to produce garment
                          
#                           provide - 
#                           {
#                           "description": "Concealed/Invisible Zipper (22–24 cm)",
#             "qty": "1 pc",
#             "color": "Black",
#             "position": "Center Back"
#             }
                          
#                           for exmaple in one of clothing we required
#                           his includes specific details like concealed zippers with color specifications (black) and quantities (1 piece). The BOM covers accessories, threads, and other construction materials, but is separate from fabric details which appear on another page.
                          
                          
#                           give json outpout only""",accoriesModel)

# print(ans)
# ===============================
# Multi-Image Structured Analysis
# ===============================

# 1️⃣ Install first:
# pip install openai pydantic
import base64
from typing import List
from openai import OpenAI



def local_image_to_data_url(path: str) -> str:
    """Convert local image file to a base64 data URL string."""
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    # Adjust mime type here if your images are PNG/JPEG/etc
    return f"data:image/jpeg;base64,{b64}"

def analyze_images(image_paths: List[str], prompt: str):
    # Convert all images to data URLs
    images_content = [
        {
            "type": "input_image",
            "image_url": local_image_to_data_url(path)
        }
        for path in image_paths
    ]

    # Build the input content list: prompt + images
    content = [{"type": "input_text", "text": prompt}] + images_content

    response = client.responses.create(
        model="gpt-4.1",  # or another vision-capable model
        input=[
            {
                "role": "user",
                "content": content,
            }
        ],
        # no response_format param, plain output
    )

    return response

# -------------------------------
# CLI Runner
# -------------------------------

if __name__ == "__main__":
    image_paths = ['assets/front.png', 'assets/back.png']

    PROMPT = """think as an expert designer and tell acceories required to produce garment
                          
                          provide - 
                          {
                          "description": "Concealed/Invisible Zipper (22–24 cm)",
            "qty": "1 pc",
            "color": "Black",
            "position": "Center Back"
            }
                          
                          for exmaple in one of clothing we required
                          his includes specific details like concealed zippers with color specifications (black) and quantities (1 piece). The BOM covers accessories, threads, and other construction materials, but is separate from fabric details which appear on another page.

                          
                          
                          give json outpout only"""

    result = analyze_images(
        image_paths=image_paths,
        prompt=PROMPT,
    )

    print(result.output[0].content[0].text)

    # print("\n=== STRUCTURED OUTPUT ===\n")
    # print(result.model_dump_json(indent=2))
