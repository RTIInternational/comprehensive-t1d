from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "dka"

FACTORS = {
    "intercept": [-9.65408, 0.83534],
    "shape": [0.92328, 0.04863],
    "age_entry": [-0.0004080, 0.00767],
    "diabetes_duration_entry": [-0.05529, 0.01114],
    "female": [0.79770, 0.11568],
    "curr_smoker": [0.30160, 0.13068],
    "mean_dbp": [0.02973, 0.00818],
    "mean_hba1c": [0.22076, 0.03860],
    "mean_trig": [0.24277, 0.13215],
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention, rng):
    """
    Calculate probability of DKA
    """

    if has_event(individual, 'dka'):
        return 1

    explanators = 0
    explanators += MODIFIED_FACTORS['age_entry'][0] * individual['age_entry']
    explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * individual['diabetes_duration_entry']
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS['mean_dbp'][0] * mean_risk_factor(individual, 'dbp')
    explanators += MODIFIED_FACTORS['mean_hba1c'][0] * mean_risk_factor(individual, 'hba1c')
    explanators += MODIFIED_FACTORS['mean_trig'][0] * mean_risk_factor(individual, 'trig')

    if get_event_in_step(individual, 'smoker', step):
        explanators += MODIFIED_FACTORS['curr_smoker'][0]

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
    complication_multiplier = custom_values['complication_multipliers']['dka multiplier']
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