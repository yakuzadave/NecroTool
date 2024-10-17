from pydantic import BaseModel, Field
from typing import List, Optional

class ArmorModifier(BaseModel):
    modifier_type: str
    value: int
    description: Optional[str] = None

class Armor(BaseModel):
    name: str
    armor_rating: int
    armor_type: str = Field(..., description="Type of armor (e.g., 'Light', 'Heavy')")
    save_modifier: Optional[int] = None
    special_rules: Optional[List[str]] = None
    modifiers: Optional[List[ArmorModifier]] = None
    is_bulk: Optional[bool] = None
    cost: Optional[int] = None
    description: Optional[str] = None
