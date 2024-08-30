import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class RhmaAcceptanceRateAnalyzer:
    def __init__(self, df, current_path, csv_dir):
        """
        Initializes the observed acceptance rate analyzer for Rhma.

        Args:
            df (pd.DataFrame): DataFrame containing merged data.
            current_path (Path): Current directory path for saving figures.
        """
        self.df = df
        self.current_path = current_path
        self.plots_dir = self.current_path / "rhma_acceptance_rate"
        self.csv_dir = csv_dir
        os.makedirs(self.plots_dir, exist_ok=True)

        # Vérifier la disponibilité de "Citta" et "Rhma" dans les données
        self.is_citta_available = 'Citta' in self.df['assignment_method'].unique(
        )
        self.is_rhma_available = 'Rhma' in self.df['scheduling_algorithm'].unique(
        )

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
        """
        Calculates the observed acceptance rate for Rhma and adds it to the DataFrame.
        """
        if not self.is_citta_available or not self.is_rhma_available:
            return 0

        # Filter for task sets declared schedulable by CITTA
        citta_schedulable_ids = self.df[(self.df['assignment_method'] == 'Citta') &
                                        (self.df['mean_success_assignment'] == 1)]['assignment_id']

        # Filter for task sets successfully scheduled by Rhma
        Rhma_schedulable = self.df[(self.df['scheduling_algorithm'] == 'Rhma') &
                                   (self.df['mean_success_scheduling'] == 1) &
                                   (self.df['assignment_id'].isin(citta_schedulable_ids))]

        # Total task sets declared schedulable by CITTA
        total_citta_schedulable = len(citta_schedulable_ids)
        # Number of task sets actually scheduled by Rhma
        num_Rhma_schedulable = len(Rhma_schedulable)

        # Calculate the acceptance rate
        if total_citta_schedulable > 0:
            acceptance_rate = (num_Rhma_schedulable /
                               total_citta_schedulable) * 100  # as percentage
        else:
            acceptance_rate = 0

        # Store the observed acceptance rate in the DataFrame
        self.df.loc[self.df['scheduling_algorithm'] == 'Rhma',
                    'observed_acceptance_rate'] = acceptance_rate

        return acceptance_rate

    def plot_acceptance_rate(self):
        """
        Plots the observed acceptance rate by Rhma.
        """
        if not self.is_rhma_available:
            return

        plt.figure(figsize=(8, 6))
        ax = sns.barplot(x='scheduling_algorithm', y='observed_acceptance_rate',
                         data=self.df[self.df['scheduling_algorithm'] == 'Rhma'])
        ax.set_title('Observed Acceptance Rate by Rhma')
        ax.set_xlabel('Scheduling Algorithm')
        ax.set_ylabel('Observed Acceptance Rate (%)')
        plt.savefig(self.plots_dir / 'rhma_observed_acceptance_rate.png')
        plt.close()

    def analyze_citta_filtering_efficiency(self):
        """Analyzes the efficiency of CITTA's filtering for RHMA."""
        print("Analyzing CITTA filtering efficiency...")

        # 1. True Positives: Tasks accepted by CITTA and schedulable by RHMA
        true_positives = self.df[(self.df['assignment_method'] == 'Citta') &
                                 (self.df['mean_success_assignment'] == 1) &
                                 (self.df['scheduling_algorithm'] == 'Rhma') &
                                 (self.df['mean_success_scheduling'] == 1)]

        # 2. True Negatives: Tasks rejected by CITTA and not schedulable by RHMA
        true_negatives = self.df[(self.df['assignment_method'] == 'Citta') &
                                 (self.df['mean_success_assignment'] == 0) &
                                 (self.df['scheduling_algorithm'] == 'Rhma') &
                                 (self.df['mean_success_scheduling'] == 0)]

        # 3. Total tasks considered by CITTA for RHMA
        total_tasks = self.df[(self.df['assignment_method'] == 'Citta') &
                              (self.df['scheduling_algorithm'] == 'Rhma')]

        # Calculate rates
        true_positive_rate = len(
            true_positives) / len(total_tasks) * 100 if len(total_tasks) > 0 else 0
        true_negative_rate = len(
            true_negatives) / len(total_tasks) * 100 if len(total_tasks) > 0 else 0
        overall_accuracy = (len(true_positives) + len(true_negatives)) / \
            len(total_tasks) * 100 if len(total_tasks) > 0 else 0

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
        """Analyzes the types of errors made by CITTA in filtering for RHMA."""
        print("Analyzing CITTA errors...")

        # 1. False Positives: Tasks accepted by CITTA but not schedulable by RHMA
        false_positives = self.df[(self.df['assignment_method'] == 'Citta') &
                                  (self.df['mean_success_assignment'] == 1) &
                                  (self.df['scheduling_algorithm'] == 'Rhma') &
                                  (self.df['mean_success_scheduling'] == 0)]

        # 2. False Negatives: Tasks rejected by CITTA but schedulable by RHMA
        false_negatives = self.df[(self.df['assignment_method'] == 'Citta') &
                                  (self.df['mean_success_assignment'] == 0) &
                                  (self.df['scheduling_algorithm'] == 'Rhma') &
                                  (self.df['mean_success_scheduling'] == 1)]

        # Calculate rates
        false_positive_rate = len(
            false_positives) / len(self.df) * 100 if len(self.df) > 0 else 0
        false_negative_rate = len(
            false_negatives) / len(self.df) * 100 if len(self.df) > 0 else 0

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
