import os
import json
import time
import django
from datetime import datetime
from pathlib import Path
from copy import deepcopy
import numpy as np

# Setup Django
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "True"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LabTimetablingAPI.settings")
django.setup()

# Config
EXPERIMENT_NAME = "GA_vs_GA+TS_vs_GA+SA"
NUM_TRIALS = 30
ALGORITHMS = ["genetic_algorithm", "genetic_local_search_tabu", "genetic_local_search_sa"]
CONFIG_TEMPLATE = {
    "semester": 1,
    "algorithm": {
        "algorithm": None,  # Will be set dynamically
        "config": {
            "max_iteration": 500,
            "population_size": 40,
            "elitism_size": 2,
            "max_stagnation": 50,
            "local_search_frequency": 15,
            "num_local_search_candidates": 5,
            "adaptive_local_search": False,
            "fitness": {
                "group_assignment_conflict": {
                    "max_threshold": 3,
                    "conflict_penalty": 0.5
                },
                "assistant_distribution": {
                    "max_group_threshold": 9,
                    "max_shift_threshold": 5,
                    "group_penalty": 0.4,
                    "shift_penalty": 0.6
                },
                "timeslot_conflict": {
                    "assistant_conflict_penalty": 1.2,
                    "group_conflict_penalty": 0.8,
                }
            },
            "operator": {
                "selection": {
                    "roulette_wheel": False,
                    "tournament": True,
                    "elitism": True,
                    "tournament_size": 5
                },
                "crossover": {
                    "single_point": False,
                    "two_point": True,
                    "uniform": False,
                    "crossover_probability": 0.8,
                    "uniform_probability": 0.2
                },
                "mutation": {
                    "swap": True,
                    "shift": True,
                    "repair": False,
                    "mutation_probability": 0.15
                },
                "repair": {
                    "time_slot": True
                }
            }
        }
    },
    "local_search": {
        "algorithm": None,  # Will be set dynamically
        "config": {
            "neighborhood": {
                "algorithm": "random_swap",
                "random_swap": {
                    "neighborhood_size": 20,
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
            "simulated_annealing": {
                "initial_temperature": 1000,
                "cooling_rate": 0.9,
                "max_iteration": 150
            },
            "tabu_search": {
                "tabu_size": 40,
                "max_iteration": 150,
                "max_stagnation": 75,
            }
        }
    }
}


# Output Directory
RESULTS_DIR = Path("experiment_results") / datetime.now().strftime("%Y%m%d_%H%M%S")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.str_):
            return str(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        else:
            return super(NumpyEncoder, self).default(obj)

def run_experiment(algorithm_name):
    """Run scheduling algorithm and collect metrics"""
    from scheduling_algorithm.utils.solution_generator import SolutionGenerator
    
    config = CONFIG_TEMPLATE.copy()
    # config["algorithm"] = "genetic_algorithm"
    if "genetic_algorithm" in algorithm_name:
        # config["algorithm"] = "genetic_algorithm"
        config["algorithm"]["algorithm"] = "genetic_algorithm"
    else:
        config["algorithm"]["algorithm"] = "genetic_local_search"
    
    if "tabu" in algorithm_name:
        config["local_search"]["algorithm"] = "tabu_search"
    elif "sa" in algorithm_name:
        config["local_search"]["algorithm"] = "simulated_annealing"
    else:
        config["local_search"]["algorithm"] = "tabu_search"
        
    # print(f"Using configuration: {json.dumps(config, indent=2)}")
    
    generator = SolutionGenerator.from_data(config)
    
    start_time = time.time()
    solution, iteration_log = generator.generate_solution_weekly_test()
    computation_time = time.time() - start_time
    
    return {
        "solution": solution.to_json(),
        "iteration_log": iteration_log,
        "computation_time": computation_time,
        "final_fitness": solution.fitness,
        "algorithm": algorithm_name,
        "timestamp": datetime.now().isoformat()
    }

def main():
    for algorithm in ALGORITHMS:
        print(f"\n=== Running {algorithm.upper()} ===")
        algorithm_dir = RESULTS_DIR / algorithm
        algorithm_dir.mkdir(exist_ok=True)
        
        for trial in range(1, NUM_TRIALS + 1):
            print(f"Trial {trial}/{NUM_TRIALS}...", end=" ", flush=True)
            
            result = run_experiment(algorithm)
            
            # Save raw output
            output_file = algorithm_dir / f"trial_{trial}.json"
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2, cls=NumpyEncoder)
            
            print(f"Done. Fitness: {result['final_fitness']:.2f}, Time: {result['computation_time']:.2f}s")

if __name__ == "__main__":
    main()