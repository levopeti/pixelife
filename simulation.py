"""
Core simulation engine
"""
import random
from creature import Creature
import config

class Simulation:
    def __init__(self, world, statistics):
        self.world = world
        self.statistics = statistics
        self.running = True
        self._spawn_initial_creatures()
    
    def _spawn_initial_creatures(self):
        for _ in range(config.INITIAL_CREATURE_COUNT):
            for attempt in range(100):
                x = random.randint(2, self.world.width - 3)
                y = random.randint(2, self.world.height - 3)
                if self.world.is_empty(x, y):
                    creature = Creature(x, y)
                    if self.world.add_creature(creature):
                        self.statistics.total_births += 1
                        break
    
    def update(self):
        self.world.update_resources()
        creatures_to_update = list(self.world.all_creatures)
        random.shuffle(creatures_to_update)
        new_creatures = []
        
        for creature in creatures_to_update:
            if not creature.alive:
                continue
            action, state = creature.decide_action(self.world)
            reward = creature.execute_action(action, self.world)
            creature.update()
            vision_data, internal_state = creature.perceive(self.world)
            next_state = creature.brain.get_state_representation(vision_data, internal_state)
            creature.brain.learn(state, action, reward, next_state)
        
        dead_creatures = [c for c in self.world.all_creatures if not c.alive]
        for creature in dead_creatures:
            self.world.remove_creature(creature)
            self.statistics.total_deaths += 1
        
        if len(self.world.all_creatures) > config.MAX_CREATURES:
            sorted_creatures = sorted(self.world.all_creatures, key=lambda c: c.age, reverse=True)
            excess = len(sorted_creatures) - config.MAX_CREATURES
            for creature in sorted_creatures[:excess]:
                self.world.remove_creature(creature)
                self.statistics.total_deaths += 1
        
        self.statistics.update(self.world)

