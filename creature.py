"""
Creature class representing individual organisms
Creatures have genetics, brains, and can perform actions
"""

import random
import math
from genetics import Chromosome
from brain import Brain, Action
from resources import ResourceType
import config

class Creature:
    """Individual organism in the simulation"""

    next_id = 0

    def __init__(self, x, y, chromosome=None, brain=None, energy=None):
        self.id = Creature.next_id
        Creature.next_id += 1
        self.x = x
        self.y = y
        self.alive = True

        if chromosome is None:
            self.chromosome = Chromosome()
        else:
            self.chromosome = chromosome

        if brain is None:
            self.brain = Brain(config.Q_LEARNING_RATE, config.Q_DISCOUNT_FACTOR, config.Q_EXPLORATION_RATE)
        else:
            self.brain = brain

        if energy is None:
            self.energy = config.CREATURE_MAX_ENERGY * 0.5
        else:
            self.energy = energy

        self.age = 0
        self.generation = 0
        self.offspring_count = 0
        self.food_eaten = 0
        self._update_traits()

    def _update_traits(self):
        """Cache genetic trait values for performance"""
        self.size = int(self.chromosome.get_value('size'))
        self.speed = self.chromosome.get_value('speed')
        self.vision_range = int(self.chromosome.get_value('vision_range'))
        self.metabolism = self.chromosome.get_value('metabolism')
        self.energy_efficiency = self.chromosome.get_value('energy_efficiency')
        self.food_preference = self.chromosome.get_value('food_preference')
        self.plant_preference = self.chromosome.get_value('plant_preference')
        self.sunlight_efficiency = self.chromosome.get_value('sunlight_efficiency')
        self.reproduction_threshold = self.chromosome.get_value('reproduction_threshold')
        self.offspring_energy = self.chromosome.get_value('offspring_energy')
        self.color = (
            int(self.chromosome.get_value('color_r')),
            int(self.chromosome.get_value('color_g')),
            int(self.chromosome.get_value('color_b'))
        )

    def perceive(self, world):
        """Gather sensory information from the world"""
        vision_data = {
            'food_nearby': False,
            'plant_nearby': False,
            'wall_nearby': False,
            'creature_nearby': False,
            'visible_cells': []
        }

        for dx in range(-self.vision_range, self.vision_range + 1):
            for dy in range(-self.vision_range, self.vision_range + 1):
                if dx == 0 and dy == 0:
                    continue
                if dx*dx + dy*dy > self.vision_range * self.vision_range:
                    continue
                check_x = self.x + dx
                check_y = self.y + dy
                if world.in_bounds(check_x, check_y):
                    cell_type = world.get_cell_type(check_x, check_y)
                    if cell_type == ResourceType.FOOD:
                        vision_data['food_nearby'] = True
                    elif cell_type == ResourceType.PLANT:
                        vision_data['plant_nearby'] = True
                    elif cell_type == ResourceType.WALL:
                        vision_data['wall_nearby'] = True
                    elif cell_type == ResourceType.CREATURE:
                        vision_data['creature_nearby'] = True

        internal_state = {
            'energy': self.energy,
            'can_reproduce': self.energy >= self.reproduction_threshold
        }
        return vision_data, internal_state

    def decide_action(self, world):
        """Use brain to decide what action to take"""
        vision_data, internal_state = self.perceive(world)
        state = self.brain.get_state_representation(vision_data, internal_state)
        valid_actions = self._get_valid_actions(world, internal_state)
        action = self.brain.choose_action(state, valid_actions)
        return action, state

    def _get_valid_actions(self, world, internal_state):
        """Determine which actions are currently valid"""
        valid = []
        if world.is_walkable(self.x, self.y - 1):
            valid.append(Action.MOVE_UP)
        if world.is_walkable(self.x, self.y + 1):
            valid.append(Action.MOVE_DOWN)
        if world.is_walkable(self.x - 1, self.y):
            valid.append(Action.MOVE_LEFT)
        if world.is_walkable(self.x + 1, self.y):
            valid.append(Action.MOVE_RIGHT)
        cell_type = world.get_cell_type(self.x, self.y)
        if cell_type in [ResourceType.FOOD, ResourceType.PLANT]:
            valid.append(Action.EAT)
        if internal_state['can_reproduce']:
            valid.append(Action.REPRODUCE)
        if self.sunlight_efficiency > 0.3:
            valid.append(Action.PHOTOSYNTHESIZE)
        valid.append(Action.STAY)
        return valid if valid else [Action.STAY]

    def execute_action(self, action, world):
        """Execute the chosen action and return reward"""
        reward = -0.1

        if action == Action.MOVE_UP:
            if world.move_creature(self, self.x, self.y - 1):
                self.y -= 1
                reward -= config.MOVEMENT_COST * self.size
        elif action == Action.MOVE_DOWN:
            if world.move_creature(self, self.x, self.y + 1):
                self.y += 1
                reward -= config.MOVEMENT_COST * self.size
        elif action == Action.MOVE_LEFT:
            if world.move_creature(self, self.x - 1, self.y):
                self.x -= 1
                reward -= config.MOVEMENT_COST * self.size
        elif action == Action.MOVE_RIGHT:
            if world.move_creature(self, self.x + 1, self.y):
                self.x += 1
                reward -= config.MOVEMENT_COST * self.size
        elif action == Action.EAT:
            energy_gained = world.consume_resource(self.x, self.y, self)
            if energy_gained > 0:
                self.energy += energy_gained * self.energy_efficiency
                self.food_eaten += 1
                reward += energy_gained
        elif action == Action.REPRODUCE:
            offspring = self.reproduce(world)
            if offspring:
                reward += 20
                self.offspring_count += 1
        elif action == Action.PHOTOSYNTHESIZE:
            energy_gained = config.SUNLIGHT_INTENSITY * self.sunlight_efficiency * 0.1
            self.energy += energy_gained
            reward += energy_gained * 0.5
        elif action == Action.STAY:
            reward += 0.05

        return reward

    def reproduce(self, world):
        """Create offspring through reproduction"""
        if self.energy < self.reproduction_threshold:
            return None

        adjacent_positions = [
            (self.x, self.y - 1), (self.x, self.y + 1),
            (self.x - 1, self.y), (self.x + 1, self.y)
        ]
        random.shuffle(adjacent_positions)

        for pos_x, pos_y in adjacent_positions:
            if world.is_empty(pos_x, pos_y) and world.in_bounds(pos_x, pos_y):
                offspring_chromosome = self.chromosome.copy()
                offspring_chromosome.mutate(config.MUTATION_RATE)
                offspring_brain = self.brain.copy()
                offspring_energy = self.offspring_energy
                offspring = Creature(pos_x, pos_y, offspring_chromosome, offspring_brain, offspring_energy)
                offspring.generation = self.generation + 1
                self.energy -= config.REPRODUCTION_COST
                return offspring
        return None

    def update(self):
        """Update creature state each tick"""
        self.age += 1
        energy_cost = config.CREATURE_ENERGY_DECAY * self.metabolism * self.size
        self.energy -= energy_cost
        if self.energy <= 0:
            self.alive = False
        if self.energy > config.CREATURE_MAX_ENERGY:
            self.energy = config.CREATURE_MAX_ENERGY
