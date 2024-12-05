from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
from enum import Enum
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel


class TileType(str, Enum):
    OPEN = "open"
    COVER = "cover"
    ELEVATION = "elevation"
    OBSTRUCTION = "obstruction"


class Tile(BaseModel):
    x: int
    y: int
    type: TileType
    elevation: int = 0
    occupier: Optional[str] = None

    def render(self) -> Text:
        """Render the tile as a Rich Text object."""
        char = {
            TileType.OPEN: ".",
            TileType.COVER: "#",
            TileType.ELEVATION: "^",
            TileType.OBSTRUCTION: "X",
        }.get(self.type, "?")
        color = {
            TileType.OPEN: "white",
            TileType.COVER: "green",
            TileType.ELEVATION: "blue",
            TileType.OBSTRUCTION: "red",
        }.get(self.type, "white")
        if self.occupier:
            char = self.occupier[0].upper()  # Use the first letter of the occupier's name.
            color = "yellow"
        return Text(char, style=color)


class Battlefield(BaseModel):
    width: int
    height: int
    tiles: List[Tile] = Field(default_factory=list)

    @model_validator(mode='before')
    @classmethod
    def validate_tiles(cls, values):
        width = values.get("width")
        height = values.get("height")
        tiles = values.get("tiles", [])
        for tile in tiles:
            if tile.x < 0 or tile.x >= width or tile.y < 0 or tile.y >= height:
                raise ValueError(f"Tile at ({tile.x}, {tile.y}) is outside the battlefield dimensions.")
        return values

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "width": 24,
                    "height": 24,
                    "tiles": []
                }
            ]
        }
    }

    def render(self) -> Panel:
        """Render the battlefield as a Rich Panel."""
        grid = [["" for _ in range(self.width)] for _ in range(self.height)]
        for tile in self.tiles:
            grid[tile.y][tile.x] = tile.render()

        rendered_rows = [
            Text("".join(str(cell) for cell in row)) for row in grid
        ]

        battlefield_text = Text("\n").join(rendered_rows)
        return Panel(
            battlefield_text,
            title="Battlefield",
            subtitle="Legend: .(Open) # (Cover) ^ (Elevation) X (Obstruction) Y (Occupier)",
            border_style="cyan",
        )

    @classmethod
    def generate_default(cls, width: int, height: int) -> "Battlefield":
        tiles = [Tile(x=x, y=y, type=TileType.OPEN) for y in range(height) for x in range(width)]
        return cls(width=width, height=height, tiles=tiles)