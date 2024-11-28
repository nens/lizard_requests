from pydantic import BaseModel
from typing import TypeAlias, Literal

ScaleTypes: TypeAlias = Literal["nominal", "interval", "ordinal", "ratio"]

class Organisation(BaseModel):
    url: str
    uuid: str
    name: str

class Location(BaseModel):
    name: str
    code: str
    organisation: Organisation
    extra_metadata: dict

class ObservationType(BaseModel):
    id: int | None = None
    code: str
    parameter: str
    unit: str | None = None
    scale: ScaleTypes
    description: str | None = None
    reference_frame: str | None = None
    compartement: str | None = None

class Timeseries(BaseModel):
    name: str
    code: str
    description: str = ""
    start: str              # Zulutime YYYY-MM-DDTHH:MM:SSZ
    end: str                # Zulutime YYYY-MM-DDTHH:MM:SSZ
    # value_type: str
    # last_value: str | float | None
    # interval: int
    observation_type: ObservationType
    datasource: str | None = None
    supplier: str | None = None
    supplier_code: str | None = None
    location: Location
    extra_metadata: dict = {}
    

class Event(BaseModel):
    time: str
    value: float | str | bool | None = None
    flag: int | None = None
    validation_code: str = ""
    comment: str = ""
    detection_limit: str = ""
