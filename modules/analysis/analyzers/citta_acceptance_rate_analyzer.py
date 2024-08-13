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

    def analyze(self):
        """
        Calculates and visualizes the acceptance rate by Citta.
        """
        self.calculate_acceptance_rate()
        self.plot_acceptance_rate()

    def calculate_acceptance_rate(self):
        """
        Calculates the acceptance rate for Citta and adds it to the DataFrame.
        """
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

    def plot_acceptance_rate(self):
        """
        Plots the acceptance rate for Citta.
        """
        plt.figure(figsize=(8, 6))
        ax = sns.barplot(x='assignment_method', y='acceptance_rate',
                         data=self.df[self.df['assignment_method'] == 'Citta'])
        ax.set_title('Citta Acceptance Rate')
        ax.set_xlabel('Assignment Method')
        ax.set_ylabel('Acceptance Rate (%)')
        plt.savefig(self.plots_dir / 'citta_acceptance_rate.png')
        plt.close()
