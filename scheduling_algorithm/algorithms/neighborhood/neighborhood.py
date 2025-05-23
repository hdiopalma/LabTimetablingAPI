import random
from typing import List

from scheduling_algorithm.structure import Chromosome
from scheduling_algorithm.data_parser import Constant

def swap_gene(chromosome: Chromosome, index1: int, index2: int):
    '''Swap 2 genes in the chromosome'''
    swap_type = ['date_day', 'assistant', 'shift', 'all', 'date_day_shift']
    swap = random.choice(swap_type)
    
    # Template buat nanti kalo misalkan generasi jadwal ngga dibagi per module tapi sekaligus.
            # while True:
            #     if neighbor[i]['module'] == neighbor[j]['module']:
            #         pass
            
            # Swap the genes data, since there's two indepentent variables, the swap is decided using probability.
    
    if swap == 'date_day':
        chromosome[index1]['time_slot_date'], chromosome[index2]['time_slot_date'] = chromosome[index2]['time_slot_date'], chromosome[index1]['time_slot_date']
        chromosome[index1]['time_slot_day'], chromosome[index2]['time_slot_day'] = chromosome[index2]['time_slot_day'], chromosome[index1]['time_slot_day']
    elif swap == 'assistant':
        chromosome[index1]['assistant'], chromosome[index2]['assistant'] = chromosome[index2]['assistant'], chromosome[index1]['assistant']
    elif swap == 'shift':
        chromosome[index1]['time_slot_shift'], chromosome[index2]['time_slot_shift'] = chromosome[index2]['time_slot_shift'], chromosome[index1]['time_slot_shift']
    elif swap == 'date_day_shift':
        chromosome[index1]['time_slot_date'], chromosome[index2]['time_slot_date'] = chromosome[index2]['time_slot_date'], chromosome[index1]['time_slot_date']
        chromosome[index1]['time_slot_day'], chromosome[index2]['time_slot_day'] = chromosome[index2]['time_slot_day'], chromosome[index1]['time_slot_day']
        chromosome[index1]['time_slot_shift'], chromosome[index2]['time_slot_shift'] = chromosome[index2]['time_slot_shift'], chromosome[index1]['time_slot_shift']
    else:
        chromosome[index1]['time_slot_date'], chromosome[index2]['time_slot_date'] = chromosome[index2]['time_slot_date'], chromosome[index1]['time_slot_date']
        chromosome[index1]['time_slot_day'], chromosome[index2]['time_slot_day'] = chromosome[index2]['time_slot_day'], chromosome[index1]['time_slot_day']
        chromosome[index1]['time_slot_shift'], chromosome[index2]['time_slot_shift'] = chromosome[index2]['time_slot_shift'], chromosome[index1]['time_slot_shift']
        chromosome[index1]['assistant'], chromosome[index2]['assistant'] = chromosome[index2]['assistant'], chromosome[index1]['assistant']

class BaseNeighborhood:
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"Neighborhood(name={self.name})"
    
    def __repr__(self):
        return self.__str__()
    
    def __call__(self, chromosome: Chromosome):
        raise NotImplementedError("Neighborhood function not implemented")
    
    def configure(self, **kwargs):
        '''Configure the neighborhood'''
        raise NotImplementedError("Neighborhood configuration not implemented")
    
class NeighborhoodManager:
    def __init__(self, neighborhood: BaseNeighborhood):
        self.neighborhood = neighborhood
    
    def __call__(self, chromosome: Chromosome):
        return self.neighborhood(chromosome)
    
    def configure(self, **kwargs):
        self.neighborhood.configure(**kwargs)
        return self
    
    def __str__(self):
        return f"NeighborhoodManager(neighborhood={self.neighborhood})"
    
    def __repr__(self):
        return self.__str__()
    
    @classmethod
    def create(cls, neighborhood_config: dict):
        '''Create the neighborhood
        args:
            neighborhood_config: dict'''
        neighborhood = neighborhood_config['neighborhood']
        if neighborhood == "SwapNeighborhood":
            return SwapNeighborhood()
        elif neighborhood == "RandomSwapNeighborhood":
            return RandomSwapNeighborhood()
        elif neighborhood == "RandomRangeSwapNeighborhood":
            return RandomRangeSwapNeighborhood()
        elif neighborhood == "DistanceSwapNeighborhood":
            return DistanceSwapNeighborhood()
        else:
            raise ValueError(f"Neighborhood {neighborhood} not found")
    
class SwapNeighborhood(BaseNeighborhood):
    def __init__(self):
        super().__init__("SwapNeighborhood")
    
    def __call__(self, chromosome: Chromosome):
        '''Generate a set of neighbor solutions by swapping 2 elements in the chromosome.
        The time complexity is O(n^2) where n is the number of genes in the chromosome.
        The space complexity is O(n^2) where n is the number of genes in the chromosome.
        Hella slow and expensive.'''
        neighbors = []
        for i in range(len(chromosome)):
            for j in range(i + 1, len(chromosome)):
                neighbor = chromosome.copy()
                swap_gene(neighbor, i, j) # Swap the genes in place
                neighbors.append(neighbor)
        return neighbors
    
    @classmethod
    def create(cls, config: dict):
        return cls()
    
class RandomSwapNeighborhood(BaseNeighborhood):
    def __init__(self):
        super().__init__("RandomSwapNeighborhood")
        self.neighborhood_size = 50
    
    def __call__(self, chromosome: Chromosome):
        '''Generate a set of neighbor solutions by swapping 2 elements in the chromosome.'''
        neighbors = []
        for _ in range(self.neighborhood_size):
            neighbor = chromosome.copy()
            i, j = random.sample(range(len(chromosome)), 2)
            
            swap_gene(neighbor, i, j) # Swap the genes in place
                
            neighbors.append(neighbor)
        return neighbors
    
    def configure(self, neighborhood_size = None):
        self.neighborhood_size = neighborhood_size or self.neighborhood_size
        return self
    
    @classmethod
    def create(cls, config: dict):
        instance = cls()
        instance.configure(**config)
        return instance
    
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
            swap_gene(neighbor, i, j)
                
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
            swap_gene(neighbor, distance[0], distance[1])
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
    def __init__(self, neighborhood: BaseNeighborhood):
        self.neighborhood = neighborhood
    
    def __call__(self, chromosome: Chromosome):
        return self.neighborhood(chromosome)
    
    def configure(self, **kwargs):
        self.neighborhood.configure(**kwargs)
        return self
    
    def __str__(self):
        return f"NeighborhoodManager(neighborhood={self.neighborhood})"
    
    def __repr__(self):
        return self.__str__()
    
    @staticmethod
    def create(neighborhood_config: dict):
        '''Create the neighborhood
        args:
            neighborhood_config: dict'''
        algorithm = neighborhood_config['algorithm']
        selected_neighborhood = None
        if algorithm == "swap":
            selected_neighborhood = SwapNeighborhood.create(neighborhood_config['swap'])
        elif algorithm == "random_swap":
            selected_neighborhood = RandomSwapNeighborhood.create(neighborhood_config['random_swap'])
        elif algorithm == "random_range_swap":
            selected_neighborhood = RandomRangeSwapNeighborhood.create(neighborhood_config['random_range_swap'])
        elif algorithm == "distance_swap":
            selected_neighborhood = DistanceSwapNeighborhood.create(neighborhood_config['distance_swap'])
        else:
            raise ValueError(f"Neighborhood {algorithm} not found")
        # print(f"Creating NeighborhoodManager with neighborhood: {selected_neighborhood}")
        return selected_neighborhood