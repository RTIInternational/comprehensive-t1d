from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "npdr"

FACTORS = {
    "intercept": [-9.72959, 0.54355],
    "shape": [1.01234, 0.03007],
    "age_entry": [-0.00115, 0.00466],
    "diabetes_duration_entry": [0.16669, 0.00907],
    "female": [-0.15214, 0.06919],
    "ever_smoker": [0.21851, 0.07589],
    "curr_hr": [0.00709, 0.00321],
    "mean_bmi": [0.02412, 0.01106],
    "mean_dbp": [0.01961, 0.00511],
    "mean_hba1c": [0.35610, 0.02267],
    "mean_trig": [0.25627, 0.08043]
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention, rng):
    """
    Calculate probability of NPDR
    """

    if has_event(individual, 'npdr'):
        return 1

    explanators = 0
    explanators += MODIFIED_FACTORS['age_entry'][0] * individual['age_entry']
    explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * individual['diabetes_duration_entry']
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS['curr_hr'][0] * get_event_in_step(individual, 'hr', step)
    explanators += MODIFIED_FACTORS['mean_bmi'][0] * mean_risk_factor(individual, 'bmi')
    explanators += MODIFIED_FACTORS['mean_dbp'][0] * mean_risk_factor(individual, 'dbp')
    explanators += MODIFIED_FACTORS['mean_hba1c'][0] * mean_risk_factor(individual, 'hba1c')
    explanators += MODIFIED_FACTORS['mean_trig'][0] * mean_risk_factor(individual, 'trig')

    if has_event(individual, 'smoker'):
        explanators += MODIFIED_FACTORS['ever_smoker'][0]

    total_risk_reduction = 0
    if intervention and is_intervention:
        risk_reductions = intervention['risk reductions']
        count = 1
        for intervent, reduction in risk_reductions.items():
            
            if intervent == 'bp_control_intervention':
                if get_event_in_step(individual, 'sbp', step) > intervention['sbp_condition']:
                    total_risk_reduction += math.pow(reduction, count)
                    count += 1
            elif intervent == 'cholesterol_control_intervention':
                if individual['age'] >= intervention['cholesterol min age']:
                    total_risk_reduction += math.pow(reduction, count)
                    count += 1
            else:
                total_risk_reduction += math.pow(reduction, count)
                count += 1

    shape = MODIFIED_FACTORS['shape'][0]
    intercept = MODIFIED_FACTORS['intercept'][0]
    complication_multiplier = custom_values['complication_multipliers']['npdr multiplier']
    complication_prob = calculate_weibull_prob_t1d(shape, explanators, step, intercept,
                                                   complication_multiplier, total_risk_reduction)

    return rounder(complication_prob)


def modify_coefficients(data, rng):
    psa_factor = data
    global MODIFIED_FACTORS
    if psa_factor:
        modified_factors_dict = {}
        for factor, value in FACTORS.items():
            new_value = normal.model(rng, value[0], value[1], 4)
            modified_factors_dict[factor] = [new_value]
        MODIFIED_FACTORS = modified_factors_dict