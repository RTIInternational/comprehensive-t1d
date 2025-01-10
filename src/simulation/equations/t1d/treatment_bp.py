import numpy as np

from src.simulation.utils import *
from src.simulation.equations.models import *

EVENT = "bp_treatment"

FACTORS = {
    "intercept": -7.72022,
    "rho_val": 1.279126,
    "age_entry": 0.0121626,
    "lagged_sbp": 0.0285132
}


def calculate(individual, step, *_):
    """
    Calculate application of blood pressure treatement.
    """

    if has_event(individual, 'bp_treatment'):
        return 1

    explanators = 0
    explanators += FACTORS['age_entry'] * individual['age_entry']
    # note step - 1 as the third argument here- we update sbp later so we need
    # to look back to the previous step to get the correct sbp
    explanators += FACTORS["lagged_sbp"] * get_event_in_step(individual, 'sbp', step - 1)

    integrated_hazard_t = weibull.model(explanators, step - 1, FACTORS['intercept'], FACTORS['rho_val'])
    integrated_hazard_t1 = weibull.model(explanators, step, FACTORS['intercept'], FACTORS['rho_val'])

    complication_prob = 1 - np.exp(integrated_hazard_t - integrated_hazard_t1)

    return rounder(complication_prob, ndigits=2)


def modify_coefficients(data, rng):
    pass