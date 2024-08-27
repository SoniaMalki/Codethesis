import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class CittaAcceptanceRateAnalyzer:
    def __init__(self, df, current_path):
        """
        Initializes the acceptance rate analyzer for Citta.

        Args:
            df (pd.DataFrame): DataFrame containing merged data.
            current_path (Path): Current directory path for saving figures.
        """
        self.df = df
        self.current_path = current_path
        self.plots_dir = self.current_path / "citta_acceptance_rate"
        os.makedirs(self.plots_dir, exist_ok=True)

        # Vérifier si "Citta" est une méthode d'assignation présente dans le DataFrame
        self.is_citta_available = 'Citta' in self.df['assignment_method'].unique(
        )

    def analyze(self):
        """
        Calculates and visualizes the acceptance rate by Citta.
        """
        if not self.is_citta_available:
            print("Citta method is not available in the data. Skipping analysis.")
            return

        self.calculate_acceptance_rate()
        self.calculate_schedulability_leakage()
        self.plot_acceptance_rate()
        self.plot_schedulability_leakage()

    def calculate_acceptance_rate(self):
        """
        Calculates the acceptance rate for Citta and adds it to the DataFrame.
        """
        if not self.is_citta_available:
            return 0

        # Filter the DataFrame for Citta results only
        citta_df = self.df[self.df['assignment_method'] == 'Citta']

        # Calculate the total number of task sets tested
        total_tasks = len(citta_df)

        # Calculate the number of task sets deemed schedulable by Citta
        num_schedulable = citta_df['mean_success_assignment'].sum()

        # Calculate the acceptance rate
        if total_tasks > 0:
            acceptance_rate = (num_schedulable / total_tasks) * \
                100  # as percentage
        else:
            acceptance_rate = 0

        # Store the acceptance rate in the DataFrame
        self.df.loc[self.df['assignment_method'] ==
                    'Citta', 'acceptance_rate'] = acceptance_rate
        return acceptance_rate

    def calculate_schedulability_leakage(self):
        """
        Calculates the schedulability leakage to quantify the pessimism of Citta.
        """
        if not self.is_citta_available:
            self.leakage_rate = 0
            return

        # Filter for task sets declared non-schedulable by Citta
        citta_non_schedulable_ids = self.df[(self.df['assignment_method'] == 'Citta') &
                                            (self.df['mean_success_assignment'] == 0)]['assignment_id']

        # Filter for those non-schedulable by Citta but scheduled by RHMA
        leakage_cases = self.df[(self.df['scheduling_algorithm'] == 'RHMA') &
                                (self.df['mean_success_scheduling'] == 1) &
                                (self.df['assignment_id'].isin(citta_non_schedulable_ids))]

        # Calculate total number of task sets tested
        total_tasks = len(self.df['assignment_id'].unique())

        # Calculate leakage rate
        if total_tasks > 0:
            leakage_rate = (len(leakage_cases) / total_tasks) * \
                100  # as percentage
        else:
            leakage_rate = 0

        self.leakage_rate = leakage_rate

    def plot_acceptance_rate(self):
        """
        Plots the acceptance rate for Citta.
        """
        if not self.is_citta_available:
            return

        plt.figure(figsize=(8, 6))
        ax = sns.barplot(x='assignment_method', y='acceptance_rate',
                         data=self.df[self.df['assignment_method'] == 'Citta'])
        ax.set_title('Citta Acceptance Rate')
        ax.set_xlabel('Assignment Method')
        ax.set_ylabel('Acceptance Rate (%)')
        plt.savefig(self.plots_dir / 'citta_acceptance_rate.png')
        plt.close()

    def plot_schedulability_leakage(self):
        """
        Plots the schedulability leakage rate for Citta.
        """
        if not self.is_citta_available:
            return

        plt.figure(figsize=(8, 6))
        sns.barplot(x=['Schedulability Leakage'], y=[self.leakage_rate])
        plt.title('Schedulability Leakage Rate for Citta')
        plt.ylabel('Leakage Rate (%)')
        # Ensure the y-axis always shows up to 100% or beyond
        plt.ylim(0, max(100, self.leakage_rate + 10))
        plt.savefig(self.plots_dir / 'citta_schedulability_leakage.png')
        plt.close()
