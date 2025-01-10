from src.simulation.utils import *

EVENT = "ldl"

IS_DETERMINISTIC = True

FACTORS = {
    "lambda_val": 13.75,
    "prev": 0.78,
    "initial": 0.0993,
    "age_entry": 0.0423,
    "diabetes_duration_entry": -0.0498,
    "step": 0.0257,
    "female": -0.788,
    "ever_lipid_treatment": -8.572
}


def calculate_default(individual, step):
    explanators = 0
    explanators += FACTORS['age_entry'] * individual['age_entry']
    explanators += FACTORS['diabetes_duration_entry'] * individual['diabetes_duration_entry']
    explanators += FACTORS['female'] * individual['female']
    explanators += FACTORS["step"] * step
    explanators += FACTORS["prev"] * get_event_in_step(individual, 'ldl', step - 1)
    explanators += FACTORS["initial"] * get_event_in_step(individual, 'ldl', 0)

    if has_event(individual, 'lipid_treatment'):
        explanators += FACTORS['ever_lipid_treatment']

    return explanators + FACTORS['lambda_val']


def calculate(individual, step, _, intervention, has_intervention, rng):
    progression = calculate_default(individual, step)
    # check if advanced intervention applies
    is_non_compliant = individual['cholesterol_non_compliant']
    if intervention and intervention['cholesterol_control_setup_type'] == 'advanced':
        ldl_reductions = intervention['cholesterol_control_advanced'][0]
        statin_reductions = intervention['cholesterol_control_statin'][0]
        # determine whether this is a non-intervention or intervention run
        age_type = 'Standard'
        if has_intervention and not is_non_compliant:
            age_type = 'Intervention'
        min_age = ldl_reductions[f'Treatment begins at age {age_type}']

        # a user specified trajectory is applied to both, non-intervention and intervention runs
        # min age for treatment depends on the type of run
        trajectory_info = intervention['cholesterol_control_trajectory'][0]
        if trajectory_info['modify_trajectory'] == 'modify_trajectory' and individual['age'] < min_age:
            ldl_change = trajectory_info['annual_ldl_change']
            progression = get_event_in_step(individual, 'ldl', step - 1) + ldl_change

        # only apply if individual is at least as old as user specified minimum age
        # per instruction, intervention and non-intervention values are the same
        if individual['age'] >= min_age:
            run_type = 'std'
            if has_intervention:
                run_type = 'int'
            cvd_type = 0
            if has_event(individual, 'cvd'):
                cvd_type = 1
            if ldl_reductions[f'moderate_statin_cvd{cvd_type}_{run_type}'] == 0:
                ldl_reduction = statin_reductions['moderate_statin_reduction']
                statin_type = 1
            elif ldl_reductions[f'high_statin_cvd{cvd_type}_{run_type}'] == 1:
                ldl_reduction = statin_reductions['high_statin_reduction']
                statin_type = 2
            else:
                ldl_reduction = 0
                statin_type = 0

            progression = progression * (1 - ldl_reduction)
            individual['statin type'].append(statin_type)
        else:
            individual['statin type'].append(0)

    return rounder(progression, ndigits=2)


def modify_coefficients(data, rng):
    pass