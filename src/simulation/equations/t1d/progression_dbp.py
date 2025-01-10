from src.simulation.utils import *

EVENT = "dbp"

IS_DETERMINISTIC = True


def calculate(individual, step, *_):
    if not has_event(individual, 'bp_treatment'):
        return get_event_in_step(individual, 'dbp_pre', step)
    else:
        return get_event_in_step(individual, 'dbp_post', step)


def modify_coefficients(data, rng):
    pass