import numpy as np

from src.simulation.utils import *
from src.simulation.equations.models import *

EVENT = "lipid_treatment"

FACTORS = {
    "intercept": -9.296846,
    "rho_val": 1.577264,
    "age_entry": 0.0531668,
    "lagged_ldl": 0.0181986,
}


def calculate(individual, step, *_):
    """
    Calculate application of lipid treatement.
    """

    if has_event(individual, 'lipid_treatment'):
        return 1

    explanators = 0
    explanators += FACTORS['age_entry'] * individual['age_entry']
    # note step - 1 as the third argument here- we update ldl later so we need
    # to look back to the previous step to get the correct ldl
    explanators += FACTORS["lagged_ldl"] * get_event_in_step(individual, 'ldl', step - 1)

    integrated_hazard_t = weibull.model(explanators, step - 1, FACTORS['intercept'], FACTORS['rho_val'])
    integrated_hazard_t1 = weibull.model(explanators, step, FACTORS['intercept'], FACTORS['rho_val'])

    complication_prob = 1 - np.exp(integrated_hazard_t - integrated_hazard_t1)

    return rounder(complication_prob, ndigits=2)


def modify_coefficients(data, rng):
    pass