default_config = {
    "local_search": {
        "algorithm": "simulated_annealing",
        "config": {
            "neighborhood": {
                "algorithm": "random_swap",
                "random_swap": {
                    "neighborhood_size": 50
                },
                "random_range_swap": {
                    "neighborhood_size_factor": 0.1,
                    "range_size_factor": 0.1
                },
                "distance_swap": {
                    "distance_percentage": 0.1
                },
                "swap": False
            },
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
            "simulated_annealing": {
                "initial_temperature": 100,
                "cooling_rate": 0.1,
                "max_iteration": 1000,
            },
            "tabu_search": {
                "tabu_size": 50,
                "max_iteration": 1000,
                "max_stagnation": 100,
                
            }
        }
    },
    "algorithm": {
        "algorithm": "genetic_local_search",
        "config": {
            "max_iteration": 500,
            "population_size": 25,
            "elitism_size": 2,
            "max_stagnation": 100,
            #hybrid parameters
            "local_search_frequency": 10,
            "num_local_search_candidates": 1,
            "adaptive_local_search": False,
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
                },
                "timeslot_conflict": {
                    "assistant_conflict_penalty": 2,
                    "group_conflict_penalty": 1
                }
            },
            "operator": {
                "selection": {
                    "roulette_wheel": True,
                    "tournament": False,
                    "elitism": True,
                    "tournament_size": 5
                },
                "crossover": {
                    "single_point": True,
                    "two_point": False,
                    "uniform": False,
                    "crossover_probability": 0.1,
                    "uniform_probability": 0.5
                },
                "mutation": {
                    "swap": True,
                    "shift": False,
                    "random": False,
                    "mutation_probability": 0.1
                },
                "repair": {
                    "time_slot": True
                }
            }
        }
    }
}


