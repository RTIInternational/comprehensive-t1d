import json
import os
from random import uniform

import numpy as np


def generate_random_distribution(
    n_agents: int, n_steps: int, behaviors: dict, initial_seed: int | float
):
    """
    Generate a random uniform distribution of numbers for each behavior.

    Parameters
    ----------
    n_agents : int
        Number of agents in the simulation
    n_steps : int
        Number of steps in the simulation
    behaviors : dict
        Dictionary of behavior names
    initial_seed : int | float
        Initial seed for the random number generator

    Returns
    -------
    dict
        Dictionary of random numbers for each behavior
    """
    random_numbers = {}
    for index, (behavior_name, behavior) in enumerate(behaviors.items(), start=1):
        try:
            if behavior.needs_probability:
                rng = np.random.default_rng(seed=initial_seed + index)
                random_numbers[behavior_name] = rng.uniform(size=(n_agents, n_steps))
        except Exception:
            # Not logging the exception since it could pollute the logs, especially
            # when the function is getting called for every agent a la `run_sim_on_agent`
            continue

    return random_numbers


def rounder(number, ndigits=4):
    """
    Round a float to a specified length. This abstraction ensures values are in
    the correct data type

    :param number: number to round
    :param ndigits: number of digits to round to (default 4)
    :return: float rounded to ndigits
    """
    try:
        return round(float(number), ndigits)
    except (ValueError, TypeError):
        # Convert strings or None to 0
        return 0


def generate_random_probability():
    """
    Generate a random probability comparison

    :returns: "random" probability
    """
    return rounder(uniform(0, 1))


def get_value(key, dictionary, fallback):
    """
    Get the the value of a key from a dictionary. If the key is not available,
    fallback to a default dictionary. This assumes key is valid.

    :param key: factor key
    :param dictionary: dictionary to check
    :param fallback: fallback dictionary
    :return: value associated with key
    """
    if key in dictionary:
        return dictionary[key]

    return fallback[key]


def get_discount(rate, time):
    return rounder(1 / ((1 + rate) ** time), 2)


def has_event(individual, flag):
    """
    Determine whether or not an individual has ever had an event - including the current step

    :param individual: member of the population
    :param flag: key to evaluate
    :return: has there been an event?
    """
    return any(individual[flag])


def has_event_in_step(individual, flag, step):
    """
    Determine whether or not an individual has had an event in a given step - including the current step

    :param individual: member of the population
    :param flag: key to evaluate
    :param step: timestep
    :return: has there been an event?
    """
    return bool(get_event_in_step(individual, flag, step, default=False))


def has_acute_event(individual, flag, step):
    """
    Determine whether or not an individual has an event in the step immediately prior

    :param individual: member of the population
    :param flag: key to evaluate
    :param step: timestep
    :return: has there been an event?
    """
    return has_event_in_step(individual, flag, step - 1)


def has_acute_event_in_simulation(individual, flag, step):
    """
    Determine whether an individual has an event in the step immediately prior

    :param individual: member of the population
    :param flag: key to evaluate
    :param step: timestep
    :return: has there been an event?
    """
    if step > 1:
        return has_event_in_step(individual, flag, step - 1)
    return 0


def has_history(individual, flag, step):
    """
    Determine whether an individual has had an event prior to the current
    step

    :param individual: member of the population
    :param flag: key to evaluate
    :param step: timestep
    :return: is any flag truthy?
    """
    return any(individual[flag][:step])


def has_history_in_simulation(individual, flag, step):
    """
    Determine whether an individual has had an event during the simulation but prior to the current step.

    Certain T2D equations look for diagnosis of a complication during the
    simulation only, ignoring any events at baseline.

    :param individual: member of the population
    :param flag: key to evaluate
    :return: has there been an event?
    """
    return any(individual[flag][1:step])


def has_event_in_simulation(individual, flag):
    """
    Determine whetheran individual has had an event during the simulation.

    Certain T2D equations look for diagnosis of a complication during the
    simulation only, ignoring any events at baseline.

    :param individual: member of the population
    :param flag: key to evaluate
    :return: has there been an event?
    """
    return any(individual[flag][1:])


def get_event(individual, flag):
    """
    Get the individuals history for an event

    :param individual: member of the population
    :param flag: key to evaluate
    :return: event list
    """
    return individual[flag]


def get_event_in_step(individual, flag, step, default=None):
    """
    Get the value of an event in a given step

    :param individual: member of the population
    :param flag: key to evaluate
    :param step: timestep
    :return: event in a given step
    """
    try:
        return individual[flag][step]
    except IndexError:
        # if we catch an index error, this means we haven't processed that field
        return default


def calculate_time_weighted_risk_factor(events):
    """
    Given an individual's event history, calculate the time weighted risk factor

    :param events: event list
    :return: time weighted factor
    """
    numerator = sum([x * (i + 1) for i, x in enumerate(events)])
    denominator = sum([i + 1 for i in range(len(events))])

    try:
        return numerator / denominator
    except ZeroDivisionError:
        return 0


def time_weighted_risk_factor(individual, flag):
    """
    Get the time weighted risk factor for an attribute.

    :param individual: member of the population
    :param flag: key to evaluate
    :return: time weighted factor
    """
    events = get_event(individual, flag)
    return calculate_time_weighted_risk_factor(events)


def mean_risk_factor(individual, flag):
    """
    Get the mean risk factor for an attribute.

    :param individual: member of the population
    :param flag: key to evaluate
    :return: time weighted factor
    """
    events = get_event(individual, flag)
    numerator = sum(list(events))
    denominator = len(events)

    try:
        return numerator / denominator
    except ZeroDivisionError:
        return 0


def get_time_of_event(individual, flag):
    """
    Get the timestep of the first occurrence of an event

    :param individual: member of the population
    :param flag: key to evaluate
    :return: timestep of first occurrence
    """
    try:
        event_history = get_event(individual, flag)
        return event_history.index(1)
    except ValueError:
        return -1


def delete_last_entry(individual, event):
    event_history = individual[event]
    del event_history[-1]
    return event_history


def make_directory(directory_path):
    """
    Create an output directory as applicable.
    """

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def get_screening_coefficients():
    """
    Get the coefficients for for screening behaviors when the "diabetes type" is "screen"

    Returns
    -------
    dict
        The coefficients for screening behaviors.
    """
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

    with open(os.path.join(root_dir, "scenarios", "screening.json"), "r") as json_file:
        coefficients = json.load(json_file)

    who_gets_screened = coefficients["who_gets_screened"]
    screening_characteristics = coefficients["screening_characteristics"]
    modified_coefficients = {
        "screening_frequency": who_gets_screened["screening_frequency"],
        "min_age": who_gets_screened["age"]["min_age"],
        "max_age": who_gets_screened["age"]["max_age"],
        "min_bmi": who_gets_screened["min_bmi"],
        "screening_sequence": [],
        "confirmatory_test": screening_characteristics["confirmation_test"],
        "specificity_diabetes": screening_characteristics["diabetes_specificity"] / 100,
        "specificity_prediabetes": screening_characteristics["prediabetes_specificity"]
        / 100,
        "sensitivity_diabetes": screening_characteristics["diabetes_sensitivity"] / 100,
        "sensitivity_prediabetes": screening_characteristics["prediabetes_sensitivity"]
        / 100,
        "cost_screening": screening_characteristics["cost_screening"],
        "cost_confirmatory": screening_characteristics["cost_confirmatory"],
        "probability_of_nonscreening_diagnosis": coefficients[
            "probability_of_nonscreening_diagnosis"
        ],
    }

    if (screening_frequency := modified_coefficients["screening_frequency"]) != 0:
        modified_coefficients["screening_sequence"] = list(
            range(1, 100, screening_frequency)
        )
    else:
        modified_coefficients["screening_sequence"] = [1]

    return modified_coefficients
