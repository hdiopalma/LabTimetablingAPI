#Fitness Manager
#path: scheduling_algorithm/fitness_function/manager.py

from typing import List
from scheduling_algorithm.structure import Chromosome
from scheduling_algorithm.fitness_function.base_fitness import BaseFitness
from scheduling_algorithm.fitness_function.group_assignment_conflict import GroupAssignmentCapacityFitness
from scheduling_algorithm.fitness_function.assistant_distribution import AssistantDistributionFitness
from scheduling_algorithm.fitness_function.timeslot_conflict import TimeslotConflict

class FitnessManager:
    def __init__(self, fitness_functions: List[BaseFitness]):
        self.fitness_functions = fitness_functions

    def __call__(self, chromosome: Chromosome) -> int:
        """Calculate the fitness of a chromosome"""
        labs = chromosome["laboratory"]
        modules = chromosome["module"]
        chapters = chromosome["chapter"]
        timeslot_dates = chromosome["time_slot_date"]
        # timeslot_days = chromosome["time_slot_day"]
        timeslot_shifts = chromosome["time_slot_shift"]
        groups = chromosome["group"]
        assistants = chromosome["assistant"]
            
        # Calculate total fitness
        total_fitness = 0
        for fitness_function in self.fitness_functions:
            if isinstance(fitness_function, GroupAssignmentCapacityFitness):
                total_fitness += fitness_function.calculate_penalty(modules, assistants, timeslot_dates, timeslot_shifts)
            elif isinstance(fitness_function, AssistantDistributionFitness):
                total_fitness += fitness_function.calculate_penalty(modules, assistants, groups, timeslot_dates, timeslot_shifts)
            elif isinstance(fitness_function, TimeslotConflict):
                total_fitness += fitness_function.calculate_penalty(assistants, groups, chapters, timeslot_dates, timeslot_shifts)
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