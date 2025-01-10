from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "esrd"

FACTORS = {
    "intercept": [-7.47408, 1.93660],
    "shape": [1.22032, 0.13275],
    "age_entry": [-0.06399, 0.02146],
    "diabetes_duration_entry": [-0.01951, 0.02872],
    "female": [-0.53111, 0.27194],
    "curr_totchol": [0.00340, 0.00219],
    "ever_hypertension": [1.62143, 0.41159],
    "lag_tv_cvd": [1.97909, 0.37177],
    "has_micro": [1.93077, 1.17040],
    "has_macro": [2.56869, 1.11677],
    "twd_hr": [0.03657, 0.01571]
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention, rng):
    """
    Calculate probability of ESRD
    """

    if has_event(individual, 'esrd'):
        return 1

    # only execute if individual has gfr in a previous step
    if not has_history(individual, 'gfr', step):
        return 0

    # ESRD calculations are based on the year of GFR diagnosis as opposed to
    # simulation start. We use the year of GFR diagnosis to update age at entry,
    # diabetes duration at entry and timestep.
    gfr_diagnosis_step = get_time_of_event(individual, 'gfr')
    esrd_step = step - gfr_diagnosis_step

    explanators = 0
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS['age_entry'][0] * (individual['age_entry'] + gfr_diagnosis_step)
    explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * (individual['diabetes_duration_entry'] + gfr_diagnosis_step)
    explanators += MODIFIED_FACTORS['curr_totchol'][0] * get_event_in_step(individual, 'totchol', step)
    explanators += MODIFIED_FACTORS['twd_hr'][0] * time_weighted_risk_factor(individual, 'hr')

    if has_event(individual, 'hypertension'):
        explanators += MODIFIED_FACTORS['ever_hypertension'][0]

    if has_acute_event(individual, 'cvd', step):
        explanators += MODIFIED_FACTORS['lag_tv_cvd'][0]

    '''
    When a person has neither micro nor macro, they have both indicators set to zero
    When a person develops micro, they have MICMACIND1 = 1, MICMACIND2 = 0
    When a person develops macro (for which they must have first developed micro),
    MICMACIND2 is set to 1 and MICMACIND1 is set back to 0.
    '''
    if has_event(individual, 'macroalbuminuria'):
        explanators += MODIFIED_FACTORS["has_macro"][0]
    elif has_event(individual, 'microalbuminuria'):
        explanators += MODIFIED_FACTORS["has_micro"][0]

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
    complication_multiplier = custom_values['complication_multipliers']['esrd multiplier']
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