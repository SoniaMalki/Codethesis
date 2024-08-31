import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class RhmaAcceptanceRateAnalyzer:
    def __init__(self, taskset_sets, assignment_sets, scheduling_sets, df, current_path, csv_dir):
        """
        Initializes the observed acceptance rate analyzer for Rhma.

        Args:
            df (pd.DataFrame): DataFrame containing merged data.
            current_path (Path): Current directory path for saving figures.
        """
        self.taskset_sets = taskset_sets
        self.assignment_sets = assignment_sets
        self.scheduling_sets = scheduling_sets
        self.df = df
        self.current_path = current_path
        self.plots_dir = self.current_path / "rhma_acceptance_rate"
        self.csv_dir = csv_dir
        os.makedirs(self.plots_dir, exist_ok=True)

        # Vérifier la disponibilité de "Citta" et "Rhma" dans les données
        self.is_citta_available = any(
            'Citta' in assignment_set.assignment_method for assignment_set in self.assignment_sets)
        self.is_rhma_available = any(
            'Rhma' in scheduling_set.scheduling_algorithm for scheduling_set in self.scheduling_sets)

    def analyze(self):
        """
        Calculates and visualizes the observed acceptance rate by Rhma.
        """
        if not self.is_citta_available or not self.is_rhma_available:
            print("Citta or Rhma data not available in the dataset. Skipping analysis.")
            return

        self.calculate_acceptance_rate()
        self.plot_acceptance_rate()
        self.analyze_citta_performance()

    def calculate_acceptance_rate(self):
        citta_schedulable = 0
        rhma_schedulable = 0
        total_tasksets = 0

        for taskset_set in self.taskset_sets:
            citta_assignment = self.find_assignment(
                taskset_set.taskset_id, 'Citta')
            if citta_assignment:
                rhma_scheduling = self.find_scheduling(
                    taskset_set.taskset_id, citta_assignment.assignment_id, 'Rhma')
                if rhma_scheduling:
                    for taskset, assignment, scheduling in zip(taskset_set.taskset_list, citta_assignment.assignment_list, rhma_scheduling.scheduling_list):
                        total_tasksets += 1
                        if assignment.success:
                            citta_schedulable += 1
                            if scheduling.success:
                                rhma_schedulable += 1

        self.acceptance_rate = (
            rhma_schedulable / citta_schedulable * 100) if citta_schedulable > 0 else 0

        acceptance_df = pd.DataFrame({
            'Total Tasksets': [total_tasksets],
            'CITTA Schedulable': [citta_schedulable],
            'RHMA Schedulable': [rhma_schedulable],
            'Acceptance Rate (%)': [self.acceptance_rate]
        })
        acceptance_df.to_csv(
            self.csv_dir / 'rhma_acceptance_rate.csv', index=False)

    def plot_acceptance_rate(self):
        plt.figure(figsize=(8, 6))
        sns.barplot(x=['RHMA'], y=[self.acceptance_rate])
        plt.title('Observed Acceptance Rate by RHMA')
        plt.ylabel('Acceptance Rate (%)')
        plt.ylim(0, 100)
        plt.savefig(self.plots_dir / 'rhma_observed_acceptance_rate.png')
        plt.close()

    def analyze_citta_performance(self):
        true_positives = 0
        true_negatives = 0
        false_positives = 0
        false_negatives = 0
        total_tasks = 0

        for taskset_set in self.taskset_sets:
            citta_assignment = self.find_assignment(
                taskset_set.taskset_id, 'Citta')
            if citta_assignment:
                rhma_scheduling_citta = self.find_scheduling(
                    taskset_set.taskset_id, citta_assignment.assignment_id, 'Rhma')
                if rhma_scheduling_citta:
                    for taskset, citta_assignment_item, rhma_scheduling_citta_item in zip(taskset_set.taskset_list, citta_assignment.assignment_list, rhma_scheduling_citta.scheduling_list):
                        total_tasks += 1

                        # Check if RHMA is possible for any assignment
                        rhma_possible = False
                        for assignment_set in self.assignment_sets:
                            if assignment_set.taskset_id == taskset_set.taskset_id:
                                rhma_scheduling = self.find_scheduling(
                                    taskset_set.taskset_id, assignment_set.assignment_id, 'Rhma')
                                if rhma_scheduling:
                                    assignment_item = assignment_set.assignment_list[taskset_set.taskset_list.index(
                                        taskset)]
                                    scheduling_item = rhma_scheduling.scheduling_list[taskset_set.taskset_list.index(
                                        taskset)]
                                    if assignment_item.success and scheduling_item.success:
                                        rhma_possible = True
                                        break

                        if citta_assignment_item.success:
                            if rhma_scheduling_citta_item.success:
                                true_positives += 1
                            else:
                                false_positives += 1
                        else:
                            if rhma_possible:
                                false_negatives += 1
                            else:
                                true_negatives += 1

        true_positive_rate = (
            true_positives / total_tasks * 100) if total_tasks > 0 else 0
        true_negative_rate = (
            true_negatives / total_tasks * 100) if total_tasks > 0 else 0
        false_positive_rate = (
            false_positives / total_tasks * 100) if total_tasks > 0 else 0
        false_negative_rate = (
            false_negatives / total_tasks * 100) if total_tasks > 0 else 0
        overall_accuracy = ((true_positives + true_negatives) /
                            total_tasks * 100) if total_tasks > 0 else 0

        performance_df = pd.DataFrame({
            'True Positive Rate (%)': [true_positive_rate],
            'True Negative Rate (%)': [true_negative_rate],
            'False Positive Rate (%)': [false_positive_rate],
            'False Negative Rate (%)': [false_negative_rate],
            'Overall Accuracy (%)': [overall_accuracy]
        })
        performance_df.to_csv(
            self.csv_dir / 'citta_performance.csv', index=False)

        plt.figure(figsize=(10, 6))
        sns.barplot(data=performance_df)
        plt.title('CITTA Performance Metrics')
        plt.ylabel('Rate (%)')
        plt.ylim(0, 100)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(self.plots_dir / 'citta_performance.png')
        plt.close()

    def find_assignment(self, taskset_id, assignment_method):
        for assignment_set in self.assignment_sets:
            if assignment_set.taskset_id == taskset_id and assignment_set.assignment_method == assignment_method:
                return assignment_set
        return None

    def find_scheduling(self, taskset_id, assignment_id, scheduling_algorithm):
        for scheduling_set in self.scheduling_sets:
            if scheduling_set.taskset_id == taskset_id and scheduling_set.assignment_id == assignment_id and scheduling_set.scheduling_algorithm == scheduling_algorithm:
                return scheduling_set
        return None

    def find_other_assignments(self, taskset_id, exclude_method):
        return [assignment_set for assignment_set in self.assignment_sets
                if assignment_set.taskset_id == taskset_id and assignment_set.assignment_method != exclude_method]
