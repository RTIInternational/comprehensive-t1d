from src.simulation.utils import *

EVENT = "dbp_post"

IS_DETERMINISTIC = True

FACTORS = {
    "intercept": 25.55175,
    "prev": 0.6204052,
    "initial": 0.0824484,
    "age_entry": -0.0845199,
    "diabetes_duration_entry": -0.0762739,
    "step": -0.0686822,
    "female": -1.119158
}


def calculate(individual, step, *_):
    if not has_event(individual, 'bp_treatment'):
        return 0

    # Macro calculations are based on the year of micro diagnosis as opposed to
    # simulation start. We use the year of micr diagnosis to update age at entry,
    # diabetes duration at entry and timestep.
    bp_tx_applied_step = get_time_of_event(individual, 'bp_treatment')
    tx_step = step - bp_tx_applied_step

    explanators = 0
    explanators += FACTORS['age_entry'] * individual['age_entry']
    explanators += FACTORS['diabetes_duration_entry'] * individual['diabetes_duration_entry']
    explanators += FACTORS['female'] * individual['female']
    explanators += FACTORS["step"] * tx_step
    explanators += FACTORS["prev"] * get_event_in_step(individual, 'dbp', step - 1)
    explanators += FACTORS["initial"] * get_event_in_step(individual, 'dbp', 0)

    progression = explanators + FACTORS['intercept']

    return rounder(progression, ndigits=2)


def modify_coefficients(data, rng):
    pass
