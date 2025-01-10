from src.simulation.utils import *
from src.simulation.equations.models import *

EVENT = "smoker"

FACTORS = {
    "intercept": -3.742,
    "prev": 5.49,
    "initial": 1.663,
    "age_entry": -0.00999,
    "diabetes_duration_entry": -0.0138,
    "step": -0.0198,
    "female": 0.0491
}


def calculate(individual, step, *_):
    """predicts smoking"""

    # individual quit smoking in the previous time step
    # individuals are allowed to oscillate between quitting and smoking ... if an individual quits in t6, they may
    # pick up smoking again in t7
    if get_event_in_step(individual, 'quit_smoking', step - 1):
        return 0

    # individual keeps smoking
    if get_event_in_step(individual, 'smoker', step - 1):
        return 1

    explanators = 0
    explanators += FACTORS['age_entry'] * individual['age_entry']
    explanators += FACTORS['diabetes_duration_entry'] * individual['diabetes_duration_entry']
    explanators += FACTORS['female'] * individual['female']
    explanators += FACTORS["step"] * step
    explanators += FACTORS["prev"] * get_event_in_step(individual, 'smoker', step - 1)
    explanators += FACTORS["initial"] * get_event_in_step(individual, 'smoker', 0)

    progression_prob = logistic.model(explanators, FACTORS['intercept'])

    return rounder(progression_prob, ndigits=2)


def modify_coefficients(data, rng):
    pass