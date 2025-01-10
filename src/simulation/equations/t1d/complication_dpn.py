from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "dpn"

FACTORS = {
    "intercept": [-13.88689, 1.04813],
    "shape": [1.28829, 0.09638],
    "age_entry": [0.04866, 0.01033],
    "diabetes_duration_entry": [0.06538, 0.01130],
    "female": [0.30198, 0.13882],
    "ever_hypertension": [0.44272, 0.15023],
    "lag_tv_csme": [0.57131, 0.15752],
    "mean_hba1c": [0.30423, 0.05162],
    "mean_hr": [0.01673, 0.00886],
    "mean_trig": [0.41894, 0.15080],
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention, rng):
    """
    Calculate probability of DPN
    """

    if has_event(individual, 'dpn'):
        return 1

    explanators = 0
    explanators += MODIFIED_FACTORS['age_entry'][0] * individual['age_entry']
    explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * individual['diabetes_duration_entry']
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS['mean_hba1c'][0] * mean_risk_factor(individual, 'hba1c')
    explanators += MODIFIED_FACTORS['mean_hr'][0] * mean_risk_factor(individual, 'hr')
    explanators += MODIFIED_FACTORS['mean_trig'][0] * mean_risk_factor(individual, 'trig')

    if has_event(individual, 'hypertension'):
        explanators += MODIFIED_FACTORS['ever_hypertension'][0]

    if has_history(individual, 'csme', step):
        explanators += MODIFIED_FACTORS['lag_tv_csme'][0]

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
    complication_multiplier = custom_values['complication_multipliers']['dpn multiplier']
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