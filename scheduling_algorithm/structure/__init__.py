from scheduling_algorithm.structure.gene import Gene
from scheduling_algorithm.structure.chromosome import Chromosome
from scheduling_algorithm.structure.population import Population
from scheduling_algorithm.structure.tabu_list import TabuList

#Simple data structure for timeslot
from collections import namedtuple
TimeSlot = namedtuple("TimeSlot", ["date", "day", "shift"])