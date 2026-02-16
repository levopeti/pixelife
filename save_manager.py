"""
Save and load system for the simulation
Allows saving and loading the complete simulation state
"""

import pickle
import os
import json
from datetime import datetime
import config

class SaveManager:
    """Manages saving and loading simulation states"""
    
    def __init__(self):
        # Create save directory if it doesn't exist
        if not os.path.exists(config.SAVE_DIRECTORY):
            os.makedirs(config.SAVE_DIRECTORY)
    
    def save_simulation(self, world, statistics, filename=None):
        """
        Save complete simulation state
        
        Args:
            world: World object to save
            statistics: Statistics object to save
            filename: Optional filename, if None generates timestamp-based name
        
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simulation_{timestamp}.save"
        
        filepath = os.path.join(config.SAVE_DIRECTORY, filename)
        
        # Prepare data structure
        save_data = {
            'world': self._serialize_world(world),
            'statistics': self._serialize_statistics(statistics),
            'config': self._serialize_config(),
            'version': '1.0'
        }
        
        # Save to file
        with open(filepath, 'wb') as f:
            pickle.dump(save_data, f)
        
        # Also save a human-readable summary
        summary_path = filepath.replace('.save', '_summary.txt')
        with open(summary_path, 'w') as f:
            f.write(self._generate_summary(statistics))
        
        print(f"Simulation saved to: {filepath}")
        return filepath
    
    def load_simulation(self, filename):
        """
        Load simulation state from file
        
        Args:
            filename: Name of file to load (can be full path or just filename)
        
        Returns:
            Tuple of (world, statistics) or None if load failed
        """
        # Handle both full path and filename
        if not os.path.exists(filename):
            filepath = os.path.join(config.SAVE_DIRECTORY, filename)
        else:
            filepath = filename
        
        if not os.path.exists(filepath):
            print(f"Save file not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'rb') as f:
                save_data = pickle.load(f)
            
            # Deserialize world and statistics
            from world import World
            from statistics import Statistics
            
            world = self._deserialize_world(save_data['world'])
            statistics = self._deserialize_statistics(save_data['statistics'])
            
            print(f"Simulation loaded from: {filepath}")
            print(f"  Ticks: {statistics.ticks}")
            print(f"  Creatures: {statistics.creature_count}")
            print(f"  Max Generation: {statistics.max_generation}")
            
            return world, statistics
        
        except Exception as e:
            print(f"Error loading save file: {e}")
            return None
    
    def list_saves(self):
        """List all available save files"""
        if not os.path.exists(config.SAVE_DIRECTORY):
            return []
        
        saves = []
        for filename in os.listdir(config.SAVE_DIRECTORY):
            if filename.endswith('.save'):
                filepath = os.path.join(config.SAVE_DIRECTORY, filename)
                stat = os.stat(filepath)
                saves.append({
                    'filename': filename,
                    'path': filepath,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime)
                })
        
        # Sort by modification time (newest first)
        saves.sort(key=lambda x: x['modified'], reverse=True)
        return saves
    
    def _serialize_world(self, world):
        """Serialize world object to dictionary"""
        return {
            'width': world.width,
            'height': world.height,
            'grid': world.grid.tolist(),
            'resources': {str(k): self._serialize_resource(v) 
                         for k, v in world.resources.items()},
            'creatures': [self._serialize_creature(c) 
                         for c in world.all_creatures]
        }
    
    def _deserialize_world(self, data):
        """Deserialize world object from dictionary"""
        from world import World
        import numpy as np
        
        world = World.__new__(World)
        world.width = data['width']
        world.height = data['height']
        world.grid = np.array(data['grid'], dtype=int)
        world.resources = {}
        world.creatures = {}
        world.all_creatures = []
        
        # Restore resources
        for pos_str, resource_data in data['resources'].items():
            pos = eval(pos_str)  # Convert string back to tuple
            resource = self._deserialize_resource(resource_data)
            world.resources[pos] = resource
        
        # Restore creatures
        for creature_data in data['creatures']:
            creature = self._deserialize_creature(creature_data)
            world.creatures[(creature.x, creature.y)] = creature
            world.all_creatures.append(creature)
        
        return world
    
    def _serialize_creature(self, creature):
        """Serialize creature object"""
        from genetics import Chromosome
        
        return {
            'id': creature.id,
            'x': creature.x,
            'y': creature.y,
            'energy': creature.energy,
            'age': creature.age,
            'generation': creature.generation,
            'offspring_count': creature.offspring_count,
            'food_eaten': creature.food_eaten,
            'chromosome': {
                'genes': {name: {
                    'name': gene.name,
                    'value': gene.value,
                    'min_val': gene.min_val,
                    'max_val': gene.max_val
                } for name, gene in creature.chromosome.genes.items()}
            },
            'q_table': dict(creature.brain.q_table),
            'brain_params': {
                'learning_rate': creature.brain.learning_rate,
                'discount_factor': creature.brain.discount_factor,
                'exploration_rate': creature.brain.exploration_rate
            }
        }
    
    def _deserialize_creature(self, data):
        """Deserialize creature object"""
        from creature import Creature
        from genetics import Chromosome, Gene
        from brain import Brain
        import numpy as np
        
        # Recreate chromosome
        chromosome = Chromosome()
        for gene_name, gene_data in data['chromosome']['genes'].items():
            chromosome.genes[gene_name] = Gene(
                gene_data['name'],
                gene_data['value'],
                gene_data['min_val'],
                gene_data['max_val']
            )
        
        # Recreate brain
        brain = Brain(
            data['brain_params']['learning_rate'],
            data['brain_params']['discount_factor'],
            data['brain_params']['exploration_rate']
        )
        
        # Restore Q-table
        for state, q_values in data['q_table'].items():
            brain.q_table[state] = np.array(q_values)
        
        # Create creature
        creature = Creature(data['x'], data['y'], chromosome, brain, data['energy'])
        creature.id = data['id']
        creature.age = data['age']
        creature.generation = data['generation']
        creature.offspring_count = data['offspring_count']
        creature.food_eaten = data['food_eaten']
        
        return creature
    
    def _serialize_resource(self, resource):
        """Serialize resource object"""
        return {
            'type': resource.type,
            'x': resource.x,
            'y': resource.y,
            'energy_value': resource.energy_value,
            'age': resource.age,
            'extra': self._get_resource_extra_data(resource)
        }
    
    def _deserialize_resource(self, data):
        """Deserialize resource object"""
        from resources import Food, Plant, Wall, Resource
        
        if data['type'] == 2:  # FOOD
            resource = Food(data['x'], data['y'])
        elif data['type'] == 3:  # PLANT
            resource = Plant(data['x'], data['y'])
            if 'growth_stage' in data['extra']:
                resource.growth_stage = data['extra']['growth_stage']
        elif data['type'] == 1:  # WALL
            resource = Wall(data['x'], data['y'])
        else:
            resource = Resource(data['x'], data['y'], data['type'], data['energy_value'])
        
        resource.age = data['age']
        return resource
    
    def _get_resource_extra_data(self, resource):
        """Get resource-specific extra data"""
        extra = {}
        if hasattr(resource, 'growth_stage'):
            extra['growth_stage'] = resource.growth_stage
        return extra
    
    def _serialize_statistics(self, statistics):
        """Serialize statistics object"""
        return {
            'ticks': statistics.ticks,
            'creature_count': statistics.creature_count,
            'peak_population': statistics.peak_population,
            'total_births': statistics.total_births,
            'total_deaths': statistics.total_deaths,
            'average_generation': statistics.average_generation,
            'max_generation': statistics.max_generation,
            'average_traits': dict(statistics.average_traits)
        }
    
    def _deserialize_statistics(self, data):
        """Deserialize statistics object"""
        from statistics import Statistics
        import time
        
        statistics = Statistics()
        statistics.ticks = data['ticks']
        statistics.creature_count = data['creature_count']
        statistics.peak_population = data['peak_population']
        statistics.total_births = data['total_births']
        statistics.total_deaths = data['total_deaths']
        statistics.average_generation = data['average_generation']
        statistics.max_generation = data['max_generation']
        statistics.average_traits = data['average_traits']
        
        # Reset timing
        statistics.start_time = time.time()
        statistics.last_update_time = time.time()
        statistics.last_tick_count = statistics.ticks
        
        return statistics
    
    def _serialize_config(self):
        """Save current configuration"""
        return {
            'world_width': config.WORLD_WIDTH,
            'world_height': config.WORLD_HEIGHT,
            'mutation_rate': config.MUTATION_RATE,
            'max_creatures': config.MAX_CREATURES
        }
    
    def _generate_summary(self, statistics):
        """Generate human-readable summary"""
        return statistics.get_summary()

