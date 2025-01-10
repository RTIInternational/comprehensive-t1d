EVENT = "age"

IS_DETERMINISTIC = True

BEHAVIOR = 'SET'


def calculate(individual, *_):
    """
    Increment an individual's age
    """
    return individual['age'] + 1


def modify_coefficients(data, rng):
    pass