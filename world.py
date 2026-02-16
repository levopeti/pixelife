"""
World class managing the 2D grid environment
Handles resource placement, creature movement, and spatial queries
"""

import random
import numpy as np
from resources import ResourceType, Food, Plant, Wall
import config

class World:
    """2D grid world containing all resources and creatures"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=int)
        self.resources = {}
        self.creatures = {}
        self.all_creatures = []
        self._initialize_world()

    def _initialize_world(self):
        """Generate initial world with resources and obstacles"""
        for x in range(self.width):
            self._place_wall(x, 0)
            self._place_wall(x, self.height - 1)
        for y in range(self.height):
            self._place_wall(0, y)
            self._place_wall(self.width - 1, y)

        num_wall_clusters = random.randint(10, 20)
        for _ in range(num_wall_clusters):
            center_x = random.randint(5, self.width - 5)
            center_y = random.randint(5, self.height - 5)
            cluster_size = random.randint(3, 8)
            for _ in range(cluster_size):
                offset_x = random.randint(-2, 2)
                offset_y = random.randint(-2, 2)
                self._place_wall(center_x + offset_x, center_y + offset_y)

        for _ in range(config.INITIAL_FOOD_COUNT):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if self.is_empty(x, y):
                self._place_food(x, y)

        for _ in range(config.INITIAL_PLANT_COUNT):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if self.is_empty(x, y):
                self._place_plant(x, y)

    def _place_wall(self, x, y):
        """Place a wall at given coordinates"""
        if self.in_bounds(x, y):
            self.grid[y][x] = ResourceType.WALL
            self.resources[(x, y)] = Wall(x, y)

    def _place_food(self, x, y):
        """Place food at given coordinates"""
        if self.in_bounds(x, y) and self.is_empty(x, y):
            self.grid[y][x] = ResourceType.FOOD
            self.resources[(x, y)] = Food(x, y)

    def _place_plant(self, x, y):
        """Place plant at given coordinates"""
        if self.in_bounds(x, y) and self.is_empty(x, y):
            self.grid[y][x] = ResourceType.PLANT
            self.resources[(x, y)] = Plant(x, y)

    def add_creature(self, creature):
        """Add a creature to the world"""
        if self.in_bounds(creature.x, creature.y) and self.is_empty(creature.x, creature.y):
            self.grid[creature.y][creature.x] = ResourceType.CREATURE
            self.creatures[(creature.x, creature.y)] = creature
            self.all_creatures.append(creature)
            return True
        return False

    def remove_creature(self, creature):
        """Remove a creature from the world"""
        if (creature.x, creature.y) in self.creatures:
            self.grid[creature.y][creature.x] = ResourceType.EMPTY
            del self.creatures[(creature.x, creature.y)]
            if creature in self.all_creatures:
                self.all_creatures.remove(creature)

    def move_creature(self, creature, new_x, new_y):
        """Move a creature to a new position"""
        if not self.in_bounds(new_x, new_y):
            return False
        if not self.is_walkable(new_x, new_y):
            return False
        old_pos = (creature.x, creature.y)
        if old_pos in self.creatures:
            self.grid[creature.y][creature.x] = ResourceType.EMPTY
            del self.creatures[old_pos]
        self.grid[new_y][new_x] = ResourceType.CREATURE
        self.creatures[(new_x, new_y)] = creature
        return True

    def consume_resource(self, x, y, creature):
        """Consume a resource at given position"""
        if (x, y) not in self.resources:
            return 0
        resource = self.resources[(x, y)]
        energy_gain = 0
        if resource.type == ResourceType.FOOD:
            energy_gain = resource.energy_value * creature.food_preference
        elif resource.type == ResourceType.PLANT:
            energy_gain = resource.energy_value * creature.plant_preference
        if energy_gain > 0:
            del self.resources[(x, y)]
            self.grid[y][x] = ResourceType.CREATURE
        return energy_gain

    def update_resources(self):
        """Update all resources and handle respawning"""
        for resource in list(self.resources.values()):
            resource.update()
        if random.random() < config.FOOD_RESPAWN_RATE:
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if self.is_empty(x, y):
                self._place_food(x, y)
        if random.random() < config.PLANT_GROWTH_RATE:
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if self.is_empty(x, y):
                self._place_plant(x, y)

    def in_bounds(self, x, y):
        """Check if coordinates are within world bounds"""
        return 0 <= x < self.width and 0 <= y < self.height

    def is_empty(self, x, y):
        """Check if cell is empty"""
        if not self.in_bounds(x, y):
            return False
        return self.grid[y][x] == ResourceType.EMPTY

    def is_walkable(self, x, y):
        """Check if creature can walk on this cell"""
        if not self.in_bounds(x, y):
            return False
        cell_type = self.grid[y][x]
        return cell_type in [ResourceType.EMPTY, ResourceType.FOOD, ResourceType.PLANT]

    def get_cell_type(self, x, y):
        """Get the type of cell at coordinates"""
        if not self.in_bounds(x, y):
            return ResourceType.WALL
        return self.grid[y][x]

    def get_creature_at(self, x, y):
        """Get creature at coordinates"""
        return self.creatures.get((x, y), None)

    def get_resource_at(self, x, y):
        """Get resource at coordinates"""
        return self.resources.get((x, y), None)
