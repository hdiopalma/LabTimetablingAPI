#Population Initialization Class
import random
from typing import List
from scheduling_algorithm.structure import Chromosome
from scheduling_algorithm.fitness_function import FitnessManager

import concurrent.futures

class Population:
    def __init__(self, chromosomes: List[Chromosome], fitness_manager: FitnessManager):
        self.chromosomes = chromosomes
        self.fitness_manager = fitness_manager
    
    def __str__(self):
        return f"Population(chromosomes={self.chromosomes})"
    
    def __repr__(self):
        return self.__str__()
    
    def __getitem__(self, index):
        return self.chromosomes[index]
    
    def __len__(self):
        return len(self.chromosomes)
    
    def __iter__(self):
        return iter(self.chromosomes)
    
    def __eq__(self, other: "Population"):
        return self.chromosomes == other.chromosomes
    
    def __contains__(self, chromosome: Chromosome):
        return chromosome in self.chromosomes
    
    def sort_best(self):
        self.chromosomes.sort(key=lambda chromosome: chromosome.fitness)

    def sort_worst(self):
        self.chromosomes.sort(key=lambda chromosome: chromosome.fitness, reverse=True)
    
    def calculate_fitness(self):
        for chromosome in self.chromosomes:
            chromosome.fitness = self.fitness_manager(chromosome)
    
    def add_chromosome(self, chromosome: Chromosome):
        #if chromosome is list, add all chromosomes in the list
        if isinstance(chromosome, list):
            self.chromosomes.extend(chromosome)
        else:
            self.chromosomes.append(chromosome)

    def remove_worst(self, slice_size):
        self.chromosomes = self.chromosomes[:slice_size]
        

    def pop(self):
        return self.chromosomes.pop()
    
    def get_random_chromosome(self):
        return random.choice(self.chromosomes)
    
    def set_fitness_manager(self, fitness_manager: FitnessManager):
        self.fitness_manager = fitness_manager