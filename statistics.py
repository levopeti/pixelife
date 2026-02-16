"""
Statistics tracking and monitoring for the simulation
"""
import time
from collections import defaultdict

class Statistics:
    def __init__(self):
        self.start_time = time.time()
        self.ticks = 0
        self.creature_count = 0
        self.peak_population = 0
        self.total_births = 0
        self.total_deaths = 0
        self.generation_distribution = defaultdict(int)
        self.average_generation = 0
        self.max_generation = 0
        self.average_traits = {}
        self.ticks_per_second = 0
        self.last_update_time = time.time()
        self.last_tick_count = 0
    
    def update(self, world):
        self.ticks += 1
        self.creature_count = len(world.all_creatures)
        if self.creature_count > self.peak_population:
            self.peak_population = self.creature_count
        
        if self.creature_count > 0:
            self.generation_distribution.clear()
            total_generation = 0
            self.max_generation = 0
            trait_sums = defaultdict(float)
            
            for creature in world.all_creatures:
                self.generation_distribution[creature.generation] += 1
                total_generation += creature.generation
                self.max_generation = max(self.max_generation, creature.generation)
                trait_sums['size'] += creature.size
                trait_sums['speed'] += creature.speed
                trait_sums['vision_range'] += creature.vision_range
                trait_sums['energy'] += creature.energy
                trait_sums['age'] += creature.age
            
            self.average_generation = total_generation / self.creature_count
            for trait, total in trait_sums.items():
                self.average_traits[trait] = total / self.creature_count
        
        current_time = time.time()
        if current_time - self.last_update_time >= 1.0:
            ticks_elapsed = self.ticks - self.last_tick_count
            self.ticks_per_second = ticks_elapsed / (current_time - self.last_update_time)
            self.last_update_time = current_time
            self.last_tick_count = self.ticks
    
    def get_elapsed_time(self):
        return time.time() - self.start_time
    
    def get_summary(self):
        summary = []
        summary.append(f"=== Simulation Statistics ===")
        summary.append(f"Ticks: {self.ticks}")
        summary.append(f"Elapsed Time: {self.get_elapsed_time():.1f}s")
        summary.append(f"TPS: {self.ticks_per_second:.1f}")
        summary.append(f"Creatures: {self.creature_count}")
        summary.append(f"Peak Population: {self.peak_population}")
        summary.append(f"Total Births: {self.total_births}")
        summary.append(f"Total Deaths: {self.total_deaths}")
        summary.append(f"Avg Generation: {self.average_generation:.2f}")
        summary.append(f"Max Generation: {self.max_generation}")
        return "\n".join(summary)
    
    def print_summary(self):
        print(self.get_summary())

