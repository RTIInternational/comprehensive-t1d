from src.simulation.utils import *

EVENT = "insulin_dose"

IS_DETERMINISTIC = True

FACTORS = {
    "lambda_val": 0.123,
    "prev": 0.818,
    "initial": 0.0386,
    "age_entry": -0.000355,
    "diabetes_duration_entry": -0.000656,
    "step": -0.000957,
    "female": -0.0182
}


def calculate(individual, step, *_):
    explanators = 0
    explanators += FACTORS['age_entry'] * individual['age_entry']
    explanators += FACTORS['diabetes_duration_entry'] * individual['diabetes_duration_entry']
    explanators += FACTORS['female'] * individual['female']
    explanators += FACTORS["step"] * step
    explanators += FACTORS["prev"] * get_event_in_step(individual, 'insulin_dose', step - 1)
    explanators += FACTORS["initial"] * get_event_in_step(individual, 'insulin_dose', 0)

    progression = explanators + FACTORS['lambda_val']

    return rounder(progression, ndigits=2)


def modify_coefficients(data, rng):
    pass
