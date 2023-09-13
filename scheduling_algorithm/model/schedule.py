#schedule.py
#Description: This file contains the Schedule class, which is used to generate a schedule chromosome
#             and to evaluate the fitness of a schedule chromosome.

import random
import copy
import numpy as np
from scheduling_data.models import Laboratory, Module, Chapter, Group, Participant, Assistant
