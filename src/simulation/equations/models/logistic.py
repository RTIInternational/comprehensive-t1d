import numpy as np
from numba import jit

@jit(nopython=True)
def model(explanators, intercept):
    """
    Calculate a logistic integrated hazard

    :param explanators: sum of explanatory variables
    :param lambda_val: lambda factor
    :returns: logistic regression intergrated hazard value
    """
    z = (intercept + explanators)
    return 1 / (1 + np.exp(-z))
