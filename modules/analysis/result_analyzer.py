import pandas as pd

from modules.analysis.result_loader import ResultLoader
from modules.analysis.analyzers.allocability_analyzer import AllocabilityAnalyzer


class ResultAnalyzer:
    def __init__(self, current_path):
        self.current_path = current_path
        self.loader = ResultLoader(current_path=current_path)
        self.taskset_sets, self.assignment_sets, self.scheduling_sets = self.loader.load_results()

        self.df_tasksets = pd.DataFrame([vars(t) for t in self.taskset_sets])
        self.df_assignments = pd.DataFrame(
            [vars(a) for a in self.assignment_sets]
        )
        self.df_schedulings = pd.DataFrame(
            [vars(s) for s in self.scheduling_sets]
        )

        self.df = self.df_tasksets.merge(
            self.df_assignments, on=["taskset_id"], suffixes=("_taskset", "_assignment")
        ).merge(self.df_schedulings, on=["taskset_id", "assignment_id"], suffixes=("_assignment", "_scheduling"))

    def run_analysis(self):
        self.analyze_allocability()
        # self.analyze_schedulability()
        # self.analyze_overutilization()
        # self.analyze_citta_acceptance_ratio()
        # self.analyze_citta_prediction_accuracy()
        # self.analyze_wmin_citta_similarity()

    def analyze_allocability(self):
        analyzer = AllocabilityAnalyzer(self.df)
        analyzer.analyze()

    # def analyze_schedulability(self):
    #     analyzer = SchedulabilityAnalyzer(self.df)
    #     analyzer.analyze()

    # def analyze_overutilization(self):
    #     analyzer = OverutilizationAnalyzer(self.df)
    #     analyzer.analyze()

    # def analyze_citta_acceptance_ratio(self):
    #     analyzer = CittaAnalyzer(self.df)
    #     analyzer.analyze_acceptance_ratio()

    # def analyze_citta_prediction_accuracy(self):
    #     analyzer = CittaAnalyzer(self.df)
    #     analyzer.analyze_prediction_accuracy()

    # def analyze_wmin_citta_similarity(self):
    #     analyzer = WminCittaSimilarityAnalyzer(self.df)
    #     analyzer.analyze()
