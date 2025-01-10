from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "mace_death"

FACTORS = {'fixed_value': 0.215}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, *_):
    """
    Calculate probability of death
    """

    if has_event_in_step(individual, 'cvd_mace', step):
        mortality_multipliers = custom_values['mortality_multipliers']
        multiplier = mortality_multipliers['Equation 2']
        return MODIFIED_FACTORS['fixed_value'] * multiplier
    return 0


def modify_coefficients(data, rng):
    pass
