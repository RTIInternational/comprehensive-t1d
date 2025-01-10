from src.simulation.utils import *

EVENT = "bmi"

IS_DETERMINISTIC = True

FACTORS = {
    "intercept": 0.702,
    "prev": 0.949,
    "initial": 0.0438,
    "age_entry": -0.00538,
    "diabetes_duration_entry": -0.00767,
    "step": -0.00133,
    "female": -0.00779
}


def calculate(individual, step, *_):
    explanators = 0
    explanators += FACTORS['age_entry'] * individual['age_entry']
    explanators += FACTORS['diabetes_duration_entry'] * individual['diabetes_duration_entry']
    explanators += FACTORS['female'] * individual['female']
    explanators += FACTORS["step"] * step
    explanators += FACTORS["prev"] * get_event_in_step(individual, 'bmi', step - 1)
    explanators += FACTORS["initial"] * get_event_in_step(individual, 'bmi', 0)

    progression = explanators + FACTORS['intercept']

    return rounder(progression, ndigits=2)

def modify_coefficients(data, rng):
    pass
