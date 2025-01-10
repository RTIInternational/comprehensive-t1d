import numpy as np

from src.simulation.utils import *
from src.simulation.equations.models import *
from copy import deepcopy

EVENT = "non_cvd_death"

FACTORS = {
    "intercept": [-17.93622, 1.329928],
    "rho_val": [0.1101173, 0.0148709],
    "age_entry": [0.0824034, 0.0150548],
    "diabetes_duration_entry": [0.0181183, 0.017421],
    "female": [-0.4331695, 0.2061673],
    "curr_hr": [0.0304241, 0.0081852],
    "curr_trig": [0.2466859, 0.1791741],
    "lag_tv_esrd": [1.073115, 0.3271868],
    "lag_tv_gfr": [0.2838462, 0.2266435],
    "lag_tv_mi": [0.390968, 0.0874074],
    "twd_hba1c": [0.390968, 0.0874074],
    "twd_insulin_dose": [1.557231, 0.5110887]
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, *_):
    """
    Calculate probability of death
    """

    if has_event(individual, 'cvd'):
        return 0

    explanators = 0
    explanators += MODIFIED_FACTORS['age_entry'][0] * individual['age_entry']
    explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * individual['diabetes_duration_entry']
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS["curr_hr"][0] * get_event_in_step(individual, 'hr', step)
    explanators += MODIFIED_FACTORS["curr_trig"][0] * get_event_in_step(individual, 'trig', step)
    explanators += MODIFIED_FACTORS["twd_hba1c"][0] * time_weighted_risk_factor(individual, 'hba1c')
    explanators += MODIFIED_FACTORS["twd_insulin_dose"][0] * time_weighted_risk_factor(individual, 'insulin_dose')

    if has_history(individual, 'esrd', step):
        explanators += MODIFIED_FACTORS["lag_tv_esrd"][0]

    if has_history(individual, 'gfr', step):
        explanators += MODIFIED_FACTORS["lag_tv_gfr"][0]

    if has_history(individual, 'microalbuminuria', step):
        explanators += MODIFIED_FACTORS["lag_tv_mi"][0]

    integrated_hazard_t = gompertz.model(explanators, step - 1, MODIFIED_FACTORS['intercept'][0], MODIFIED_FACTORS['rho_val'][0])
    integrated_hazard_t1 = gompertz.model(explanators, step, MODIFIED_FACTORS['intercept'][0], MODIFIED_FACTORS['rho_val'][0])

    mortality_multipliers = custom_values['mortality_multipliers']
    multiplier = mortality_multipliers['Equation 1']

    complication_prob = 1 - np.exp(multiplier * (integrated_hazard_t - integrated_hazard_t1))

    return rounder(complication_prob)


def modify_coefficients(data, rng):
    psa_factor = data
    global MODIFIED_FACTORS
    if psa_factor:
        modified_factors_dict = {}
        for factor, value in FACTORS.items():
            new_value = normal.model(rng, value[0], value[1], 4)
            modified_factors_dict[factor] = [new_value]
        MODIFIED_FACTORS = modified_factors_dict