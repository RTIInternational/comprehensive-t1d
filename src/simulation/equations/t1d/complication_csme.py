from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "csme"

FACTORS = {
    "intercept": [-11.86074, 0.63436],
    "shape": [1.00658, 0.06929],
    "age_entry": [0.02847, 0.00709],
    "diabetes_duration_entry": [0.02361, 0.01173],
    "diabetes_duration_entry_pre7": [0.05853, 0.01011],
    "female": [-0.28556, 0.09316],
    "curr_hr": [0.00943, 0.00412],
    "curr_insulin_dose": [0.44166, 0.17898],
    "lag_tv_npdr": [1.30084, 0.13709],
    "lag_tv_pdr": [0.41313, 0.13471],
    "mean_bmi": [0.03086, 0.01370],
    "mean_hba1c": [0.39592, 0.03322],
    "mean_ldl": [0.00557, 0.00172]
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention, rng):
    """
    Calculate probability of clinically significant macular edema.
    """

    if has_event(individual, 'csme'):
        return 1

    explanators = 0
    explanators += MODIFIED_FACTORS['age_entry'][0] * individual['age_entry']
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS["curr_hr"][0] * get_event_in_step(individual, 'hr', step)
    explanators += MODIFIED_FACTORS["curr_insulin_dose"][0] * get_event_in_step(individual, 'insulin_dose', step)
    explanators += MODIFIED_FACTORS["mean_bmi"][0] * mean_risk_factor(individual, 'bmi')
    explanators += MODIFIED_FACTORS["mean_hba1c"][0] * mean_risk_factor(individual, 'hba1c')
    explanators += MODIFIED_FACTORS["mean_ldl"][0] * mean_risk_factor(individual, 'ldl')

    if step < 7:
        explanators += MODIFIED_FACTORS['diabetes_duration_entry_pre7'][0] * individual['diabetes_duration_entry']
    else:
        explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * individual['diabetes_duration_entry']

    if has_history(individual, 'npdr', step):
        explanators += MODIFIED_FACTORS["lag_tv_npdr"][0]

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
    complication_multiplier = custom_values['complication_multipliers']['csme multiplier']
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