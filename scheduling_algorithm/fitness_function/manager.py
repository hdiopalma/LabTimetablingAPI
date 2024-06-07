#Fitness Manager

from typing import List
from scheduling_algorithm.structure import Chromosome
from scheduling_algorithm.fitness_function.base_fitness import BaseFitness
from scheduling_algorithm.fitness_function.group_assignment_conflict import GroupAssignmentCapacityFitness
from scheduling_algorithm.fitness_function.assistant_distribution import AssistantDistributionFitness
from scheduling_algorithm.fitness_function.timeslot_conflict import TimeslotConflict

from collections import defaultdict

class FitnessManager:
    def __init__(self, fitness_functions: List[BaseFitness]):
        self.fitness_functions = fitness_functions
        self.capacity = self.third_layer(list) # {lab: {mod: {time: [group]}}}
        self.assistant_groups = self.second_layer(set)
        self.assistant_shifts = self.second_layer(set)
        self.timeslots_assistant = self.second_layer(int)
        self.timeslots_group = self.second_layer(int)
        
    def first_layer(self, default_type=list):
        return defaultdict(default_type)
    
    def second_layer(self, default_type=list):
        return defaultdict(lambda: defaultdict(default_type))
    
    def third_layer(self, default_type=list):
        return defaultdict(lambda: defaultdict(lambda: defaultdict(default_type)))

    def __call__(self, chromosome: Chromosome) -> int:
        self.capacity.clear()
        self.assistant_groups.clear()
        self.assistant_shifts.clear()
        self.timeslots_assistant.clear()
        self.timeslots_group.clear()

        # Single pass to gather all necessary data
        for gene in chromosome:
            lab = gene["laboratory"]
            mod = gene["module"]
            time = gene["time_slot"]
            group = gene["group"]
            assistant = gene["assistant"]

            self.capacity[lab][mod][time].append(group)
            self.assistant_groups[assistant][mod].add(group)
            self.assistant_shifts[assistant][mod].add(time)
            self.timeslots_assistant[time][assistant] += 1
            self.timeslots_group[time][group] += 1
            

        # Calculate total fitness
        total_fitness = 0
        for fitness_function in self.fitness_functions:
            if isinstance(fitness_function, GroupAssignmentCapacityFitness):
                total_fitness += fitness_function.calculate_penalty(self.capacity)
            elif isinstance(fitness_function, AssistantDistributionFitness):
                total_fitness += fitness_function.calculate_penalty(self.assistant_groups, self.assistant_shifts)
            elif isinstance(fitness_function, TimeslotConflict):
                total_fitness += fitness_function.calculate_penalty(self.timeslots_assistant, self.timeslots_group)

        return total_fitness
    
    def configure(self, fitness_functions: List[BaseFitness]):
        """Configure the fitness manager
        Args:
            fitness_functions (List[BaseFitness]): List of fitness functions"""
        
        self.fitness_functions = fitness_functions

    def grouped_fitness(self, chromosome: Chromosome):
        """Return a dictionary of fitness functions and their respective fitness value"""
        return {fitness_function.name: fitness_function(chromosome) for fitness_function in self.fitness_functions}
    
    @classmethod
    def create(cls, config: dict):
        """Create a FitnessManager instance from configuration"""
        fitness_functions = []
        for name, config in config.items():
            if name == "group_assignment_conflict":
                fitness_functions.append(GroupAssignmentCapacityFitness.create(config))
            elif name == "assistant_distribution":
                fitness_functions.append(AssistantDistributionFitness.create(config))
            elif name == "timeslot_conflict":
                fitness_functions.append(TimeslotConflict.create(config))
        if not fitness_functions:
            raise ValueError("No fitness functions found in configuration")
        print("Creating FitnessManager with fitness functions: ")
        for fitness_function in fitness_functions:
            print(fitness_function)
        instance = cls(fitness_functions)
        return instance