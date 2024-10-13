import random

def roll_dice(number_of_dice: int, sides: int) -> list:
    return [random.randint(1, sides) for _ in range(number_of_dice)]

def calculate_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    return abs(x1 - x2) + abs(y1 - y2)
