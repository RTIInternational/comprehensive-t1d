from src.simulation.utils import *

EVENT = "hba1c"

IS_DETERMINISTIC = True

FACTORS = {
    "intercept": 1.638,
    "prev": 0.818,
    "initial": 0.0196,
    "age_entry": -0.00126,
    "diabetes_duration_entry": -0.00604,
    "step": -0.000449,
    "female": -0.000174,
    "dcct_int_y1": -1.994,
    "dcct_int_ay1": -0.173,
    "y1994_dcct_conv_edc": -0.316,
    "ay1994_dcct_conv_edc": -0.164,
    "dcct_edic": -0.109
}


def target_mapping(type):
    mapping = {
        'individual["age"] < 18': f'If age < 18 {type}',
        'individual["age"] >= 65': f'If age >= 65 {type}',
        'has_event(individual, "cvd") or has_event(individual, "esrd")': f'If CVD = 1 or ESRD = 1 {type}',
        'individual["age"] >= 65 and (has_event(individual, "cvd") or has_event(individual, "esrd"))':
            f'If age >= 65 and (CVD = 1 or ESRD = 1) {type}'
    }
    return mapping


def calculate_default(individual, step):
    dcct_edic = get_dcct_edic_coeff(individual)
    dcct_int_y1, dcct_int_ay1 = get_dcct_yearly_int_coeffs(individual, step)
    y1994_dcct_conv_edc, ay1994_dcct_conv_edc = get_1994_yearly_coeffs()

    explanators = 0
    explanators += FACTORS['age_entry'] * individual['age_entry']
    explanators += FACTORS['diabetes_duration_entry'] * individual['diabetes_duration_entry']
    explanators += FACTORS['female'] * individual['female']
    explanators += FACTORS["step"] * step
    explanators += FACTORS["prev"] * get_event_in_step(individual, 'hba1c', step - 1)
    explanators += FACTORS["initial"] * get_event_in_step(individual, 'hba1c', 0)
    explanators += FACTORS["dcct_edic"] * dcct_edic
    explanators += FACTORS["dcct_int_y1"] * dcct_int_y1
    explanators += FACTORS["dcct_int_ay1"] * dcct_int_ay1
    explanators += FACTORS["y1994_dcct_conv_edc"] * y1994_dcct_conv_edc
    explanators += FACTORS["ay1994_dcct_conv_edc"] * ay1994_dcct_conv_edc

    progression = explanators + FACTORS['intercept']
    return progression


def calculate(individual, step, _, intervention, has_intervention, rng):
    """
    implements the advanced glycemic control intervention

    1) two ways of calculating t+1 hba1c values: 1) risk factor progression equation (default) or 2) user specified
    trajectory
    1a) the basic intervention only changes baseline values for risk factors and complications

    2) for the advanced intervention the user can also change values and targets for non-intervention runs (referred
    to in schema as 'Standard')
    2a) targets define age or condition dependent thresholds that trigger the application of a drug
    2b) if several targets apply, the one with the max value is selected

    3) values and targets may be different for non-intervention and intervention runs

    4) determine all targets that apply to an individual; if no conditional targets apply, use general one

    5) determine if an individual has received at least one drug
    5a) if no drugs have been administered yet, add hba1c increase to baseline value
    5b) if at least 1 drug has been administered, add to previous value

    6) every time a target is exceeded, apply a drug (reduction in hba1c); a maximum of 3 drugs can be applied with the
    third drug being re-applied for any exceed target beyond the third one
    """

    # user has chosen advanced intervention setup
    is_non_compliant = individual['glycemic_non_compliant']
    if intervention and intervention['glycemic_control_setup_type'] == 'advanced':
        modify_trajectory = intervention['glycemic_control_trajectory_advanced'][0]
        intensification = intervention['glycemic_control_intensification_advanced'][0]

        # all available target conditionals; these will be used in an eval expression below
        targets = [
            'individual["age"] < 18', 'individual["age"] >= 65',
            'has_event(individual, "cvd") or has_event(individual, "esrd")',
            'individual["age"] >= 65 and (has_event(individual, "cvd") or has_event(individual, "esrd"))'
        ]

        # targets with values specified by the user in the UI
        all_targets_dict = intervention["glycemic_control_targets_advanced"][0]

        # determine whether this is a non-intervention (Standard) or intervention run
        type = 'Standard'
        if has_intervention and not is_non_compliant:
            type = 'Intervention'

        # get the number of drugs this individual has been on (default = 0)
        individual_drug = get_event_in_step(individual, 'glycemic drug', step - 1)
        # advanced intervention has a default value; this is the only way to distinguish the cost of the basic
        # intervention from the advanced one
        if individual_drug == 0:
            individual_drug = 1

        # determine all targets that apply to this individual; if no conditional targets apply, use general one
        mapping = target_mapping(f'{type}')
        individual_target_dict = {}
        for target in targets:
            if eval(target):
                individual_target_dict[mapping[target]] = all_targets_dict[mapping[target]]
        if not individual_target_dict:
            target = all_targets_dict[f'General {type}']
        # determine max value and set that as the target value to use
        else:
            max_value = [max(individual_target_dict.values())][0]
            max_targets = [
                v for k, v in individual_target_dict.items() if v == max_value]
            target = max_targets[0]

        if not bool(modify_trajectory['custom_a1c_trajectory']):
            progression = calculate_default(individual, step)
        # trajectory has been customized by user
        else:
            # if no drugs have been administered yet, apply hba1c increase to baseline value
            if individual_drug == 1:
                effective_step = 0
                # get the actual change value; applies only if no drugs have been administered
                change = modify_trajectory[f'Annual A1c Before {type}']
            # apply to value from previous time step
            else:
                effective_step = step - 1
                # get the actual change value; applies only if at least 1 drugs has been administered
                change = modify_trajectory[f'Annual A1c After {type}']
            # and calculate new hba1c value
            progression = get_event_in_step(individual, 'hba1c', effective_step) + change

        # drug labels are strings in the UI but is easier to just store the current drug as an additive number in an
        # individual
        drug_mapping = {2: 'Effect of intensifying on A1c ', 3: 'Effect of next intensification on A1c ',
                        4: 'Effect of subsequent intensification on A1c '}

        # if the new hba1c value exceeds the determined target + an additional small amount, apply apply a drug
        if progression > target + all_targets_dict[f'Intensify if A1c > target {type}']:
            individual_drug += 1
            # only 3 drugs can be applied
            if individual_drug > 4:
                individual_drug = 4
            # get the reducing effect of the applicable drug
            drug_effect = intensification[drug_mapping[individual_drug] + type]
            # apply the effect of the drug
            # drug_effect is negative (improvement)
            progression = progression + drug_effect
            # update individual with an additional drug
        individual['glycemic drug'].append(individual_drug)
    # user has opted not to define an advanced intervention
    else:
        progression = calculate_default(individual, step)
        individual['glycemic drug'].append(get_event_in_step(individual, 'glycemic drug', step - 1))
    return rounder(progression, ndigits=2)


def modify_coefficients(data, rng):
    pass