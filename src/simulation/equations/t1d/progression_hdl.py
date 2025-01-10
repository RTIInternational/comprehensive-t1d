from src.simulation.utils import *

EVENT = "hdl"

IS_DETERMINISTIC = True

FACTORS = {
    "intercept": 1.822,
    "prev": 0.855,
    "initial": 0.0879,
    "age_entry": 0.0218,
    "diabetes_duration_entry": -0.0188,
    "step": 0.0751,
    "female": 0.993,
    "ever_lipid_treatment": -0.385
}


def calculate_default(individual, step):
    explanators = 0
    explanators += FACTORS['age_entry'] * individual['age_entry']
    explanators += FACTORS['diabetes_duration_entry'] * individual['diabetes_duration_entry']
    explanators += FACTORS['female'] * individual['female']
    explanators += FACTORS["step"] * step
    explanators += FACTORS["prev"] * get_event_in_step(individual, 'hdl', step - 1)
    explanators += FACTORS["initial"] * get_event_in_step(individual, 'hdl', 0)

    if has_event(individual, 'lipid_treatment'):
        explanators += FACTORS['ever_lipid_treatment']

    return explanators + FACTORS['intercept']


def calculate(individual, step, _, intervention, has_intervention, rng):
    if intervention and intervention['cholesterol_control_setup_type'] == 'advanced':
        hdl_reductions = intervention['cholesterol_control_advanced'][0]
        is_non_compliant = individual['cholesterol_non_compliant']
        age_type = 'Standard'
        if has_intervention and not is_non_compliant:
            age_type = 'Intervention'
        min_age = hdl_reductions[f'Treatment begins at age {age_type}']
        # a user specified trajectory is applied to both, non-intervention and intervention runs
        # min age for treatment depends on the type of run
        trajectory_info = intervention['cholesterol_control_trajectory'][0]
        if trajectory_info['modify_trajectory'] == 'modify_trajectory' and individual['age'] < min_age:
            hdl_change = trajectory_info['annual_hdl_change']
            progression = get_event_in_step(individual, 'hdl', step - 1) + hdl_change
        else:
            progression = calculate_default(individual, step)
    else:
        progression = calculate_default(individual, step)

    return rounder(progression, ndigits=2)


def modify_coefficients(data, rng):
    pass