from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "cvd_mace"

FACTORS = {
    "intercept": [-16.71950, 1.33807],
    "shape": [1.36022, 0.12924],
    "age_entry": [0.09133, 0.01439],
    "diabetes_duration_entry": [0.06910, 0.01535],
    "female": [-0.07853, 0.17157],
    "curr_smoker": [0.57946, 0.18539],
    "curr_trig": [0.42644, 0.15160],
    "ever_hypertension": [0.38351, 0.20851],
    "lag_tv_amputation": [0.80827, 0.41390],
    "lag_tv_esrd": [0.55564, 0.38039],
    "lag_tv_ma": [0.68109, 0.22252],
    "lag_tv_pdr": [0.39636, 0.21612],
    "lag_tv_ulcer": [1.24108, 0.41442],
    "twd_hba1c": [0.26249, 0.07035],
    "twd_ldl": [0.00202, 0.00328],
    "twd_hr": [0.02379, 0.01103]
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
    explanators += MODIFIED_FACTORS["curr_trig"][0] * get_event_in_step(individual, 'trig', step)
    explanators += MODIFIED_FACTORS["twd_hba1c"][0] * time_weighted_risk_factor(individual, 'hba1c')
    explanators += MODIFIED_FACTORS["twd_ldl"][0] * time_weighted_risk_factor(individual, 'ldl')
    explanators += MODIFIED_FACTORS["twd_hr"][0] * time_weighted_risk_factor(individual, 'hr')

    if has_event(individual, 'hypertension'):
        explanators += MODIFIED_FACTORS["ever_hypertension"][0]

    if has_history(individual, 'amputation', step):
        explanators += MODIFIED_FACTORS["lag_tv_amputation"][0]

    if has_history(individual, 'esrd', step):
        explanators += MODIFIED_FACTORS["lag_tv_esrd"][0]

    if has_history(individual, 'macroalbuminuria', step):
        explanators += MODIFIED_FACTORS["lag_tv_ma"][0]

    if has_history(individual, 'pdr', step):
        explanators += MODIFIED_FACTORS["lag_tv_pdr"][0]

    if has_acute_event(individual, 'ulcer', step):
        explanators += MODIFIED_FACTORS["lag_tv_ulcer"][0]

    if get_event_in_step(individual, 'smoker', step):
        explanators += MODIFIED_FACTORS["curr_smoker"][0]

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
    complication_multiplier = custom_values['complication_multipliers']['cvd_mace multiplier']
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