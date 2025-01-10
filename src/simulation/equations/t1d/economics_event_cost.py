from src.simulation.utils import *

EVENT = "event_cost"

IS_DETERMINISTIC = True

BEHAVIOR = 'APPEND'

EVENTS = [
    'microalbuminuria', 'macroalbuminuria', 'gfr', 'esrd', 'npdr',
    'pdr', 'amputation', 'csme', 'cvd_mace', 'cvd_non_mace', 'dpn',
    'hypoglycemia', 'dka', 'ulcer', 'blindness'
]


def calculate(individual, step, economics, interventions, has_intervention, rng):

    if individual['age'] > 65 and economics['include_medicare']:
        custom_costs = economics['costs_medicare']
    else:
        custom_costs = economics['costs']

    # time adjusted discount
    discount_factor = get_discount(custom_costs['cost discount factor'], step)

    event_cost_component = 0
    for event in EVENTS:
        # an acute event implies that you have no history of it; chronic events always return 1,so we need to exclude
        # them here by checking for history
        if has_event_in_step(individual, event, step) and not has_history(individual, event, step):
            event_cost_component += custom_costs[event][0]
        if has_history(individual, event, step):
            event_cost_component += custom_costs[event][1]

    if has_event_in_step(individual, 'death', step):
        event_cost_component += custom_costs['death_cost']

    discounted_overall_cost = event_cost_component * discount_factor

    return rounder(discounted_overall_cost, 2)


def modify_coefficients(data, rng):
    pass