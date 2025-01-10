from src.simulation.utils import *

EVENT = "dbp_pre"

IS_DETERMINISTIC = True

FACTORS = {
    "intercept": 24.77545,
    "prev": 0.5921088,
    "initial": 0.0898982,
    "age_entry": -0.0085304,
    "diabetes_duration_entry": -0.0763201,
    "step": -0.0238337,
    "female": -1.318206
}


def calculate(individual, step, *_):
    if has_event(individual, 'bp_treatment'):
        return 0

    explanators = 0
    explanators += FACTORS['age_entry'] * individual['age_entry']
    explanators += FACTORS['diabetes_duration_entry'] * individual['diabetes_duration_entry']
    explanators += FACTORS['female'] * individual['female']
    explanators += FACTORS["step"] * step
    explanators += FACTORS["prev"] * get_event_in_step(individual, 'dbp', step - 1)
    explanators += FACTORS["initial"] * get_event_in_step(individual, 'dbp', 0)

    progression = explanators + FACTORS['intercept']

    return rounder(progression, ndigits=2)


def modify_coefficients(data, rng):
    pass