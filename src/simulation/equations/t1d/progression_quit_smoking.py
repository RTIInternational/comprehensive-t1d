from src.simulation.utils import *

EVENT = "quit_smoking"


def calculate(individual, step, _, intervention, has_intervention, rng):
    """predicts quitting"""

    # individual quit smoking in the previous time step
    # individuals are allowed to oscillate between quitting and smoking ... if we decide to not allow that this
    # needs to uncommented
    # if has_history(individual, 'quit_smoking', step):
    #     return 1

    if intervention and has_intervention:
        if get_event_in_step(individual, 'smoker', step - 1):
            intervention_data = intervention['smoking_control_intervention'][0]
            progression_prob = intervention_data['probability of quitting']
        # not a smoker in previous time step
        else:
            progression_prob = 0
    # no intervention
    else:
        progression_prob = 0

    return rounder(progression_prob, ndigits=2)


def modify_coefficients(data, rng):
    pass
