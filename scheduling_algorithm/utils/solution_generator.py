import time
import datetime
from math import ceil

#Algorithm
from ..algorithms import (
    GeneticAlgorithm,
    GeneticLocalSearch
)

from ..config_schema import ScheduleConfiguration
#Model
from scheduling_data.models import Solution, ScheduleData, Semester
from django.db import transaction
from scheduling_data.utils import signals

from ..factory import Factory

from ..data_parser import ModuleData

from ..structure.chromosome import Chromosome

from ..factory.factory import WeeklyFactory

def calculate_module_weeks(module_id):
    module_date = ModuleData.get_dates(module_id)
    start_date = module_date.start_date
    end_date = module_date.end_date
    weeks = ceil((end_date - start_date).days / 7)
    return weeks

class SolutionGenerator:
    def __init__(self, data: ScheduleConfiguration):
        # self.config = ScheduleConfiguration.from_data(data)
        self.config = data
        self.algorithm: GeneticAlgorithm = self.configure_algorithm()
        self.best_chromosome = None
        self.time_elapsed = 0
        self.created_solution = None
        
    @classmethod
    def from_data(cls, data: dict):
        return cls(ScheduleConfiguration.from_data(data))
        
    def configure_algorithm(self):
        algorithm = self.config.get_main_algorithm()
        if algorithm == "genetic_algorithm":
            return self.configure_genetic_algorithm()
        elif algorithm == "genetic_local_search":
            return self.configure_genetic_local_search_algorithm()
        else:
            raise ValueError(f"Invalid algorithm: {algorithm}")
        
    def configure_genetic_algorithm(self):
        config = self.config.get_algorithm_config()
        return GeneticAlgorithm.create(config=config)
    
    def configure_genetic_local_search_algorithm(self):
        main_config = self.config.get_algorithm_config()
        local_search_config = self.config.get_local_search_config()
        return GeneticLocalSearch.create(main_config, local_search_config)
    
    def generate_solution(self) -> Solution:
        solution = self.generate_solution_weekly()
        return solution
    
    def generate_solution_normal(self) -> Solution:
        """Generates a timetabling solution using the configured algorithm.

        Raises:
            e: Any exception that occurs during the solution generation.

        Returns:
            Solution: The generated solution data.
        """
        solution = self.created_solution or self.create_solution()
        try:
            modules = ModuleData.get_modules_by_semester(self.config['semester'])
            for module in modules:
                factory_instance = Factory()
                print(f"Generating population for module {module.id}")
                population = factory_instance.generate_population(population_size=self.config.get_population_size(), module_id=module.id)
                self.algorithm.run(population=population)
                self.best_chromosome = self.algorithm.log['best_chromosome']
                self.create_schedule_data(solution)
                self.update_solution(solution)
        except Exception as e:
            self.update_solution(solution, status=Solution.Status.FAILED)
            raise e
        self.created_solution = None
        return solution
    
    def generate_solution_normal_test(self) -> Solution:
        """Generates a timetabling solution using the configured algorithm.

        Raises:
            e: Any exception that occurs during the solution generation.

        Returns:
            Solution: The generated solution data.
        """
        try:
            modules = ModuleData.get_modules_by_semester(self.config['semester'])
            for module in modules:
                factory_instance = Factory()
                print(f"Generating population for module {module.id}")
                population = factory_instance.generate_population(population_size=self.config.get_population_size(), module_id=module.id)
                self.algorithm.run(population=population)
                self.best_chromosome = self.algorithm.log['best_chromosome']
        except Exception as e:
            raise e
        self.created_solution = None
        return self.best_chromosome
    
    def generate_solution_weekly(self) -> Solution:
        """Generates a timetabling solution using the configured algorithm, segmented by weeks.

        Raises:
            e: _description_

        Returns:
            Solution: _description_
        """
        solution = self.created_solution or self.create_solution()
        try:
            self.best_chromosome = Chromosome()
            modules = ModuleData.get_modules_by_semester(self.config['semester'])
            for module in modules:
                num_weeks = calculate_module_weeks(module.id)
                for week in range(num_weeks):
                    factory_instance = WeeklyFactory(weeks=num_weeks, week= week + 1)
                    print(f"Generating population for module {module.id} week {week + 1}")
                    weekly_population = factory_instance.generate_population(population_size=self.config.get_population_size(), module_id=module.id)
                    if len(weekly_population) == 0:
                        print(f"Module {module.id} week {week + 1} has no population, all the remaining chapter are already assigned on previous weeks")
                        print("Skipping to next module")
                        break
                    weekly_chromosome = self.algorithm.run(population=weekly_population)
                    self.best_chromosome += weekly_chromosome
            self.create_schedule_data(solution)
            self.update_solution(solution)
        except Exception as e:
            self.update_solution(solution, status=Solution.Status.FAILED)
            raise e
        self.created_solution = None
        return solution
    
    def generate_solution_weekly_test(self) -> Solution:
        try:
            self.best_chromosome = Chromosome()
            modules = ModuleData.get_modules_by_semester(self.config['semester'])
            for module in modules:
                num_weeks = calculate_module_weeks(module.id)
                for week in range(num_weeks):
                    factory_instance = WeeklyFactory(weeks=num_weeks, week= week + 1)
                    print(f"Generating population for module {module.id} week {week + 1}")
                    weekly_population = factory_instance.generate_population(population_size=self.config.get_population_size(), module_id=module.id)
                    if len(weekly_population) == 0:
                        print(f"Module {module.id} week {week + 1} has no population, all the remaining chapter are already assigned on previous weeks")
                        print("Starting the schedule generation algorithm...")
                        break
                    weekly_chromosome = self.algorithm.run(population=weekly_population)
                    self.best_chromosome += weekly_chromosome
        except Exception as e:
            raise e
        self.created_solution = None
        return self.best_chromosome
            
    def test(self):
        self.algorithm.run()
        self.best_chromosome = self.algorithm.log['best_chromosome']
        return self.best_chromosome
    
    def merge_solutions(self, solutions):
        pass
    
    def create_solution(self) -> Solution:
        """Creates a new solution object in the database. For storing configuration and progress data.

        Returns:
            Solution: The created solution object.
        """
        data = self.config
        
        solution = Solution()
        semester_id = data['semester']
        semester_instance = Semester.objects.get(pk=semester_id)
        solution.name = "Solution " + str(time.ctime())
        solution.semester = semester_instance
        solution.fitness = data.get_fitness_config()
        solution.selection = data.get_selection_config()
        solution.crossover = data.get_crossover_config()
        solution.mutation = data.get_mutation_config()
        solution.repair = data.get_repair_config()
        solution.neighborhood = data.get_neighborhood_config()
        solution.algorithm = data.get_algorithm()
        solution.local_search = data.get_local_search()
        solution.max_iteration = data.get_max_iteration()
        solution.population_size = data.get_population_size()
        solution.elitism_size = data.get_elitism_size()
        solution.save()
        self.created_solution = solution
        
        # signals.notify_task(solution)
        return solution
    
    def update_solution(self, solution: Solution, status=Solution.Status.COMPLETED):
        solution.status = status
        solution.best_fitness = self.best_chromosome.fitness
        solution.time_elapsed = self.algorithm.log['time_elapsed'] if status == Solution.Status.COMPLETED else 0
        solution.gene_count = len(self.best_chromosome)
        solution.save()
        signals.notify_task(solution)
        return solution
    
    def create_schedule_data(self, solution: Solution):
        schedule_data_list = []
        for gene in self.best_chromosome:
            schedule_data_list.append(ScheduleData(
                solution=solution,
                laboratory_id=gene['laboratory'],
                module_id=gene['module'],
                chapter_id=gene['chapter'],
                group_id=gene['group'],
                assistant_id=gene['assistant'],
                date= datetime.datetime.fromtimestamp(gene['time_slot'].date, tz=datetime.timezone.utc),
                day=gene['time_slot'].day,
                shift=gene['time_slot'].shift
            ))

        with transaction.atomic():
            ScheduleData.objects.bulk_create(schedule_data_list)
    
    
