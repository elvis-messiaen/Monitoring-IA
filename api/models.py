from pydantic import BaseModel, field_validator
from typing import List

class Passenger(BaseModel):
    Sex: str
    Fare: float

    @field_validator("Sex")
    def validate_sex(cls, v):
        if v.upper() not in ("M", "F"):
            raise ValueError("Sex must be 'M' or 'F'")
        return v.upper()

class Passengers(BaseModel):
    passengers: List[Passenger]