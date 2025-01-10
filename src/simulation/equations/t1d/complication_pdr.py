from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "pdr"

FACTORS = {
    "intercept": [-10.27782, 0.63599],
    "shape": [0.96797, 0.05850],
    "age_entry": [-0.02947, 0.00636],
    "diabetes_duration_entry": [-0.01418, 0.02229],
    "diabetes_duration_entry_pre10": [-0.01418, 0.00887],
    "female": [0.06273, 0.09583],
    "curr_dbp": [0.01288, 0.00530],
    "curr_hr": [0.00664, 0.00425],
    "twd_hba1c": [0.65527, 0.04167],
    "twd_hba1c_pre10": [0.65527, 0.03453],
    "ever_hypertension": [0.23093, 0.11152],
    "lag_tv_csme": [1.22808, 0.10695],
    "lag_tv_dpn": [0.59519, 0.21101],
    "lag_tv_gfr": [0.53819, 0.27129],
    "lag_tv_ma": [0.38960, 0.14288]
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention, rng):
    """
    Calculate probability of PDR
    """
    if has_event(individual, 'pdr'):
        return 1

    # only execute if individual has npdr in a previous step
    if not has_history(individual, 'npdr', step):
        return 0

    # PDR calculations are based on the year of NPDR diagnosis as opposed to
    # simulation start. We use the year of NPDR diagnosis to update age at entry,
    # diabetes duration at entry and timestep.
    npdr_diagnosis_step = get_time_of_event(individual, 'npdr')
    pdr_step = step - npdr_diagnosis_step

    explanators = 0
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS['age_entry'][0] * (individual['age_entry'] + npdr_diagnosis_step)
    explanators += MODIFIED_FACTORS['curr_dbp'][0] * get_event_in_step(individual, 'dbp', step)
    explanators += MODIFIED_FACTORS['curr_hr'][0] * get_event_in_step(individual, 'hr', step)

    if pdr_step < 10:
        explanators += MODIFIED_FACTORS['twd_hba1c_pre10'][0] * mean_risk_factor(individual, 'hba1c')
        explanators += MODIFIED_FACTORS['diabetes_duration_entry_pre10'][0] * (individual['diabetes_duration_entry'] +
                                                                   npdr_diagnosis_step)
    else:
        explanators += MODIFIED_FACTORS['twd_hba1c'][0] * mean_risk_factor(individual, 'hba1c')
        explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * (individual['diabetes_duration_entry'] +
                                                             npdr_diagnosis_step)

    if has_event(individual, 'hypertension'):
        explanators += MODIFIED_FACTORS['ever_hypertension'][0]

    if has_history(individual, 'csme', step):
        explanators += MODIFIED_FACTORS['lag_tv_csme'][0]

    if has_acute_event(individual, 'dpn', step):
        explanators += MODIFIED_FACTORS['lag_tv_dpn'][0]

    if has_history(individual, 'gfr', step):
        explanators += MODIFIED_FACTORS['lag_tv_gfr'][0]

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
    complication_multiplier = custom_values['complication_multipliers']['pdr multiplier']
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