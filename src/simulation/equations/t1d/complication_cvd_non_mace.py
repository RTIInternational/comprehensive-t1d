from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "cvd_non_mace"

FACTORS = {
    "intercept": [-15.03773, 1.06822],
    "shape": [1.45939, 0.121],
    "age_entry": [0.06460, 0.01208],
    "diabetes_duration_entry": [0.08987, 0.01388],
    "female": [0.33242, 0.14979],
    "curr_hba1c": [0.19495, 0.04820],
    "curr_insulin_dose": [0.36299, 0.18511],
    "ever_hypertension": [0.57162, 0.17683],
    "lag_tv_amputation": [0.72635, 0.45732],
    "lag_tv_mi": [0.53336, 0.16980],
    "lag_tv_pdr": [0.29893, 0.17828],
    "mean_ldl": [0.00766, 0.00291],
    "mean_trig": [0.46267, 0.17377]
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention, rng):
    """
    Calculate probability of CVD
    """

    explanators = 0
    explanators += MODIFIED_FACTORS['age_entry'][0] * individual['age_entry']
    explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * individual['diabetes_duration_entry']
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS["curr_hba1c"][0] * get_event_in_step(individual, 'hba1c', step)
    explanators += MODIFIED_FACTORS["curr_insulin_dose"][0] * get_event_in_step(individual, 'insulin_dose', step)
    explanators += MODIFIED_FACTORS["mean_ldl"][0] * mean_risk_factor(individual, 'ldl')
    explanators += MODIFIED_FACTORS["mean_trig"][0] * mean_risk_factor(individual, 'trig')

    if has_event(individual, 'hypertension'):
        explanators += MODIFIED_FACTORS["ever_hypertension"][0]

    if has_history(individual, 'amputation', step):
        explanators += MODIFIED_FACTORS["lag_tv_amputation"][0]

    if has_history(individual, 'microalbuminuria', step):
        explanators += MODIFIED_FACTORS["lag_tv_mi"][0]

    if has_history(individual, 'pdr', step):
        explanators += MODIFIED_FACTORS["lag_tv_pdr"][0]

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
    complication_multiplier = custom_values['complication_multipliers']['cvd_non_mace multiplier']
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