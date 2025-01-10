from src.simulation.utils import *

EVENT = "sbp"

IS_DETERMINISTIC = True


def calculate(individual, step, *_):
    if not has_event(individual, 'bp_treatment'):
        return get_event_in_step(individual, 'sbp_pre', step)
    else:
        return get_event_in_step(individual, 'sbp_post', step)


def modify_coefficients(data, rng):
    pass