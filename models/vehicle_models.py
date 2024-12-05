from pydantic import BaseModel, Field
from typing import Optional

class Vehicle(BaseModel):
    name: str = Field(..., description="Name of the vehicle")
    is_wrecked: bool = Field(False, description="Indicates if the vehicle is wrecked")
    wounds: Optional[int] = Field(None, description="Number of wounds the vehicle has")
    toughness: Optional[int] = Field(None, description="Toughness of the vehicle")
    armor_save: Optional[int] = Field(None, description="Armor save value of the vehicle")

    model_config = {
        "arbitrary_types_allowed": True
    }
