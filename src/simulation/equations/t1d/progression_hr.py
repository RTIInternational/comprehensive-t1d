from src.simulation.utils import *

EVENT = "hr"

IS_DETERMINISTIC = True

FACTORS = {
    "intercept": 21.29,
    "prev": 0.619,
    "initial": 0.0982,
    "age_entry": -0.0356,
    "diabetes_duration_entry": 0.0024,
    "step": -0.0249,
    "female": 0.486,
}


def calculate(individual, step, *_):
    explanators = 0
    explanators += FACTORS['age_entry'] * individual['age_entry']
    explanators += FACTORS['diabetes_duration_entry'] * individual['diabetes_duration_entry']
    explanators += FACTORS['female'] * individual['female']
    explanators += FACTORS["step"] * step
    explanators += FACTORS["prev"] * get_event_in_step(individual, 'hr', step - 1)
    explanators += FACTORS["initial"] * get_event_in_step(individual, 'hr', 0)

    progression = explanators + FACTORS['intercept']

    return rounder(progression, ndigits=2)


def modify_coefficients(data, rng):
    pass
