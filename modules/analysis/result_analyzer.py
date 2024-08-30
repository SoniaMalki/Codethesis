import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from modules.analysis.analyzers.citta_acceptance_rate_analyzer import CittaAcceptanceRateAnalyzer
from modules.analysis.analyzers.rhma_acceptance_rate_analyzer import RhmaAcceptanceRateAnalyzer
from modules.analysis.result_loader import ResultLoader
from modules.analysis.analyzers.assignment_analyzer import AssignmentAnalyzer
from modules.analysis.analyzers.scheduling_analyzer import SchedulingAnalyzer
from modules.analysis.analyzers.scheduling_by_assignment_analyzer import SchedulingByAssignmentAnalyzer


class ResultAnalyzer:
    def __init__(self, db_path, experience_id, plots_path, result_path):
        print(
            f"Initializing ResultAnalyzer for experience ID: {experience_id}")
        self.db_path = db_path
        self.current_path = plots_path / experience_id
        self.csv_dir = self.current_path / "csv_results"
        os.makedirs(self.current_path, exist_ok=True)
        os.makedirs(self.csv_dir, exist_ok=True)
        self.experience_id = experience_id
        self.loader = ResultLoader(
            db_path=db_path, experience_id=experience_id, result_path=result_path)

        self.taskset_sets, self.assignment_sets, self.scheduling_sets = self.loader.load_results()

        print("Converting results to DataFrame...")
        self.df_tasksets = pd.DataFrame([vars(t) for t in self.taskset_sets])
        self.df_assignments = pd.DataFrame(
            [vars(a) for a in self.assignment_sets])
        self.df_schedulings = pd.DataFrame(
            [vars(s) for s in self.scheduling_sets])

        print("Merging DataFrames...")
        self.df = self.df_tasksets.merge(
            self.df_assignments,
            on=["taskset_id"],
            suffixes=("_taskset", "_assignment"),
        )
        if not self.df_schedulings.empty:
            self.df = self.df.merge(
                self.df_schedulings,
                on=["taskset_id", "assignment_id"],
                suffixes=("_assignment", "_scheduling"),
            )
        else:
            self.df = self.df.rename(columns={
                "mean_success": "mean_success_assignment",
                "mean_computation_time": "mean_computation_time_assignment"
            })

        print("Calculating task_core_ratio...")
        self.df["task_core_ratio"] = (
            self.df["tasks_per_taskset"] / self.df["number_of_cores"]
        )  # Calcul du ratio tâches/cœurs

        if 'max_utilization' in self.df.columns and 'number_of_cores' in self.df.columns:
            print("Updating max_utilization by dividing by number of cores...")
            self.df['max_utilization'] = self.df['max_utilization'] / \
                self.df['number_of_cores']

        print("ResultAnalyzer initialized successfully.")

    def run_analysis(self):
        print("Running analysis...")
        # self.generate_global_performance_csv()
        # self.analyze_assignment()
        if not self.df_schedulings.empty:
            # self.analyze_scheduling()
            # self.analyze_scheduling_by_assignment()
            # self.analyze_citta_acceptance_rate()
            self.analyze_rhma_acceptance_rate()
        print("Analysis completed.")

    def analyze_assignment(self):
        print("Analyzing assignments...")
        analyzer = AssignmentAnalyzer(self.df, self.current_path, self.csv_dir)
        analyzer.analyze()
        print("Assignment analysis completed.")

    def analyze_scheduling(self):
        print("Analyzing scheduling...")
        analyzer = SchedulingAnalyzer(self.df, self.current_path, self.csv_dir)
        analyzer.analyze()
        print("Scheduling analysis completed.")

    def analyze_scheduling_by_assignment(self):
        print("Analyzing scheduling by assignment...")
        analyzer = SchedulingByAssignmentAnalyzer(
            self.df, self.current_path, self.csv_dir)
        analyzer.analyze()
        print("Scheduling by assignment analysis completed.")

    def analyze_citta_acceptance_rate(self):
        print("Analyzing citta acceptance rate...")
        analyzer = CittaAcceptanceRateAnalyzer(
            self.df, self.current_path, self.csv_dir)
        analyzer.analyze()
        print("Citta acceptance rate analysis completed.")

    def analyze_rhma_acceptance_rate(self):
        print("Analyzing Rhma acceptance rate...")
        analyzer = RhmaAcceptanceRateAnalyzer(
            self.df, self.current_path, self.csv_dir)
        analyzer.analyze()
        print("Rhma acceptance rate analysis completed.")

    def generate_global_performance_csv(self):
        global_performance = self.df.groupby('scheduling_algorithm').agg({
            'mean_success_scheduling': 'mean',
            'mean_computation_time_scheduling': 'mean',
            'mean_overutilization': 'mean'
        }).reset_index()
        global_performance.columns = [
            'Algorithm', 'Success_Rate', 'Avg_Computation_Time', 'Avg_Increased_Utilization']
        global_performance.to_csv(
            self.csv_dir / 'global_performance.csv', index=False)
