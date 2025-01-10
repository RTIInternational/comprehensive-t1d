from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "microalbuminuria"

FACTORS = {
    "intercept": [-13.31157, 0.82578],
    "shape": [0.82168, 0.05955],
    "age_entry": [-0.01666, 0.00772],
    "diabetes_duration_entry": [0.03474, 0.00962],
    "has_secondary_ed": [-0.21459, 0.11378],
    "female": [-0.26173, 0.10178],
    "race": [-0.64668, 0.20953],
    "curr_sbp": [0.02002, 0.00416],
    "curr_hr": [0.02058, 0.00439],
    "curr_smoker": [0.35219, 0.11147],
    "twd_hba1c": [0.48801, 0.03554],
    "twd_hba1c_pre7": [0.47882, 0.03255],
    "lag_tv_amputation": [1.18332, 0.45452],
    "lag_tv_gfr": [1.12824, 0.48802],
    "lag_tv_npdr": [0.63450, 0.12237],
    "mean_dbp": [0.01032, 0.00816],
    "mean_trig": [0.32985, 0.11091],
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention, rng):
    """
    Calculate probability of microalbuminuria
    """
    if has_event(individual, 'microalbuminuria'):
        return 1

    explanators = 0
    explanators += MODIFIED_FACTORS['age_entry'][0] * individual['age_entry']
    explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * individual['diabetes_duration_entry']
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS['has_secondary_ed'][0] * individual['has_secondary_ed']
    explanators += MODIFIED_FACTORS['race'][0] * individual['race']
    explanators += MODIFIED_FACTORS['curr_sbp'][0] * get_event_in_step(individual, 'sbp', step)
    explanators += MODIFIED_FACTORS['curr_hr'][0] * get_event_in_step(individual, 'hr', step)
    explanators += MODIFIED_FACTORS['curr_smoker'][0] * get_event_in_step(individual, 'smoker', step)
    explanators += MODIFIED_FACTORS['mean_dbp'][0] * mean_risk_factor(individual, 'dbp')
    explanators += MODIFIED_FACTORS['mean_trig'][0] * mean_risk_factor(individual, 'trig')

    if step < 7:
        explanators += MODIFIED_FACTORS['twd_hba1c_pre7'][0] * mean_risk_factor(individual, 'hba1c')
    else:
        explanators += MODIFIED_FACTORS['twd_hba1c'][0] * mean_risk_factor(individual, 'hba1c')

    if has_history(individual, 'amputation', step):
        explanators += MODIFIED_FACTORS['lag_tv_amputation'][0]

    if has_history(individual, 'gfr', step):
        explanators += MODIFIED_FACTORS['lag_tv_gfr'][0]

    if has_history(individual, 'npdr', step):
        explanators += MODIFIED_FACTORS['lag_tv_npdr'][0]

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
    complication_multiplier = custom_values['complication_multipliers']['microalbuminuria multiplier']
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