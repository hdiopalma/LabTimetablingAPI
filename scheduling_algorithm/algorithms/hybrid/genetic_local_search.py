from scheduling_algorithm.algorithms.global_search.genetic_algorithm import GeneticAlgorithm
from scheduling_algorithm.algorithms.local_search.manager import LocalSearchManager
from scheduling_algorithm.structure import Population, Chromosome
import time
import copy

class GeneticLocalSearch(GeneticAlgorithm):
    def __init__(self):
        super().__init__()
        self.local_search = None
        self.local_search_config = {}
        self.local_search_type = None
        
        # Hybrid parameters
        self.local_search_frequency = 5
        self.num_local_search_candidates = 5
        self.adaptive_local_search = True
        
        self.log = {
            'iteration_fitness': [],
            'time_elapsed': 0,
            'best_chromosome': None,
            'stagnation_counter': 0
        }

    def configure(self, factory=None, fitness_manager=None, selection_manager=None, 
                 crossover_manager=None, mutation_manager=None, repair_manager=None,
                 elitism_selection=None, elitism_size=1, local_search=None):
        super().configure(factory, fitness_manager, selection_manager, crossover_manager,
                         mutation_manager, repair_manager, elitism_selection, elitism_size)
        return self

    def run(self, population: Population, *args, **kwargs):
        max_iteration = kwargs.get('max_iteration', self.iteration)
        population_size = kwargs.get('population_size', self.population_size)
        
        time_start = time.time()
        population.set_fitness_manager(self.fitness_manager)
        population.calculate_fitness()
        population.sort_best()

        best_chromosome = population[0].copy()
        stagnation_counter = 0
        initial_mutation_prob = self.mutation_manager.mutation_probability

        for iteration in range(max_iteration):
            # Standard GA evolution
            population = self._evolve_population(population)
            

            # Adaptive local search
            if iteration % self.local_search_frequency == 0:
                population = self._apply_local_search(
                    population, 
                    stagnation_counter
                )
                
                
            # Calculate fitness and sort
            population.calculate_fitness()
            population.sort_best()

            # Update best solution
            current_best = population[0]
            if current_best.fitness < best_chromosome.fitness:
                best_chromosome = current_best.copy()
                stagnation_counter = 0
                self.mutation_manager.mutation_probability = initial_mutation_prob
            else:
                stagnation_counter += 1
                self._adapt_parameters(stagnation_counter)

            # Early stopping
            if stagnation_counter > 50 or best_chromosome.fitness == 0:
                break

            # Logging
            self.log['iteration_fitness'].append((iteration, best_chromosome.fitness))
            print(f"Iteration {iteration}: Best Fitness {best_chromosome.fitness}")

        # Final intensification
        best_chromosome = self._intensify_search(best_chromosome)
        
        time_end = time.time()
        self.log.update({
            'time_elapsed': time_end - time_start,
            'best_chromosome': best_chromosome,
            'stagnation_counter': stagnation_counter
        })
        return best_chromosome

    def _apply_local_search(self, population: Population, stagnation: int):
        """Apply local search with adaptive parameters"""
        # Get algorithm-specific config
        algorithm_config = self.local_search_config['config'][self.local_search_type]
        
        # Create temp config with adaptive parameters
        temp_config = copy.deepcopy(self.local_search_config)
        temp_config['config'][self.local_search_type] = self._get_adaptive_config(
            algorithm_config, 
            stagnation
        )
        
        # Create temporary local search instance
        temp_ls = LocalSearchManager.create(temp_config, self.fitness_manager)
        
        # Apply to top candidates
        improved = []
        for candidate in population[:self.num_local_search_candidates]:
            improved_candidate = temp_ls(candidate.copy())
            if improved_candidate.fitness < candidate.fitness:
                improved.append(improved_candidate)
        
        # Replace worst solutions
        if improved:
            population.replace_worst(improved)
        
        return population

    def _get_adaptive_config(self, base_config: dict, stagnation: int):
        """Generate adaptive configuration based on stagnation"""
        adapted_config = copy.deepcopy(base_config)
        
        # Increase intensity based on stagnation
        intensity = 1.0 + (stagnation // 10)
        
        # Algorithm-specific adaptations
        if self.local_search_type == "simulated_annealing":
            adapted_config["max_iteration"] = int(base_config["max_iteration"] * intensity)
            adapted_config["cooling_rate"] = base_config["cooling_rate"] ** (1/intensity)
        elif self.local_search_type == "tabu_search":
            adapted_config["max_iteration"] = int(base_config["max_iteration"] * intensity)
            adapted_config["tabu_size"] = int(base_config["tabu_size"] * intensity)
        
        return adapted_config

    def _intensify_search(self, chromosome: Chromosome):
        """Final intensification phase"""
        # Double the iteration count
        intensify_config = copy.deepcopy(self.local_search_config)
        intensify_config['config'][self.local_search_type]["max_iteration"] *= 2
        
        # Create intensified searcher
        intensifier = LocalSearchManager.create(intensify_config, self.fitness_manager)
        return intensifier(chromosome)

    def _adapt_parameters(self, stagnation: int):
        """Adapt GA parameters based on stagnation"""
        if self.adaptive_local_search:
            # Increase mutation probability
            self.mutation_manager.mutation_probability = min(
                0.8, 
                self.mutation_manager.mutation_probability * (1 + stagnation/20)
            )
            
            # Adjust local search frequency
            self.local_search_frequency = max(
                3, 
                self.local_search_frequency - (stagnation // 20)
            )

    @classmethod
    def create(cls, main_config: dict, local_search_config: dict):
        instance = super().create(main_config)
        
        # Store config and algorithm type
        instance.local_search_config = local_search_config
        instance.local_search_type = local_search_config["algorithm"]
        
        # Initialize base local search
        instance.local_search = LocalSearchManager.create(
            local_search_config, 
            instance.fitness_manager
        )
        
        print("Hybrid parameters:")
        
        try:
            instance.local_search_frequency = main_config["local_search_frequency"]
            instance.num_local_search_candidates = main_config["num_local_search_candidates"]
            instance.adaptive_local_search = main_config["adaptive_local_search"]
        except KeyError as e:
            print(f"Error in local search configuration: {e}")
            raise ValueError("Invalid local search configuration. Please check the parameters.")
        print(f"Local Search Frequency: {instance.local_search_frequency}")
        print(f"Number of Local Search Candidates: {instance.num_local_search_candidates}")
        print(f"Adaptive Local Search: {instance.adaptive_local_search}")
       
        return instance