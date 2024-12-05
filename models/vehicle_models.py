from pydantic import BaseModel, Field
from typing import Optional, Annotated


class Vehicle(BaseModel):
    """Represents a vehicle in Necromunda."""
    name: Annotated[str, Field(description="Name of the vehicle")]
    is_wrecked: Annotated[bool, Field(default=False, description="Indicates if the vehicle is wrecked")]
    wounds: Annotated[Optional[int], Field(default=None, description="Number of wounds the vehicle has")]
    toughness: Annotated[Optional[int], Field(default=None, description="Toughness of the vehicle")]
    armor_save: Annotated[Optional[int], Field(default=None, description="Armor save value of the vehicle")]

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Goliath Truck",
                    "is_wrecked": False,
                    "wounds": 3,
                    "toughness": 6,
                    "armor_save": 4
                }
            ]
        }
    }
