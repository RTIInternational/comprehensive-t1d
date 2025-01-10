from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "gfr"

FACTORS = {
    "intercept": [-16.67315, 1.63241],
    "shape": [1.24943, 0.12440],
    "age_entry_log": [0.53833, 0.32156],
    "diabetes_duration_entry": [0.03065, 0.01453],
    "female": [0.40363, 0.16205],
    "curr_sbp": [0.01812, 0.00475],
    "curr_trig": [0.67316, 0.13884],
    "lag_tv_csme": [0.40613, 0.17961],
    "lag_tv_cvd": [1.14530, 0.36498],
    "lag_tv_ma": [1.57913, 0.20124],
    "lag_tv_mi": [1.07045, 0.24915],
    "mean_bmi": [-0.05103, 0.02484],
    "mean_hba1c": [0.44351, 0.06386],
    "mean_insulin_dose": [-1.03124, 0.43632],
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, intervention, is_intervention, rng):
    """
    Calculate probability of GFR
    """

    # per instructions from PI email Dec 26, 2023: Because
    # people with dialysis have ESRD, which is defined by eGFR<15, they must have gfr.
    # Therefore, if people develop ESRD, we should also say that they now have gfr.
    if has_event(individual, 'gfr') or has_event_in_step(individual, 'esrd', step):
        return 1

    explanators = 0
    explanators += MODIFIED_FACTORS['age_entry_log'][0] * math.log(individual['age_entry'])
    explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * individual['diabetes_duration_entry']
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS['curr_sbp'][0] * get_event_in_step(individual, 'sbp', step)
    explanators += MODIFIED_FACTORS['curr_trig'][0] * get_event_in_step(individual, 'trig', step)
    explanators += MODIFIED_FACTORS['mean_bmi'][0] * mean_risk_factor(individual, 'bmi')
    explanators += MODIFIED_FACTORS['mean_hba1c'][0] * time_weighted_risk_factor(individual, 'hba1c')
    explanators += MODIFIED_FACTORS['mean_insulin_dose'][0] * mean_risk_factor(individual, 'insulin_dose')

    if has_history(individual, 'csme', step):
        explanators += MODIFIED_FACTORS['lag_tv_csme'][0]

    if has_acute_event(individual, 'cvd', step):
        explanators += MODIFIED_FACTORS['lag_tv_cvd'][0]

    if has_history(individual, 'macroalbuminuria', step):
        explanators += MODIFIED_FACTORS['lag_tv_ma'][0]

    if has_history(individual, 'microalbuminuria', step):
        explanators += MODIFIED_FACTORS['lag_tv_mi'][0]

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
    complication_multiplier = custom_values['complication_multipliers']['gfr multiplier']
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