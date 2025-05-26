import random
from typing import List

from scheduling_algorithm.structure import Chromosome
from scheduling_algorithm.data_parser import Constant

import random
from typing import Dict, List

class BaseNeighborhood:
    def __init__(self, name: str):
        self.name = name
        self.track_moves = False
    
    def __str__(self):
        return f"Neighborhood(name={self.name})"
    
    def __repr__(self):
        return self.__str__()
    
    def __call__(self, chromosome: Chromosome):
        raise NotImplementedError("Neighborhood function not implemented")
    
    def with_moves(self) -> 'BaseNeighborhood':
        '''Track the moves made by the neighborhood
        '''

        new_instance = self.__class__()
        new_instance.__dict__ = self.__dict__.copy()
        new_instance.track_moves = True
        return new_instance
    
    def swap_gene(self, chromosome: Chromosome, index1: int, index2: int):
        """Swap 2 genes in the chromosome based on a randomly chosen swap type."""
        swap_types = {
            'date_day': ['time_slot_date', 'time_slot_day'],
            'assistant': ['assistant'],
            'shift': ['time_slot_shift'],
            'date_day_shift': ['time_slot_date', 'time_slot_day', 'time_slot_shift'],
            'all': ['time_slot_date', 'time_slot_day', 'time_slot_shift', 'assistant']
        }
        
        swap = random.choice(list(swap_types.keys()))
        
        for key in swap_types[swap]:
            chromosome[index1][key], chromosome[index2][key] = chromosome[index2][key], chromosome[index1][key]
    
    def configure(self, **kwargs):
        '''Configure the neighborhood'''
        raise NotImplementedError("Neighborhood configuration not implemented")
    
class SwapNeighborhood(BaseNeighborhood):
    def __init__(self, name: str = "SwapNeighborhood"):
        super().__init__(name)
        self.neighborhood_size = 50  # Default neighborhood size
        
    def _generate_swap(self, chromosome: Chromosome):
        """Generate a random swap between two genes in the chromosome."""
        i, j = random.sample(range(len(chromosome)), 2)
        neighbor = chromosome.copy()
        self.swap_gene(neighbor, i, j)  # Swap the genes in place
        return neighbor, (i, j)
    
    def __call__(self, chromosome: Chromosome):
        results = []
        for _ in range(self.neighborhood_size):
            neighbor, move = self._generate_swap(chromosome)
            if self.track_moves:
                results.append((neighbor, move))
            else:
                results.append(neighbor)
        return results
    
    def configure(self, neighborhood_size=None):
        if neighborhood_size:
            self.neighborhood_size = neighborhood_size
        return self
    
class RandomSwapNeighborhood(SwapNeighborhood):
    def __init__(self):
        super().__init__("RandomSwapNeighborhood")
    
class RandomRangeSwapNeighborhood(BaseNeighborhood):
    def __init__(self):
        super().__init__("RandomRangeSwapNeighborhood")
        self.neighborhood_size_factor = 0.1
        self.range_size_factor = 0.1

    def __call__(self, chromosome: Chromosome):
        '''Generate a set of neighbor solutions by swapping a range of elements in the chromosome.'''
        neighbors = []
        neighborhood_size = int(len(chromosome) * self.neighborhood_size_factor)
        range_size = int(len(chromosome) * self.range_size_factor)
        for _ in range(neighborhood_size):
            neighbor = chromosome.copy()
            i = random.randint(0, len(chromosome) - range_size)
            j = random.randint(i, i + range_size)
            # Swap the genes data,
            self.swap_gene(neighbor, i, j)
            if self.track_moves:
                neighbors.append((neighbor, (i, j)))
            else:
                neighbors.append(neighbor)
        return neighbors
    
    
    def configure(self, neighborhood_size_factor = None, range_size_factor = None):
        self.neighborhood_size_factor = neighborhood_size_factor or self.neighborhood_size_factor
        self.range_size_factor = range_size_factor or self.range_size_factor
        return self
    
    @classmethod
    def create(cls, config: dict):
        instance = cls()
        instance.configure(**config)
        return instance
    
class DistanceSwapNeighborhood(BaseNeighborhood):
    def __init__(self):
        super().__init__("DistanceSwapNeighborhood")
        self.distance_percentage = 0.1
        self.distance_matrix = None

    def __call__(self, chromosome: Chromosome) -> List[Chromosome]:
        '''Swap genes based on the distance between the genes'''
        neighbors = []
        
        if self.distance_matrix is None:
            self.distance_matrix = self.calculate_distance_matrix(chromosome)

        # Sort the distance from the furthest to the closest
        distance = sorted(self.distance_matrix, key=lambda distance: distance[2], reverse=True)

        # Select the top 10% of the distance
        selected_distance = distance[:int(len(distance) * self.distance_percentage)]

        # Swap the genes
        for distance in selected_distance:
            neighbor = chromosome.copy()
            self.swap_gene(neighbor, distance[0], distance[1])
            if self.track_moves:
                neighbors.append((neighbor, (distance[0], distance[1])))
            else:
                neighbors.append(neighbor)
        return neighbors
    
    def calculate_distance_matrix(self, chromosome: Chromosome) -> List[List[int]]:
        '''Calculate the distance between each gene in the chromosome'''
        distance_matrix = []
        for i in range(len(chromosome)):
            for j in range(i + 1, len(chromosome)):
                distance = self.calculate_distance(chromosome[i], chromosome[j])
                distance_matrix.append([i, j, distance])
        return distance_matrix
    
    def calculate_distance(self, gene1: dict, gene2: dict) -> int:
        '''Calculate the distance between 2 genes'''
        date_difference = abs((gene1['time_slot_date'] - gene2['time_slot_date']).days)
        day_difference = abs(Constant.days.index(gene1['time_slot_day']) - Constant.days.index(gene2['time_slot_day']))
        shift_difference = abs(Constant.shifts.index(gene1['time_slot_shift']) - Constant.shifts.index(gene2['time_slot_shift']))
        return date_difference + day_difference + shift_difference

    def configure(self, distance_percentage = None):
        self.distance_percentage = distance_percentage or self.distance_percentage
        return self
    
    @classmethod
    def create(cls, config: dict):
        instance = cls()
        instance.configure(**config)
        return instance
    
    
class NeighborhoodManager:
    _ALGORITHM_MAP = {
        "swap": SwapNeighborhood,
        "random_swap": RandomSwapNeighborhood,
        "random_range_swap": RandomRangeSwapNeighborhood,
        "distance_swap": DistanceSwapNeighborhood
    }
    
    @classmethod
    def create(cls, config: dict, is_tabu: bool = False) -> BaseNeighborhood:
        '''Create the neighborhood
        args:
            neighborhood_config: dict
            is_tabu: bool = False
            '''
            
        
            
        algorithm = config['algorithm']
        neighborhood_class = cls._ALGORITHM_MAP[algorithm]
        if is_tabu and hasattr(neighborhood_class, 'with_moves'):
            
            neighborhood = neighborhood_class().with_moves()
            
           
        else:
            neighborhood = neighborhood_class()
            
        config_key = algorithm
        
        return neighborhood.configure(**config.get(config_key, {}))
        
        