fitness_properties = {
    "type": "object",
    "properties": {
        "group_assignment_conflict": {
            "type": "object",
            "properties": {
                "max_threshold": {
                    "type": "number"
                },
                "conflict_penalty": {
                    "type": "number"
                }
            }
        },
        "assistant_distribution": {
            "type": "object",
            "properties": {
                "max_group_threshold": {
                    "type": "number"
                },
                "max_shift_threshold": {
                    "type": "number"
                },
                "group_penalty": {
                    "type": "number"
                },
                "shift_penalty": {
                    "type": "number"
                }
            }
        },
        "timeslot_conflict": {
            "type": "object",
            "properties": {
                "assistant_conflict_penalty": {
                    "type": "number"
                },
                "group_conflict_penalty": {
                    "type": "number"
                }
            }
        }
    },
    "required": ["group_assignment_conflict", "assistant_distribution"]
}

operator_properties = {
    "type": "object",
    "properties": {
        "selection": {
            "type": "object",
            "properties": {
                "roulette_wheel": {
                    "type": "boolean"
                },
                "tournament": {
                    "type": "boolean"
                },
                "elitism": {
                    "type": "boolean"
                },
                "tournament_size": {
                    "type": "number"
                }
            },
            "required": ["roulette_wheel", "tournament", "elitism"]
        },
        "crossover": {
            "type": "object",
            "properties": {
                "single_point": {
                    "type": "boolean"
                },
                "two_point": {
                    "type": "boolean"
                },
                "uniform": {
                    "type": "boolean"
                },
                "crossover_probability": {
                    "type": "number"
                },
                "uniform_probability": {
                    "type": "number"
                }
            },
            "required": ["single_point", "two_point", "uniform"]
        },
        "mutation": {
            "type": "object",
            "properties": {
                "swap": {
                    "type": "boolean"
                },
                "shift": {
                    "type": "boolean"
                },
                "random": {
                    "type": "boolean"
                },
                "mutation_probability": {
                    "type": "number"
                }
            },
            "required": ["swap", "shift", "random"]
        },
        "repair": {
            "type": "object",
            "properties": {
                "time_slot": {
                    "type": "boolean"
                }
            },
            "required": ["time_slot"]
        }
    },
    "required": ["selection", "crossover", "mutation", "repair"]
}

algorithm_properties = {
    "type": "object",
    "properties": {
        "algorithm": {
            "type": "string",
            "enum": ["genetic_algorithm", "genetic_local_search"]
        },
        "config": {
            "type":
            "object",
            "properties": {
                "max_iteration": {
                    "type": "number"
                },
                "max_stagnation": {
                    "type": "number"
                },
                "population_size": {
                    "type": "number"
                },
                "elitism_size": {
                    "type": "number"
                },
                # Hybrid parameters
                "local_search_frequency": {
                    "type": "number",
                },
                "num_local_search_candidates": {
                    "type": "number",
                },
                "adaptive_local_search": {
                    "type": "boolean",
                },
                "fitness": fitness_properties,
                "operator": operator_properties
            },
            "required": [
                "max_iteration", "population_size", "elitism_size", "fitness",
                "operator"
            ]
        }
    },
    "required": ["algorithm", "config"]
}

neighborhood_properties = {
    "type": "object",
    "properties": {
        "algorithm": {
            "type": "string",
            "enum":
            ["swap", "random_swap", "random_range_swap", "distance_swap"]
        },
        "random_swap": {
            "type": "object",
            "properties": {
                "neighborhood_size": {
                    "type": "number"
                }
            },
            "required": ["neighborhood_size"]
        },
        "random_range_swap": {
            "type": "object",
            "properties": {
                "neighborhood_size_factor": {
                    "type": "number"
                },
                "range_size_factor": {
                    "type": "number"
                }
            },
            "required": ["neighborhood_size_factor", "range_size_factor"]
        },
        "distance_swap": {
            "type": "object",
            "properties": {
                "distance_percentage": {
                    "type": "number"
                }
            },
            "required": ["distance_percentage"]
        },
        "swap": {
            "type": "boolean",
            "default": False
        }
    },
    "required": ["algorithm"]
}

simulated_annealing_properties = {
    "type": "object",
    "properties": {
        # "fitness": {"$ref": "#/properties/algorithm/properties/config/properties/fitness"},
        "initial_temperature": {
            "type": "number"
        },
        "cooling_rate": {
            "type": "number"
        },
        "max_iteration": {
            "type": "number"
        },
    }
}

tabu_search_properties = {
    "type": "object",
    "properties": {
        # "fitness": {"$ref": "#/properties/algorithm/properties/config/properties/fitness"}, #Refers to the fitness properties of the algorithm
        "tabu_size": {
            "type": "number"
        },
        "max_iteration": {
            "type": "number"
        },
        "max_stagnation": {
            "type": "number"
        }
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
                "fitness": fitness_properties,
                "simulated_annealing": simulated_annealing_properties,
                "tabu_search": tabu_search_properties,
            },
            "required": ["neighborhood"]
        },
    },
    "required": ["algorithm", "config"]
}

config_schema = {
    "type": "object",
    "properties": {
        "semester": {
            "type": "number"
        },  #Semester number, it will be moved to factory when I implement custom factory configuration
        "algorithm": algorithm_properties,
        "local_search": local_search_properties
    },
    "required": ["algorithm", "semester"]
}
