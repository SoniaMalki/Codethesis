import pandas as pd

from modules.analysis.result_loader import ResultLoader
from modules.analysis.analyzers.assignment_analyzer import AssignmentAnalyzer
from modules.analysis.analyzers.scheduling_analyzer import SchedulingAnalyzer
from modules.analysis.analyzers.scheduling_by_assignment_analyzer import SchedulingByAssignmentAnalyzer


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

        self.df["task_core_ratio"] = self.df["tasks_per_taskset"] / \
            self.df["number_of_cores"]  # Calcul du ratio tâches/cœurs

    def run_analysis(self):
        # self.analyze_assignment()
        # self.analyze_scheduling()
        self.analyze_scheduling_by_assignment()

    def analyze_assignment(self):
        analyzer = AssignmentAnalyzer(self.df, self.current_path)
        analyzer.analyze()

    def analyze_scheduling(self):
        analyzer = SchedulingAnalyzer(self.df, self.current_path)
        analyzer.analyze()

    def analyze_scheduling_by_assignment(self):
        analyzer = SchedulingByAssignmentAnalyzer(self.df, self.current_path)
        analyzer.analyze()
