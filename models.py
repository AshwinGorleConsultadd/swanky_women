from pydantic import BaseModel
from typing import Optional, List

class TechPackHeader(BaseModel):
    date: str
    season: str
    collection: str
    style_name: str
    description: str
    category: str
    brand: str
    size_range: str
    total_order_quantity: Optional[str]
    sample_size_1st: str
    sample_pre_production: Optional[str]
    sample_production: Optional[str]



class accoriesModel(BaseModel):
    description: str
    qty: str
    color: str
    position: str


class SeamsModel(BaseModel):
    type: str
    symbol: str
    allowance: str
    description: str
    stitch_type: str
    stitch_symbol: str
    stitch_size: str
    machine: str


class MeasurementsModel(BaseModel):
    point_of_measurement: str
    code: str
    description: str
    measurement_cm: float
    tolerance_cm: str

class FabricModel(BaseModel):
    description: str
    color: str
    position:str


class FabricQualityStandardModel(BaseModel):
    test: str
    method: str
    requirements: str
    comments: str


class SizeChartModel(BaseModel):
    pom: str
    m: float
    l: float
    xl: float


class Page2DataModel(BaseModel):
    color: str
    fabrics: Optional[str] = ""
    details: Optional[str] = ""

class AccessoriesList(BaseModel):
    accessories: List[accoriesModel]

class SeamsList(BaseModel):
    seams: List[SeamsModel]

class MeasurementsList(BaseModel):
    measurements: List[MeasurementsModel]

class FabricsList(BaseModel):
    fabrics: List[FabricModel]

class QualityStandardsList(BaseModel):
    quality_standards: List[FabricQualityStandardModel]

class SizeChartList(BaseModel):
    size_chart: List[SizeChartModel]