class EquationFactory:
    """
    EquationFactory provides a wrapper around execution of equations. This wrapper
    abstracts common equation patterns.
    """

    def __init__(self, rng, equation_set, module, uuid, economics, interventions, has_intervention):
        self.equation_set = equation_set
        self.module = module
        self.event = getattr(self.module, 'EVENT', None)
        self.is_terminal = getattr(self.module, 'IS_TERMINAL', False)
        self.is_deterministic = getattr(self.module, 'IS_DETERMINISTIC', False)
        self.do_nothing = getattr(self.module, 'DO_NOT_RETURN_ANYTHING', False)
        self.behavior = getattr(self.module, 'BEHAVIOR', 'APPEND')
        self.has_intervention = has_intervention
        self.interventions = interventions
        self.economics = economics
        self.uuid = uuid
        self.reduction_factor = None
        self.individual = {}
        self.step = 0
        self.rng = rng

    def _update_record(self, value):
        """
        Update a record using the appropriate update strategy.

        :param value: Value to update
        """

        if self.behavior == 'APPEND':
            self.individual[self.event].append(value)
        else:
            self.individual[self.event] = value

    def _execute_deterministic(self):
        """
        Execute a deterministic calculation. Such a calculation returns a scalar
        value to be applied directly to the individual.
        """
        # bariatric_surgery updates these in t=1 or when relapse occurs; don't update them again
        surgery_risk_factors = ['bmi', 'sbp', 'ldl', 'hdl', 'trig']
        if (self.has_intervention and self.equation_set in ['t2d', 'pre', 'screen']
                and self.individual['bariatric_surgery'] and self.step == 1 and
                self.event in surgery_risk_factors):
            pass
        # only for t2d, during the time step relapse occurs, bariatric surgery updates hba1c
        elif (self.has_intervention and self.equation_set == 't2d' and sum(self.individual['relapse']) == 1
                and self.event in ['hba1c']):
            pass
        elif (self.has_intervention and self.equation_set in ['t2d'] and
              (sum(self.individual['remission']) == 1 or self.individual['improvement'])
                and self.event in ['hba1c', 'fpg']) and self.step == 1:
            pass
        elif (self.has_intervention and self.equation_set in ['pre', 'screen'] and
              self.individual['improvement'] and self.event in ['hba1c', 'fpg']) and self.step == 1:
            pass
        elif (self.has_intervention and self.equation_set in ['pre', 'screen'] and self.event in ['diabetes'] and
              self.step == 1 and self.individual['improvement']):
            pass
        else:
            self._update_record(self.module.calculate(self.individual, self.step, self.economics, self.interventions,
                                                  self.has_intervention, self.rng))

    def _execute_probabilistic(self):
        """
        Execute a probabilistic calculation. Probabilistic calculations are compared
        against a randomly generated number and applied as needed.
        """

        # for pre and screen, diabetes is updated in surgery at t=1 in case of remission or improvement
        if (self.has_intervention and self.equation_set in ['pre', 'screen'] and self.event in ['diabetes'] and
              self.step == 1 and self.individual['improvement']):
            pass
        else:
            complication_prob = self.module.calculate(self.individual, self.step, self.economics, self.interventions,
                                                      self.has_intervention, self.rng)
            event_bool = 0
            cointoss_prob = self.rng.random()
            if complication_prob > 0 and complication_prob >= cointoss_prob:
                event_bool = 1

            self._update_record(event_bool)

            if event_bool and self.is_terminal:
                self._terminate()

    def _terminate(self):
        """
        If the individual has passed away as the result of a terminal calculation,
        stop calculations against this individual.
        """
        self.individual['should_update'] = 0
        self.individual['deceased'] = 1

    def invoke(self):
        """
        Invoke the calculation. Determine the right strategy (deterministic or
        probabilistic) for this equation and execute accordingly.

        :returns: Updated individual
        """
        # an individual gets updated directly in this case
        if self.do_nothing:
            self.module.calculate(self.individual, self.step, self.economics, self.interventions,
                                  self.has_intervention, self.rng)
        elif not self.is_deterministic:
            self._execute_probabilistic()
        else:
            self._execute_deterministic()

        return self.individual

    def set_individual(self, individual):
        """
        Set the equation's current individual.

        :param individual: individual data set
        """
        self.individual = individual

    def set_step(self, step):
        """
        Set the equation's current step.

        :param step: current timestep
        """
        self.step = step
