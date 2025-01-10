from src.simulation.utils import *
from src.simulation.equations.models import uniform
import math

EVENT = "depression"

def calculate(individual, step, custom_values, intervention, is_intervention, rng=None):

    if has_event(individual, 'depression'):
        return 1

    cointoss_prob = rng.random()
    # based on Rotella and Mannucci (2013)
    if 0.016 >= cointoss_prob:
        return 1
    return 0


def modify_coefficients(data, rng):
    pass

