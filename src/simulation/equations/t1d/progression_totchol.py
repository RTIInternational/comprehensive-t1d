import numpy as np
from src.simulation.utils import *

EVENT = "totchol"

IS_DETERMINISTIC = True


def calculate(individual, step, _, intervention, has_intervention, rng):
    """
    Calculate total cholesterol in an individual. This is dependent on hdl, ldl
    and triglycerides
    """
    hdl = get_event_in_step(individual, 'hdl', step)
    ldl = get_event_in_step(individual, 'ldl', step)
    trig = get_event_in_step(individual, 'trig', step)

    return rounder(hdl + ldl + np.exp(trig) / 5, ndigits=2)


def modify_coefficients(data, rng):
    pass
