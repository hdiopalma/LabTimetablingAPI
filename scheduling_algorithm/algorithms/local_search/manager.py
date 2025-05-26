from .simulated_annealing import SimulatedAnnealing
from .tabu_search import TabuSearch
from ..neighborhood.neighborhood import NeighborhoodManager
from ...fitness_function import FitnessManager

class LocalSearchManager:
    @staticmethod
    def create(config: dict, fitness_manager: FitnessManager):
        '''Create the local search algorithm
        '''
        fitness = fitness_manager
        algorithm = config["algorithm"]
        if algorithm == "simulated_annealing":
            # print("Creating Simulated Annealing")
            neighborhood = NeighborhoodManager.create(config["config"]["neighborhood"])
            return SimulatedAnnealing.create(fitness, neighborhood, config["config"]["simulated_annealing"])
        elif algorithm == "tabu_search":
            neighborhood = NeighborhoodManager.create(config["config"]["neighborhood"], is_tabu=True)
            return TabuSearch.create(fitness, neighborhood, config["config"]["tabu_search"])
        else:
            raise ValueError(f"Invalid local search algorithm: {algorithm}")
        
        
#Config schema for reference
neighborhood_properties = {
    "type": "object",
    "properties": {
        "algorithm": {
            "type": "string",
            "enum": ["swap", "random_swap", "random_range_swap", "distance_swap"]
        },
        "random_swap": {
            "type": "object",
            "properties": {"neighborhood_size": {"type": "number"}},
            "required": ["neighborhood_size"]
        },
        "random_range_swap": {
            "type": "object",
            "properties": {"neighborhood_size_factor": {"type": "number"}, "range_size_factor": {"type": "number"}},
            "required": ["neighborhood_size_factor", "range_size_factor"]
        },
        "distance_swap": {
            "type": "object",
            "properties": {"distance_percentage": {"type": "number"}},
            "required": ["distance_percentage"]
        },
        "swap": {"type": "boolean", "default": False}
    },
    "required": ["algorithm"]
}

simulated_annealing_properties = {
    "type": "object",
    "properties": {
        "initial_temperature": {"type": "number"},
        "cooling_rate": {"type": "number"},
        "max_iteration": {"type": "number"},
        "max_time": {"type": "number"}
    }
}

tabu_search_properties = {
    "type": "object",
    "properties": {
        "tabu_list_size": {"type": "number"},
        "max_iteration": {"type": "number"},
        "max_time": {"type": "number"},
        "max_iteration_without_improvement": {"type": "number"},
        "max_time_without_improvement": {"type": "number"}
    }
}

local_search_properties = {
    "type": "object",
    "properties": {
        "algorithm": {
            "type": "string",
            "enum": ["simulated_annealing", "tabu_search"]
        },
        "config": {
            "type": "object",
            "properties": {
                "neighborhood": neighborhood_properties,
                "fitness": "fitness_properties",
                "simulated_annealing": simulated_annealing_properties,
                "tabu_search": tabu_search_properties
            },
            "required": ["neighborhood"]
        },
    },
    "required": ["algorithm", "config"]
}
