from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "ulcer"

FACTORS = {
    "intercept": [-12.58304, 1.40071],
    "shape": [0.66105, 0.08271],
    "age_entry_log": [0.86588, 0.31393],
    "diabetes_duration_entry": [0.00605, 0.01551],
    "female": [-0.16699, 0.17106],
    "curr_hr": [0.02303, 0.00736],
    "mean_hba1c": [0.39987, 0.06263],
    "mean_hba1c_pre10": [0.34243, 0.05838],
    "ever_hypertension": [0.46974, 0.21213],
    "lag_tv_csme": [0.27181, 0.22566],
    "lag_tv_dpn": [0.60511, 0.32312],
    "lag_tv_ma": [0.50967, 0.24160]

}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention, rng):
    """
    Calculate probability of an ulcer
    """

    if has_event(individual, 'ulcer'):
        return 1

    explanators = 0
    explanators += MODIFIED_FACTORS['age_entry_log'][0] * math.log(individual['age_entry'])
    explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * individual['diabetes_duration_entry']
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS['curr_hr'][0] * get_event_in_step(individual, 'hr', step)

    if step < 10:
        explanators += MODIFIED_FACTORS['mean_hba1c_pre10'][0] * mean_risk_factor(individual, 'hba1c')
    else:
        explanators += MODIFIED_FACTORS['mean_hba1c'][0] * mean_risk_factor(individual, 'hba1c')

    if has_event(individual, 'hypertension'):
        explanators += MODIFIED_FACTORS['ever_hypertension'][0]

    if has_history(individual, 'csme', step):
        explanators += MODIFIED_FACTORS['lag_tv_csme'][0]

    if has_acute_event(individual, 'dpn', step):
        explanators += MODIFIED_FACTORS['lag_tv_dpn'][0]

    if has_history(individual, 'macroalbuminuria', step):
        explanators += MODIFIED_FACTORS['lag_tv_ma'][0]

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
    complication_multiplier = custom_values['complication_multipliers']['ulcer multiplier']
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