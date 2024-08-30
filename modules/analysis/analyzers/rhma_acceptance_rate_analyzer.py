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

        self.analyze_citta_filtering_efficiency()
        self.analyze_citta_errors()

    def calculate_acceptance_rate(self):
        citta_schedulable = 0
        rhma_schedulable = 0
        total_tasksets = 0

        for assignment_set, scheduling_set in zip(self.assignment_sets, self.scheduling_sets):
            if assignment_set.assignment_method == 'Citta':
                for assignment, scheduling in zip(assignment_set.assignment_list, scheduling_set.scheduling_list):
                    total_tasksets += 1
                    if assignment.success:
                        citta_schedulable += 1
                        if scheduling.success and scheduling_set.scheduling_algorithm == 'Rhma':
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

    def analyze_citta_filtering_efficiency(self):
        true_positives = 0
        true_negatives = 0
        total_tasks = 0

        for assignment_set, scheduling_set in zip(self.assignment_sets, self.scheduling_sets):
            if assignment_set.assignment_method == 'Citta' and scheduling_set.scheduling_algorithm == 'Rhma':
                for assignment, scheduling in zip(assignment_set.assignment_list, scheduling_set.scheduling_list):
                    total_tasks += 1
                    if assignment.success and scheduling.success:
                        true_positives += 1
                    elif not assignment.success and not scheduling.success:
                        true_negatives += 1

        true_positive_rate = (
            true_positives / total_tasks * 100) if total_tasks > 0 else 0
        true_negative_rate = (
            true_negatives / total_tasks * 100) if total_tasks > 0 else 0
        overall_accuracy = ((true_positives + true_negatives) /
                            total_tasks * 100) if total_tasks > 0 else 0

        # Create DataFrame for CSV
        filtering_efficiency_df = pd.DataFrame({
            'True Positive Rate (%)': [true_positive_rate],
            'True Negative Rate (%)': [true_negative_rate],
            'Overall Accuracy (%)': [overall_accuracy]
        })
        filtering_efficiency_df.to_csv(
            self.csv_dir / 'citta_filtering_efficiency.csv', index=False)

        # Create bar plot
        plt.figure(figsize=(8, 6))
        sns.barplot(data=filtering_efficiency_df)
        plt.title('CITTA Filtering Efficiency for RHMA')
        plt.ylabel('Rate (%)')
        plt.ylim(0, 110)  # Set y-axis limit for better visualization
        plt.savefig(self.plots_dir / 'citta_filtering_efficiency.png')
        plt.close()

    def analyze_citta_errors(self):
        false_positives = 0
        false_negatives = 0
        total_tasks = 0

        for assignment_set, scheduling_set in zip(self.assignment_sets, self.scheduling_sets):
            if assignment_set.assignment_method == 'Citta' and scheduling_set.scheduling_algorithm == 'Rhma':
                for assignment, scheduling in zip(assignment_set.assignment_list, scheduling_set.scheduling_list):
                    total_tasks += 1
                    if assignment.success and not scheduling.success:
                        false_positives += 1
                    elif not assignment.success and scheduling.success:
                        false_negatives += 1

        # Calculate rates
        false_positive_rate = (
            false_positives / total_tasks * 100) if total_tasks > 0 else 0
        false_negative_rate = (
            false_negatives / total_tasks * 100) if total_tasks > 0 else 0

        # Create DataFrame for CSV
        error_rates_df = pd.DataFrame({
            'False Positive Rate (%)': [false_positive_rate],
            'False Negative Rate (%)': [false_negative_rate]
        })
        error_rates_df.to_csv(
            self.csv_dir / 'citta_error_rates.csv', index=False)

        # Create bar plot
        plt.figure(figsize=(8, 6))
        sns.barplot(data=error_rates_df)
        plt.title('CITTA Error Rates for RHMA')
        plt.ylabel('Rate (%)')
        plt.ylim(0, 110)
        plt.savefig(self.plots_dir / 'citta_error_rates.png')
        plt.close()
