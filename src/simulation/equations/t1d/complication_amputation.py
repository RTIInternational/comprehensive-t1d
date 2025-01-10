from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "amputation"

FACTORS = {
    "intercept": [-21.45157, 2.25181],
    "shape": [2.27974, 0.29770],
    "age_entry": [0.05222, 0.01974],
    "diabetes_duration_entry": [0.04404, 0.02302],
    "female": [-0.67355, 0.30221],
    "curr_smoker": [0.48390, 0.28560],
    "curr_insulin_dose": [1.11176, 0.45148],
    "lag_tv_csme": [0.57939, 0.29130],
    "lag_tv_cvd": [0.58108, 0.56683],
    "lag_tv_esrd": [1.48145, 0.42835],
    "lag_tv_hypoglycemia": [0.49831, 0.31906],
    "lag_tv_ma": [0.74967, 0.32406],
    "lag_tv_ulcer": [2.36226, 0.37790],
    "mean_hba1c": [0.50359, 0.11069],
    "mean_hr": [0.04646, 0.01952]
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention, rng):
    """
    Calculate probability of an amputation.
    """

    if has_event(individual, 'amputation'):
        return 1

    explanators = 0
    explanators += MODIFIED_FACTORS['age_entry'][0] * individual['age_entry']
    explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * individual['diabetes_duration_entry']
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS['curr_insulin_dose'][0] * get_event_in_step(individual, 'insulin_dose', step)
    explanators += MODIFIED_FACTORS['mean_hba1c'][0] * mean_risk_factor(individual, 'hba1c')
    explanators += MODIFIED_FACTORS['mean_hr'][0] * mean_risk_factor(individual, 'hr')

    if has_history(individual, 'csme', step):
        explanators += MODIFIED_FACTORS['lag_tv_csme'][0]

    if has_acute_event(individual, 'cvd', step):
        explanators += MODIFIED_FACTORS['lag_tv_cvd'][0]

    if has_history(individual, 'esrd', step):
        explanators += MODIFIED_FACTORS['lag_tv_esrd'][0]

    if has_acute_event(individual, 'hypoglycemia', step):
        explanators += MODIFIED_FACTORS['lag_tv_hypoglycemia'][0]

    if has_history(individual, 'macroalbuminuria', step):
        explanators += MODIFIED_FACTORS['lag_tv_ma'][0]

    if has_acute_event(individual, 'ulcer', step):
        explanators += MODIFIED_FACTORS['lag_tv_ulcer'][0]

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
    complication_multiplier = custom_values['complication_multipliers']['amputation multiplier']
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
