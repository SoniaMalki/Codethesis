import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class RhmaAcceptanceRateAnalyzer:
    def __init__(self, df, current_path):
        """
        Initializes the observed acceptance rate analyzer for Rhma.

        Args:
            df (pd.DataFrame): DataFrame containing merged data.
            current_path (Path): Current directory path for saving figures.
        """
        self.df = df
        self.current_path = current_path
        self.plots_dir = self.current_path / "rhma_acceptance_rate"
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
