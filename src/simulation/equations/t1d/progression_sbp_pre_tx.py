from src.simulation.utils import *

EVENT = "sbp_pre"

IS_DETERMINISTIC = True

FACTORS = {
    "intercept": 29.16077,
    "prev": 0.6419806,
    "initial": 0.0889154,
    "age_entry": 0.0889167,
    "diabetes_duration_entry": -0.0429529,
    "step": 0.089427,
    "female": -1.216122
}


def calculate(individual, step, *_):
    if has_event(individual, 'bp_treatment'):
        return 0

    explanators = 0
    explanators += FACTORS['age_entry'] * individual['age_entry']
    explanators += FACTORS['diabetes_duration_entry'] * individual['diabetes_duration_entry']
    explanators += FACTORS['female'] * individual['female']
    explanators += FACTORS["step"] * step
    explanators += FACTORS["prev"] * get_event_in_step(individual, 'sbp', step - 1)
    explanators += FACTORS["initial"] * get_event_in_step(individual, 'sbp', 0)

    progression = explanators + FACTORS['intercept']

    return rounder(progression, ndigits=2)


def modify_coefficients(data, rng):
    pass
