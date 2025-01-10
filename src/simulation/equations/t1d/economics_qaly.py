from src.simulation.utils import *

EVENT = "qaly"

IS_DETERMINISTIC = True

BEHAVIOR = 'APPEND'


EVENTS = ["microalbuminuria", "macroalbuminuria", "gfr", "esrd", "npdr",
          "pdr", "amputation", "csme", "cvd_mace", "cvd_non_mace", "dpn",
          "hypoglycemia", "dka", "ulcer"]

DEMOGRAPHIC_EVENTS = ["age", "female", "diabetes_duration_entry"]


def calculate(individual, step, economics, *_):
    custom_disutilities = economics['disutilities']

    discount_value = custom_disutilities['qaly discount factor']
    discount_factor = get_discount(discount_value, step)

    # constant term in variable Excel sheet
    qaly = custom_disutilities['base qaly']

    for event in EVENTS:
        # an acute event implies that you have no history of it; chronic events always return 1,so we need to exclude
        # them here by checking for history
        if has_event_in_step(individual, event, step) and not has_history(individual, event, step):
            qaly += custom_disutilities[event][0]
        if has_history(individual, event, step):
            qaly += custom_disutilities[event][1]

    for event in DEMOGRAPHIC_EVENTS:
        qaly += custom_disutilities[event] * individual[event]

    discounted_qaly = qaly * discount_factor

    return rounder(discounted_qaly, 4)


def modify_coefficients(data, rng):
    pass