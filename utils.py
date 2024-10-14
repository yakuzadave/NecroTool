import random
from typing import List, Tuple

def roll_dice(number_of_dice: int, sides: int) -> List[int]:
    """
    Roll a specified number of dice with a given number of sides.

    Args:
        number_of_dice (int): The number of dice to roll.
        sides (int): The number of sides on each die.

    Returns:
        List[int]: A list of the results of each die roll.
    """
    return [random.randint(1, sides) for _ in range(number_of_dice)]

def calculate_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """
    Calculate the Manhattan distance between two points.

    Args:
        x1 (int): The x-coordinate of the first point.
        y1 (int): The y-coordinate of the first point.
        x2 (int): The x-coordinate of the second point.
        y2 (int): The y-coordinate of the second point.

    Returns:
        int: The Manhattan distance between the two points.
    """
    return abs(x1 - x2) + abs(y1 - y2)

def generate_random_position(max_x: int, max_y: int) -> Tuple[int, int]:
    """
    Generate a random position within the given bounds.

    Args:
        max_x (int): The maximum x-coordinate value.
        max_y (int): The maximum y-coordinate value.

    Returns:
        Tuple[int, int]: A tuple containing the random x and y coordinates.
    """
    return random.randint(0, max_x), random.randint(0, max_y)
