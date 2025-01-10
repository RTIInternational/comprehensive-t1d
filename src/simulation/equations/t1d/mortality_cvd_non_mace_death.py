from src.simulation.utils import *
from src.simulation.equations.models import *
from copy import deepcopy

EVENT = "non_mace_death"

FACTORS = {
    "intercept": [-6.369674, 1.959899],
    "rho_val": [0.0702433, 0.030014],
    "age_entry": [-0.0452561, 0.0197149],
    "diabetes_duration_entry": [-0.0027643, 0.0203021],
    "female": [0.4253355, 0.3183535],
    "race": [-1.628687, 0.6340932],
    "lag_tv_mace": [0.5332735, 0.2866912],
    "curr_dbp": [0.0329504, 0.0136836],
    "curr_trig": [0.5131766, 0.2217169],
    "lag_tv_esrd": [0.5677936, 0.4014573],
    "lag_tv_hyp": [0.8304742, 0.3103535]
}
MODIFIED_FACTORS = deepcopy(FACTORS)


def calculate(individual, step, custom_values, *_):
    """
    Calculate probability of death
    """

    if not (has_event(individual, 'cvd_non_mace') or
            has_history(individual, 'cvd_mace', step)):
        return 0

    # Non-mace death equation sets the model's time step to zero in the first year
    # of a non-mace event OR the first year following a mace event. To determine
    # this time step, we first get the years of occurrence for mace and non-mace
    # events.
    non_mace_diagnosis_step = get_time_of_event(individual, 'cvd_non_mace')
    mace_diagnosis_step = get_time_of_event(individual, 'cvd_mace')

    # get_time_of_event returns -1 if the event hasn't occurred. If we encounter
    # a -1, reset that number to an arbitrarily high figure. We do this because
    # we're looking for the earliest occurrence of either mace or non-mace. -1
    # would always win as lowest occurrence.
    if non_mace_diagnosis_step == -1:
        non_mace_diagnosis_step = 999

    # The equation only considers MACE events in prior steps, so if the first
    # occurrence is in the current step, we ignore it.
    if mace_diagnosis_step == -1 or mace_diagnosis_step == step:
        mace_diagnosis_step = 999

    first_cvd_event_step = step - min(non_mace_diagnosis_step, mace_diagnosis_step + 1)

    explanators = 0
    explanators += MODIFIED_FACTORS['age_entry'][0] * (individual['age_entry'] + first_cvd_event_step)
    explanators += MODIFIED_FACTORS['diabetes_duration_entry'][0] * (individual['diabetes_duration_entry'] + first_cvd_event_step)
    explanators += MODIFIED_FACTORS['female'][0] * individual['female']
    explanators += MODIFIED_FACTORS['race'][0] * individual['race']
    explanators += MODIFIED_FACTORS['curr_dbp'][0] * get_event_in_step(individual, 'dbp', step)
    explanators += MODIFIED_FACTORS['curr_trig'][0] * get_event_in_step(individual, 'trig', step)

    if has_history(individual, 'cvd_mace', step):
        explanators += MODIFIED_FACTORS['lag_tv_mace'][0]

    if has_history(individual, 'esrd', step):
        explanators += MODIFIED_FACTORS['lag_tv_esrd'][0]

    if has_acute_event(individual, 'hypoglycemia', step):
        explanators += MODIFIED_FACTORS['lag_tv_hyp'][0]

    integrated_hazard_t = gompertz.model(explanators, first_cvd_event_step - 1,
                                         MODIFIED_FACTORS['intercept'][0], MODIFIED_FACTORS['rho_val'][0])
    integrated_hazard_t1 = gompertz.model(explanators, first_cvd_event_step,
                                          MODIFIED_FACTORS['intercept'][0], MODIFIED_FACTORS['rho_val'][0])

    mortality_multipliers = custom_values['mortality_multipliers']
    multiplier = mortality_multipliers['Equation 3']

    complication_prob = 1 - np.exp(multiplier * (integrated_hazard_t - integrated_hazard_t1))

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