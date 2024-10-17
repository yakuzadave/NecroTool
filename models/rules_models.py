# rules_models.py
from pydantic import BaseModel
from typing import List

# Represents a special rule that can apply to models or scenarios, detailing its effects.
class SpecialRule(BaseModel):
    name: str  # Name of the special rule.
    description: str  # Description of the rule.
    effect: str  # Effect or impact of the rule.
