from src.simulation.utils import *

EVENT = "sbp_post"

IS_DETERMINISTIC = True

FACTORS = {
    "intercept": 33.20981,
    "prev": 0.6478691,
    "initial": 0.0688441,
    "age_entry": 0.0807516,
    "diabetes_duration_entry": -0.0046047,
    "step": 0.0855703,
    "female": -0.6678222
}


def target_mapping(type):
    mapping = {
        'individual["age"] >= 65': f'If age >= 65 {type}',
        'has_event(individual, "cvd")': f'If CVD = 1 {type}',
        'individual["age"] >= 65 and has_event(individual, "cvd")':
            f'If age >= 65 and CVD = 1 {type}'
    }
    return mapping


def calculate_default(individual, step):
    # Macro calculations are based on the year of micro diagnosis as opposed to
    # simulation start. We use the year of micr diagnosis to update age at entry,
    # diabetes duration at entry and timestep.
    bp_tx_applied_step = get_time_of_event(individual, 'bp_treatment')
    tx_step = step - bp_tx_applied_step

    explanators = 0
    explanators += FACTORS['age_entry'] * individual['age_entry']
    explanators += FACTORS['diabetes_duration_entry'] * \
        individual['diabetes_duration_entry']
    explanators += FACTORS['female'] * individual['female']
    explanators += FACTORS["step"] * tx_step
    explanators += FACTORS["prev"] * \
        get_event_in_step(individual, 'sbp', step - 1)
    explanators += FACTORS["initial"] * get_event_in_step(individual, 'sbp', 0)

    return explanators + FACTORS['intercept']


def calculate(individual, step, _, intervention, has_intervention, rng):

    if not has_event(individual, 'bp_treatment'):
        individual['bp drug'].append(
            get_event_in_step(individual, 'bp drug', step - 1))
        return 0

    # user has chosen advanced intervention setup
    is_non_compliant = individual['bp_non_compliant']
    if intervention and intervention['bp_control_setup_type'] == 'advanced':
        modify_trajectory = intervention['bp_control_trajectory_advanced'][0]
        intensification = intervention['bp_control_intensification_advanced'][0]

        # all available target conditionals; these will be used in an eval expression below
        targets = [
            'individual["age"] >= 65',
            'has_event(individual, "cvd")',
            'individual["age"] >= 65 and has_event(individual, "cvd")'
        ]

        # targets with values specified by the user in the UI
        all_targets_dict = intervention["bp_control_targets_advanced"][0]

        # determine whether this is a non-intervention or intervention run
        run_type = 'Standard'
        if has_intervention and not is_non_compliant:
            run_type = 'Intervention'

        # get the number of drugs this individual has been on (default = 0)
        individual_drug = get_event_in_step(individual, 'bp drug', step - 1)
        # advanced intervention has a default value; this is the only way to distinguish the cost of the basic
        # intervention from the advanced on2
        if individual_drug == 0:
            individual_drug = 1

        # determine all targets that apply to this individual; if no conditional targets apply, use general one
        mapping = target_mapping(f'{run_type}')
        individual_target_dict = {}
        for target in targets:
            if eval(target):
                individual_target_dict[mapping[target]
                                       ] = all_targets_dict[mapping[target]]
        if not individual_target_dict:
            target = all_targets_dict[f'General {run_type}']
        # determine max value and set that as the target value to use
        else:
            max_value = [max(individual_target_dict.values())][0]
            max_targets = [
                v for k, v in individual_target_dict.items() if v == max_value]
            target = max_targets[0]

        if not bool(modify_trajectory['custom_sbp_trajectory']):
            progression = calculate_default(individual, step)
        # trajectory has been modified by user
        else:
            # if no drugs have been administered yet, apply hba1c increase to baseline value
            if individual_drug == 1:
                effective_step = 0
                change = modify_trajectory[f'Annual SBP change Before {run_type}']
                # 1 is added to indicate default cost of advanced intervention
                individual['bp drug'].append(1)
            # apply to value from previous time step
            else:
                effective_step = step - 1
                # get the actual change value; dependent on type of run (non-intervention, intervention)
                change = modify_trajectory[f'Annual SBP change After {run_type}']
            # and calculate new hba1c value
            progression = get_event_in_step(
                individual, 'sbp', effective_step) + change

        # drug labels are strings in the UI but is easier to just store the current drug as an additive number in an
        # individual
        drug_mapping = {1: 'Effect of first drug on blood pressure ', 2: 'Effect of second drug on blood pressure ',
                        3: 'Effect of subsequent drug on blood pressure '}

        # if the new hba1c value exceeds the determined target apply a a drug
        if progression > target + all_targets_dict[f'Intensify if SBP > target {run_type}']:
            individual_drug += 1
            # only 3 drugs can be applied
            if individual_drug > 3:
                individual_drug = 3
            # get the reducing effect of the applicable drug
            drug_effect = intensification[drug_mapping[individual_drug] + run_type]
            # apply the effect of the drug ... negative entered value = improvement
            progression = progression + drug_effect
            # update individual with an additional drug
        individual['bp drug'].append(individual_drug)
    else:
        progression = calculate_default(individual, step)
        individual['bp drug'].append(get_event_in_step(individual, 'bp drug', step - 1))

    return rounder(progression, ndigits=2)


def modify_coefficients(data, rng):
    pass