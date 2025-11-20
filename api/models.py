from pydantic import BaseModel, field_validator
from typing import List


class Passenger(BaseModel):
    """
    Model representing a single Titanic passenger.

    Attributes:
        Sex: Passenger sex ('M' or 'F')
        Fare: Ticket fare price
    """
    Sex: str
    Fare: float

    @field_validator("Sex")
    def validate_sex(cls, v):
        """
        Validate that sex is either 'M' or 'F'.

        Args:
            v: Sex value to validate

        Returns:
            Uppercased sex value

        Raises:
            ValueError: If sex is not 'M' or 'F'
        """
        if v.upper() not in ("M", "F"):
            raise ValueError("Sex must be 'M' or 'F'")
        return v.upper()


class Passengers(BaseModel):
    """
    Model representing multiple Titanic passengers.

    Attributes:
        passengers: List of Passenger objects
    """
    passengers: List[Passenger]