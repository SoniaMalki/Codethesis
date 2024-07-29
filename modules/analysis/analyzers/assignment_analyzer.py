import os
import time
import matplotlib.pyplot as plt
import seaborn as sns


class AssignmentAnalyzer:
    def __init__(self, df, current_path):
        self.df = df
        self.assignment_methods = [
            "WorstFitAssigner", "FirstFitAssigner", "BestFitAssigner", "Citta", "Wmin"]
        self.sorting_criteria = ["wcet_ascending", "wcet_descending", "period_ascending", "period_descending",
                                 "utilization_ascending", "utilization_descending", "execution_slack_ascending", "execution_slack_descending", "random_order"]
        self.taskset_parameters = ["interference_factor", "probability_factor",
                                   "max_utilization", "tasks_per_taskset", "number_of_cores"]
        self.current_path = current_path
        self.plots_dir = self.current_path / "plots" / "assignment"
        os.makedirs(self.plots_dir, exist_ok=True)

    def analyze(self):
        self.plot_global_success_rate()
        self.plot_global_computation_time()

        # Exclure Wmin des analyses par critère de tri
        df_subset = self.df[self.df["assignment_method"] != "Wmin"]
        self.plot_success_rate_by_sorting_criteria(df_subset)
        self.plot_computation_time_by_sorting_criteria(df_subset)

    def plot_global_success_rate(self):
        plt.figure(figsize=(10, 6))
        sns.barplot(x="assignment_method",
                    y="mean_success_assignment", data=self.df)
        plt.title("Taux de succès global par algorithme d'assignation")
        plt.xlabel("Algorithme d'assignation")
        plt.ylabel("Taux de succès")
        plt.savefig(self.plots_dir / 'global_success_rate.png')
        plt.close()

    def plot_global_computation_time(self):
        plt.figure(figsize=(10, 6))
        sns.boxplot(x="assignment_method",
                    y="mean_computation_time_assignment", data=self.df)
        plt.title("Temps de calcul global par algorithme d'assignation")
        plt.xlabel("Algorithme d'assignation")
        plt.ylabel("Temps de calcul (s)")
        plt.savefig(self.plots_dir / 'global_computation_time.png')
        plt.close()

    def plot_success_rate_by_sorting_criteria(self, df_subset):
        plt.figure(figsize=(12, 8))
        sns.barplot(x="sorting_criterion", y="mean_success_assignment",
                    hue="assignment_method", data=df_subset)
        plt.title("Taux de succès en fonction du critère de tri")
        plt.xlabel("Critère de tri")
        plt.ylabel("Taux de succès")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(self.plots_dir / 'success_rate_by_sorting_criteria.png')
        plt.close()

    def plot_computation_time_by_sorting_criteria(self, df_subset):
        plt.figure(figsize=(12, 8))
        sns.boxplot(x="sorting_criterion", y="mean_computation_time_assignment",
                    hue="assignment_method", data=df_subset)
        plt.title("Temps de calcul en fonction du critère de tri")
        plt.xlabel("Critère de tri")
        plt.ylabel("Temps de calcul (s)")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(self.plots_dir /
                    'computation_time_by_sorting_criteria.png')
        plt.close()
