from src.simulation.utils import *

EVENT = "cvd"


def calculate(individual, step, *_):
    """
    Calculate aggregate cvd. This equation is dependent on cvd_mace and cvd_non_mace
    """
    if (
        has_event_in_step(individual, 'cvd_mace', step) or
        has_event_in_step(individual, 'cvd_non_mace', step)
    ):
        return 1

    return 0


def modify_coefficients(data, rng):
    pass