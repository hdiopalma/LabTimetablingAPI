
#Algorithm
from ..algorithms import (
    GeneticAlgorithm,
    GeneticLocalSearch
)

from ..config_schema import ScheduleConfiguration

class SolutionGenerator:
    def __init__(self, data: ScheduleConfiguration):
        # self.config = ScheduleConfiguration.from_data(data)
        self.config = data
        
    def configure_algorithm(self):
        algorithm = self.config.get_algorithm()
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
        local_search_config = self.config.get_local_search()
        return GeneticLocalSearch.create(main_config, local_search_config)
