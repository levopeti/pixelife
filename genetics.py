"""
Genetic system for creatures
Handles chromosomes, genes, mutations, and crossover
"""

import random
import numpy as np

class Gene:
    """Represents a single gene that controls a creature trait"""

    def __init__(self, name, value, min_val, max_val):
        self.name = name
        self.value = value
        self.min_val = min_val
        self.max_val = max_val

    def mutate(self, mutation_rate):
        """Mutate the gene value with given probability"""
        if random.random() < mutation_rate:
            mutation = random.gauss(0, (self.max_val - self.min_val) * 0.1)
            self.value = np.clip(self.value + mutation, self.min_val, self.max_val)
            return True
        return False

    def copy(self):
        """Create a copy of this gene"""
        return Gene(self.name, self.value, self.min_val, self.max_val)


class Chromosome:
    """Collection of genes that define a creature's traits"""

    def __init__(self):
        self.genes = {}
        self._initialize_genes()

    def _initialize_genes(self):
        """Initialize all genes with random values"""
        self.genes['size'] = Gene('size', random.uniform(1, 3), 1, 5)
        self.genes['speed'] = Gene('speed', random.uniform(0.5, 2), 0.1, 3)
        self.genes['vision_range'] = Gene('vision_range', random.uniform(3, 7), 2, 10)
        self.genes['metabolism'] = Gene('metabolism', random.uniform(0.3, 0.7), 0.1, 1.0)
        self.genes['energy_efficiency'] = Gene('energy_efficiency', random.uniform(0.5, 0.9), 0.3, 1.0)
        self.genes['food_preference'] = Gene('food_preference', random.random(), 0, 1)
        self.genes['plant_preference'] = Gene('plant_preference', random.random(), 0, 1)
        self.genes['sunlight_efficiency'] = Gene('sunlight_efficiency', random.random(), 0, 1)
        self.genes['reproduction_threshold'] = Gene('reproduction_threshold', random.uniform(60, 90), 50, 100)
        self.genes['offspring_energy'] = Gene('offspring_energy', random.uniform(30, 50), 20, 60)
        self.genes['color_r'] = Gene('color_r', random.randint(50, 255), 50, 255)
        self.genes['color_g'] = Gene('color_g', random.randint(50, 255), 50, 255)
        self.genes['color_b'] = Gene('color_b', random.randint(50, 255), 50, 255)

    def mutate(self, mutation_rate):
        """Mutate all genes according to mutation rate"""
        mutations = 0
        for gene in self.genes.values():
            if gene.mutate(mutation_rate):
                mutations += 1
        return mutations

    def crossover(self, other_chromosome):
        """Perform crossover with another chromosome to create offspring chromosome"""
        offspring = Chromosome()
        for gene_name in self.genes.keys():
            if random.random() < 0.5:
                offspring.genes[gene_name] = self.genes[gene_name].copy()
            else:
                offspring.genes[gene_name] = other_chromosome.genes[gene_name].copy()
        return offspring

    def get_value(self, gene_name):
        """Get the value of a specific gene"""
        return self.genes[gene_name].value

    def copy(self):
        """Create a deep copy of this chromosome"""
        new_chromosome = Chromosome()
        for gene_name, gene in self.genes.items():
            new_chromosome.genes[gene_name] = gene.copy()
        return new_chromosome
