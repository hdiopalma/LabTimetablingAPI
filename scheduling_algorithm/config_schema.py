import jsonschema
import json
from django.conf import settings
import os
from .config.schema import config_schema
from .config.default import default_config


import copy

class ScheduleConfiguration:

    def __init__(self, data, config_schema, default_config):
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

        # Set default values for missing fitness configuration
        if data["local_search"]["config"].get("fitness") is None:
            data["local_search"]["config"]["fitness"] = data["algorithm"]["config"]["fitness"]

        config = copy.deepcopy(self.default)
        
        
        for key, value in data.items():
            if key in config:
                if isinstance(value, dict):
                    config[key] = update_dict(config[key], value)
                else:
                    config[key] = value
            else:
                if key == "semester":
                    config[key] = value
                else:
                    raise ValueError(f"Invalid configuration key: {key}")
                
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
        '''Create instance from data'''
        #from scheduling_algorithm/config/
        # folder = os.path.join(settings.BASE_DIR, "scheduling_algorithm/config/")
        # with open(folder + "config_schema.json", "r") as f:
        #     config_schema = json.load(f)
        # with open(folder + "default_config.json", "r") as f:
        #     default_config = json.load(f)
        
        config = config_schema
        default = default_config
        
        instance = cls(data, config, default)
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
        return self.data["algorithm"]["config"]["fitness"]

    def get_operator_config(self):
        return self.data["algorithm"]["config"]["operator"]

    def get_selection_config(self):
        return self.get_operator_config()["selection"]

    def get_crossover_config(self):
        return self.get_operator_config()["crossover"]

    def get_mutation_config(self):
        return self.get_operator_config()["mutation"]

    def get_repair_config(self):
        return self.get_operator_config()["repair"]

    def get_neighborhood_config(self):
        '''Return neighborhood configuration'''
        return self.data["local_search"]["config"]["neighborhood"]
    
    def get_algorithm(self):
        return self.data['algorithm']

    def get_main_algorithm(self):
        return self.data['algorithm']['main']
    
    def get_algorithm_config(self):
        return self.data["algorithm"]["config"]

    def get_local_search(self):
        return self.data["local_search"]

    def get_local_search_config(self):
        return self.data["local_search"]

    def get_simulated_annealing_config(self):
        return self.data["local_search"]["simulated_annealing"]

    def get_tabu_search_config(self):
        return self.data["local_search"]["tabu_search"]

    def is_genetic_algorithm(self):
        return self.data["algorithm"]["main"] == "genetic_algorithm"

    def is_genetic_local_search(self):
        return self.data["algorithm"]["main"] == "genetic_local_search"

    def get_max_iteration(self):
        return self.data["algorithm"]["config"]["max_iteration"]

    def get_population_size(self):
        return self.data["algorithm"]["config"]["population_size"]

    def get_elitism_size(self):
        return self.data["algorithm"]["config"]["elitism_size"]

    def __getitem__(self, key):
        return self.data[key]

def update_dict(default_dict, user_dict):
    # Update the default dictionary with values from the user dictionary
    for key, value in user_dict.items():
        if key in default_dict:
            if isinstance(value, dict) and isinstance(default_dict[key], dict):
                # Recursively update nested dictionaries
                default_dict[key] = update_dict(default_dict[key], value)
            else:
                # Update non-dictionary values
                default_dict[key] = value
    return default_dict