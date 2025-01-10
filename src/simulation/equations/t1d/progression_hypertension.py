from src.simulation.utils import *

EVENT = "hypertension"

IS_DETERMINISTIC = True


def calculate(individual, step, *_):
    """
    Calculate hypertension in an individual. This is dependent on sbp and dbp
    """
    sbp = get_event_in_step(individual, 'sbp', step)
    dbp = get_event_in_step(individual, 'dbp', step)

    if dbp > 90 or sbp > 140 or has_event(individual, 'bp_treatment'):
        return 1

    return 0


def modify_coefficients(data, rng):
    pass
