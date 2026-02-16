"""
Resource types that exist in the world
Food, plants, sunlight, obstacles
"""

import random

class ResourceType:
    """Enumeration of resource types"""
    EMPTY = 0
    WALL = 1
    FOOD = 2
    PLANT = 3
    SUNLIGHT = 4
    CREATURE = 5


class Resource:
    """Base class for resources in the world"""

    def __init__(self, x, y, resource_type, energy_value=0):
        self.x = x
        self.y = y
        self.type = resource_type
        self.energy_value = energy_value
        self.age = 0

    def update(self):
        """Update resource state each tick"""
        self.age += 1


class Food(Resource):
    """Food resource that can be consumed"""

    def __init__(self, x, y):
        super().__init__(x, y, ResourceType.FOOD, energy_value=random.uniform(10, 20))


class Plant(Resource):
    """Plant resource that grows over time and uses sunlight"""

    def __init__(self, x, y):
        super().__init__(x, y, ResourceType.PLANT, energy_value=random.uniform(5, 15))
        self.growth_stage = 0
        self.max_growth = 10

    def update(self):
        """Plants grow over time"""
        super().update()
        if self.growth_stage < self.max_growth:
            self.growth_stage += 1
            self.energy_value = 5 + (self.growth_stage / self.max_growth) * 10


class Wall(Resource):
    """Obstacle that blocks movement"""

    def __init__(self, x, y):
        super().__init__(x, y, ResourceType.WALL, energy_value=0)
