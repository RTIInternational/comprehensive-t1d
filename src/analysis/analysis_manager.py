from .simulation_analyzer_polars import SimulationAnalyzerPolars


class AnalysisManager():
    """
    AnalysisManager is a Factory class used to invoke the appropriate analysis type
    """

    def __init__(self, scenario, uuid):
        self.uuid = uuid
        self.scenario = scenario

        self._set_analysis()

    def _set_analysis(self):

        analyzer = SimulationAnalyzerPolars

        self.analysis = analyzer(self.scenario, self.uuid)

    def manage(self):
        self.analysis.run()
