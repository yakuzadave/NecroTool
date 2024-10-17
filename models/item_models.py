# item_models.py
from pydantic import BaseModel, Field
from typing import List, Optional

# Represents a consumable item that can be used during a battle or campaign.
class Consumable(BaseModel):
    name: str = Field(..., description="The name of the consumable item, e.g., Stimm-Slug Stash, Medipack.")
    cost: Optional[int] = Field(None, description="The credit cost of the consumable item.")
    rarity: Optional[str] = Field(None, description="The rarity level of the consumable, used to determine availability in trading post.")
    uses: int = Field(..., ge=1, description="The number of uses the consumable item has.")
    effect: str = Field(..., description="The effect or benefit provided by the consumable item.")
    side_effects: Optional[str] = Field(None, description="Any negative side effects of using the consumable item.")
    description: Optional[str] = Field(None, description="A detailed description of the consumable, including lore or fluff.")

# Represents an equipment item, which may have various effects on gameplay.
class Equipment(BaseModel):
    name: str = Field(..., description="The name of the equipment, e.g., Grapnel Launcher, Photo-Visor.")
    cost: Optional[int] = Field(None, description="The credit cost of the equipment item.")
    rarity: Optional[str] = Field(None, description="The rarity level of the equipment, used to determine availability in trading post.")
    weight: Optional[str] = Field(None, description="The weight category of the equipment, e.g., Light, Medium, Heavy.")
    special_rules: Optional[List[str]] = Field(None, description="Special rules or abilities provided by the equipment.")
    modifiers: Optional[List[str]] = Field(None, description="Stat modifiers provided by the equipment, e.g., +1 to Strength.")
    is_restricted: Optional[bool] = Field(False, description="Indicates whether the equipment is restricted and requires special permission to use.")
    description: Optional[str] = Field(None, description="A detailed description of the equipment, including lore or fluff.")