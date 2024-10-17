# battlefield_models.py
from pydantic import BaseModel
from typing import List

# Represents a tile on the battlefield, with position and type.
class Tile(BaseModel):
    x: int  # X-coordinate of the tile.
    y: int  # Y-coordinate of the tile.
    type: str  # Type of the tile (e.g., 'open', 'cover', 'elevation').
    elevation: int = 0  # Elevation level of the tile.

# Represents the entire battlefield, composed of multiple tiles.
class Battlefield(BaseModel):
    width: int  # Width of the battlefield.
    height: int  # Height of the battlefield.
    tiles: List[Tile]  # List of tiles representing the battlefield.