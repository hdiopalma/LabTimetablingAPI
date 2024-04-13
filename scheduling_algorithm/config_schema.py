import jsonschema
import json

config_schema = {
    "type": "object",
    "properties": {
        "fitness": {
            "type": "object",
            "properties": {
                "group_assignment_conflict": {
                    "type": "object",
                    "properties": {
                        "max_threshold": {"type": "number"},
                        "conflict_penalty": {"type": "number"}
                    }
                },
                "assistant_distribution": {
                    "type": "object",
                    "properties": {
                        "max_group_threshold": {"type": "number"},
                        "max_shift_threshold": {"type": "number"},
                        "group_penalty": {"type": "number"},
                        "shift_penalty": {"type": "number"}
                    }
                },
            },
            "required": ["group_assignment_conflict", "assistant_distribution"]
        },
        "selection": {
            "type": "object",
            "properties": {
                "roulette_wheel": {"type": "boolean"},
                "tournament": {"type": "boolean"},
                "elitism": {"type": "boolean"},
                "tournament_size": {"type": "number"}
            },
            "required": ["roulette_wheel", "tournament", "elitism"]
        },
        "crossover": {
            "type": "object",
            "properties": {
                "single_point": {"type": "boolean"},
                "two_point": {"type": "boolean"},
                "uniform": {"type": "boolean"},
                "crossover_probability": {"type": "number"},
                "uniform_probability": {"type": "number"}
            },
            "required": ["single_point", "two_point", "uniform"]
        },
        "mutation": {
            "type": "object",
            "properties": {
                "swap": {"type": "boolean"},
                "shift": {"type": "boolean"},
                "random": {"type": "boolean"},
                "mutation_probability": {"type": "number"}
            },
            "required": ["swap", "shift", "random"]
        },
        "repair": {
            "type": "object",
            "properties": {
                "time_slot": {"type": "boolean"}
            },
            "required": ["time_slot"]
        },
        "neighborhood": {
            "type": "object",
            "properties": {
                "random_swap": {"type": "boolean"},
                "neighborhood_size": {"type": "number"}
            },
            "required": ["random_swap"]
        },
        "local_search": {
            "type": "object",
            "properties": {
                "simulated_annealing": {"type": "boolean"},
                "tabu_search": {"type": "boolean"},
                "simulated_annealing_config": {
                    "type": "object",
                    "properties": {
                        "initial_temperature": {"type": "number"},
                        "cooling_rate": {"type": "number"},
                        "max_iteration": {"type": "number"},
                        "max_time": {"type": "number"}
                    }
                },
                "tabu_search_config": {
                    "type": "object",
                    "properties": {
                        "tabu_list_size": {"type": "number"},
                        "max_iteration": {"type": "number"},
                        "max_time": {"type": "number"},
                        "max_iteration_without_improvement": {"type": "number"},
                        "max_time_without_improvement": {"type": "number"}
                    }
                }
            },
            "required": ["simulated_annealing", "tabu_search"]
        },
        "algorithm": {
            "type": "object",
            "properties": {
                "genetic_algorithm": {"type": "boolean"},
                "genetic_local_search": {"type": "boolean"}
            },
            "required": ["genetic_algorithm", "genetic_local_search"]
        },
        "max_iteration": {"type": "number"},
        "population_size": {"type": "number"},
        "elitism_size": {"type": "number"}
    },
    "required": ["fitness", "selection", "crossover", "mutation", "repair", "neighborhood", "local_search", "algorithm"]
}

default_config = {
    "fitness": {
        "group_assignment_conflict": {
            "max_threshold": 3,
            "conflict_penalty": 1
        },
        "assistant_distribution": {
            "max_group_threshold": 15,
            "max_shift_threshold": 50,
            "group_penalty": 1,
            "shift_penalty": 1
        }
    },
    "selection": {
        "roulette_wheel": True,
        "tournament": True,
        "elitism": True,
        "tournament_size": 2
    },
    "crossover": {
        "single_point": True,
        "two_point": True,
        "uniform": True,
        "crossover_probability": 0.1,
        "uniform_probability": 0.5
    },
    "mutation": {
        "swap": True,
        "shift": True,
        "random": True,
        "mutation_probability": 0.1
    },
    "repair": {
        "time_slot": True
    },
    "neighborhood": {
        "random_swap": True,
        "neighborhood_size": 100
    },
    "local_search": {
        "simulated_annealing": True,
        "tabu_search": False,
        "simulated_annealing_config": {
            "initial_temperature": 100,
            "cooling_rate": 0.1,
            "max_iteration": 1000,
            "max_time": 60
        },
        "tabu_search_config": {
            "tabu_list_size": 50,
            "max_iteration": 1000,
            "max_time": 60,
            "max_iteration_without_improvement": 100,
            "max_time_without_improvement": 5
        }
    },
    "algorithm": {
        "genetic_algorithm": False,
        "genetic_local_search": True
    },
    "max_iteration": 500,
    "population_size": 25,
    "elitism_size": 2
}

class ScheduleConfiguration:
    def __init__(self, data):
        self.data = data
        self.schema = config_schema
        self.default = default_config

    def validate_config(self, data):
        try:
            jsonschema.validate(data, self.schema)
        except jsonschema.exceptions.ValidationError as e:
            return False, e.message
        return True, None
        
    def load_config(self, data):
        config = self.default.copy()
        config.update(data)
        # validate config
        print("Loading configuration...")
        is_valid, error_message = self.validate_config(config)
        if not is_valid:
            raise ValueError(f"Invalid configuration: {error_message}")
        self.data = config
        print("Configuration loaded successfully.")
        return config

    @classmethod
    def from_data(cls, data):
        # load configuration
        instance = cls(data)
        instance.load_config(data)
        return instance
    
    @classmethod
    def from_file(cls, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        return cls.from_data(data)
    
    def save(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get_fitness_config(self):
        return self.data["fitness"]
    
    def get_selection_config(self):
        return self.data["selection"]
    
    def get_crossover_config(self):
        return self.data["crossover"]
    
    def get_mutation_config(self):
        return self.data["mutation"]
    
    def get_repair_config(self):
        return self.data["repair"]
    
    def get_neighborhood_config(self):
        '''Return neighborhood configuration'''
        return self.data["neighborhood"]

    def get_local_search_config(self):
        return self.data["local_search"]
        
    
    def is_genetic_algorithm(self):
        return self.data["algorithm"]["genetic_algorithm"]
    
    def is_genetic_local_search(self):
        return self.data["algorithm"]["genetic_local_search"]
    
    def get_max_iteration(self):
        return self.data["max_iteration"]
    
    def get_population_size(self):
        return self.data["population_size"]
    
    def get_elitism_size(self):
        return self.data["elitism_size"]

    def __getitem__(self, key):
        return self.data[key]