#schedule.py
#Description: This file contains the Schedule class, which is used to generate a schedule chromosome
#             and to evaluate the fitness of a schedule chromosome.

# Each day has 6 shifts (Shift 1 to Shift 6).
# Each assistant can assist up to 3 groups on one shift.
# One laboratory can have up to 2 classes at the same time.
# We'll represent each assistant's assignment with a unique identifier.
# We'll use "0" to denote no class in a specific shift.
# Each participant and assistant already have their own course assigned, they must find free time between them so than can make a schedule for practicum.
# Each participant and assistant have a specific laboratory assigned, they must find free time between them so than can make a schedule for practicum.
# Each participant have a specific group assigned, they must find free time between them so than can make a schedule for practicum.

import random
import copy
import numpy as np
from scheduling_data.models import Laboratory, Module, Chapter, Group, Participant, Assistant

class ScheduleChromosome:
    def __init__(self, configuration):
        self._configuration = configuration
        self._fitness = 0

        #Time-space representation of the schedule
        self._schedule = np.zeros((self._configuration.get_number_of_days(), self._configuration.get_number_of_shifts(), self._configuration.get_number_of_laboratories()), dtype=int)
        
