from src.simulation.utils import *
from src.simulation.equations.models import normal
from copy import deepcopy

EVENT = "macroalbuminuria"

FACTORS = {
    "intercept": [-8.14952, 0.92823],
    "shape": [0.69037, 0.05769],
    "age_entry": [-0.00174, 0.00832],
    "diabetes_duration_entry": [-0.02012, 0.01340],
    "female": [-0.72802, 0.14798],
    "race": [-0.48018, 0.26301],
    "twd_hba1c": [0.30475, 0.05669],
    "twd_hba1c_pre10": [0.33340, 0.04899],
    "curr_hypertension": [0.80703, 0.15249],
    "lag_tv_cvd": [0.90789, 0.37317],
    "lag_tv_gfr": [1.17585, 0.37111],
    "lag_tv_npdr": [0.81896, 0.22067],
    "mean_totchol": [0.00223, 0.00219],
    "mean_hr": [0.02856, 0.00888]
}
MODIFIED_FACTORS = deepcopy(FACTORS)

def calculate(individual, step, custom_values, intervention, is_intervention, rng):
    """
    Calculate probability of macroalbuminuria
    """

    if has_event(individual, 'macroalbuminuria'):
        return 1

    # only execute if individual has microalbuminuria in a previous step
    if not has_history(individual, 'microalbuminuria', step):
        return 0

    # Macro calculations are based on the year of micro diagnosis as opposed to
    # simulation start. We use the year of micr diagnosis to update age at entry,
    # diabetes duration at entry and timestep.
    micro_diagnosis_step = get_time_of_event(individual, 'microalbuminuria')
    macro_step = step - micro_diagnosis_step

    explanators = 0
    explanators += MODIFIED_FACTORS['age_entry'][0] * (individual['age_entry'] + micro_diagnosis_step)
    explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * (individual['diabetes_duration_entry'] + micro_diagnosis_step)
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS['race'][0] * individual['race']
    explanators += MODIFIED_FACTORS['curr_hypertension'][0] * get_event_in_step(individual, 'hypertension', step)
    explanators += MODIFIED_FACTORS['mean_totchol'][0] * mean_risk_factor(individual, 'totchol')
    explanators += MODIFIED_FACTORS['mean_hr'][0] * mean_risk_factor(individual, 'hr')

    if macro_step < 10:
        explanators += MODIFIED_FACTORS['twd_hba1c_pre10'][0] * mean_risk_factor(individual, 'hba1c')
    else:
        explanators += MODIFIED_FACTORS['twd_hba1c'][0] * mean_risk_factor(individual, 'hba1c')

    if has_acute_event(individual, 'cvd', step):
        explanators += MODIFIED_FACTORS['lag_tv_cvd'][0]

    if has_history(individual, 'gfr', step):
        explanators += MODIFIED_FACTORS['lag_tv_gfr'][0]

    if has_history(individual, 'npdr', step):
        explanators += MODIFIED_FACTORS['lag_tv_npdr'][0]

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
    complication_multiplier = custom_values['complication_multipliers']['macroalbuminuria multiplier']
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