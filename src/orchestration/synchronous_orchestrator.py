import os
from src.population.population_generator import PopulationBuilder
from src.simulation.model import ComprehensiveModel
from src.analysis.analysis_manager import AnalysisManager
from .base_orchestrator import BaseOrchestrator, write_semaphore
from . import (BROADCAST_MESSAGES, BROADCAST_STATUSES)
import time

analysis_start = 0
simulation_end = 0
analysis_end = 0

def _run_population(scenario_tuple, uuid):
    population = PopulationBuilder(scenario_tuple, uuid)
    population.build_population()


def _run_simulation(scenario, uuid):
    simulator = ComprehensiveModel(scenario, uuid)
    simulator.run_model()


def _run_analysis(scenario, uuid):
    analysis = AnalysisManager(scenario, uuid)
    analysis.manage()


class SynchronousOchestrator(BaseOrchestrator):
    """
    Orchestrator manages the execution of a simulation pipeline from population
    generation to analysis.
    """
    def __init__(self, uuid, stages=[]):
        super().__init__(uuid)

        self.stages = stages

    def run(self):
        """
        Run the pipeline.
        """
        if not self.configured:
            return

        simulation_end = 0
        analysis_end = 0
        start = time.time()

        self.generate_output_directories()

        # Generate baseline and intervention populations
        if 'population' in self.stages:
            # non-intervention and intervention runs need to share values of most columns (except those
            # affected by basic interventions); each dict entry is a non-intervention/intervention tuple
            for run_id, scenario_tuple in self.simulations.items():
                self.broadcast('{} - {}'.format(BROADCAST_MESSAGES['generation'],
                                                run_id))
                _run_population(scenario_tuple, self.uuid)

        # If we are running the simulation stage, simulate.
        if 'simulation' in self.stages:

            for scenario_tuple in self.simulations.values():
                for scenario in scenario_tuple:
                    population_path = self.get_population_path(scenario['scenario_name'])
                    if not os.path.exists(population_path):
                        self.broadcast("You must create a population before conducting simulations.")
                        return

                    self.broadcast('{} - {}'.format(BROADCAST_MESSAGES['simulation'],
                                                    scenario['scenario_name']))
                    _run_simulation(scenario, self.uuid)

            simulation_end = time.time() - start

        if 'analysis' in self.stages:
            analysis_start = time.time()
            self.broadcast(BROADCAST_MESSAGES['analysis'])

            _run_analysis(self.scenario, self.uuid)

        self.broadcast(BROADCAST_MESSAGES['done'])

        end = time.time()

