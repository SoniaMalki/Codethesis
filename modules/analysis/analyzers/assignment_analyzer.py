import pandas as pd
import matplotlib
import seaborn as sns
import numpy as np
import os
from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
matplotlib.use('Agg')


class AssignmentAnalyzer:
    def __init__(self, df, current_path, csv_dir):
        self.df = df
        self.assignment_methods = [
            "FirstFitAssigner", "BestFitAssigner", "WorstFitAssigner", "Wmin", "Citta"]
        self.sorting_criteria = ["wcet_ascending", "wcet_descending", "period_ascending", "period_descending",
                                 "utilization_ascending", "utilization_descending", "execution_slack_ascending", "execution_slack_descending", "random_order"]
        self.taskset_parameters = ["interference_factor", "max_utilization",
                                   "task_core_ratio", "tasks_per_taskset", "number_of_cores"]
        self.current_path = current_path
        self.plots_dir = self.current_path / "assignment"
        self.csv_dir = csv_dir
        os.makedirs(self.plots_dir, exist_ok=True)

        self.df["task_core_ratio"] = self.df["tasks_per_taskset"] / \
            self.df["number_of_cores"]

        self.algorithm_colors = {
            "FirstFitAssigner": "tab:blue",
            "BestFitAssigner": "tab:orange",
            "WorstFitAssigner": "tab:green",
            "Wmin": "tab:red",
            "Citta": "tab:purple"
        }

        self.max_computation_time = np.nanmax(
            self.df["mean_computation_time_assignment"])
        self.min_computation_time = np.nanmin(
            self.df["mean_computation_time_assignment"])

        # Mise à jour des méthodes d'assignation disponibles dans les données
        self.available_methods = self.df['assignment_method'].unique()

        # Mise à jour des critères de tri disponibles dans les données
        self.available_sorting_criteria = self.df['sorting_criterion'].unique()

    def analyze(self):
        self.generate_assignment_performance_csv()
        self.generate_assignment_by_parameter_csv()
        self.plot_global_success_rate()
        self.plot_global_computation_time()

        # Exclure Wmin des analyses par critère de tri
        df_subset = self.df[self.df["assignment_method"] != "Wmin"]
        self.plot_success_rate_by_sorting_criteria(df_subset)
        self.plot_computation_time_by_sorting_criteria(df_subset)

        for parameter in self.taskset_parameters:
            self.plot_success_rate_by_taskset_parameter(parameter)
            self.plot_computation_time_by_taskset_parameter(parameter)

    def generate_assignment_performance_csv(self):
        performance = self.df.groupby(['assignment_method', 'sorting_criterion']).agg({
            'mean_success_assignment': 'mean',
            'mean_computation_time_assignment': 'mean'
        }).reset_index()
        performance.columns = [
            'Algorithm', 'Sorting_Criterion', 'Success_Rate', 'Avg_Computation_Time']
        performance.to_csv(
            self.csv_dir / 'assignment_performance.csv', index=False)

    def generate_assignment_by_parameter_csv(self):
        parameters = ["interference_probability", "max_utilization",
                      "task_core_ratio", "tasks_per_taskset", "number_of_cores"]
        results = []

        # Traitement spécial pour interference_factor et probability_factor
        if_pf_data = self.df.groupby(['assignment_method', 'interference_factor', 'probability_factor']).agg({
            'mean_success_assignment': 'mean',
            'mean_computation_time_assignment': 'mean'
        }).reset_index()
        if_pf_data['Parameter'] = 'interference_probability'
        if_pf_data['Value'] = if_pf_data.apply(
            lambda row: f"({row['interference_factor']}, {row['probability_factor']})", axis=1)
        if_pf_data = if_pf_data.drop(
            ['interference_factor', 'probability_factor'], axis=1)
        results.append(if_pf_data)

        # Exclure 'interference_probability' car déjà traité
        for param in parameters[1:]:
            param_data = self.df.groupby(['assignment_method', param]).agg({
                'mean_success_assignment': 'mean',
                'mean_computation_time_assignment': 'mean'
            }).reset_index()
            param_data['Parameter'] = param
            param_data = param_data.rename(columns={param: 'Value'})
            results.append(param_data)

        final_df = pd.concat(results)
        final_df = final_df.rename(columns={
            'assignment_method': 'Algorithm',
            'mean_success_assignment': 'Success_Rate',
            'mean_computation_time_assignment': 'Avg_Computation_Time'
        })
        final_df = final_df[['Algorithm', 'Parameter',
                             'Value', 'Success_Rate', 'Avg_Computation_Time']]
        final_df.to_csv(
            self.csv_dir / 'assignment_by_parameter.csv', index=False)

    def plot_global_success_rate(self):
        plt.figure(figsize=(10, 6))
        # Filtrer les méthodes d'assignation disponibles
        available_methods = [
            method for method in self.assignment_methods if method in self.available_methods]
        ax = sns.barplot(x="assignment_method", y="mean_success_assignment",
                         data=self.df, order=available_methods, errorbar=None, palette=self.algorithm_colors, hue="assignment_method", legend=False)
        ax.set_ylim(-0.01, 1.1)
        plt.title("Global Success Rate by Assignment Method")
        plt.xlabel("Assignment Method")
        plt.ylabel("Success Rate")
        self.autolabel_bars(ax)
        plt.savefig(self.plots_dir / 'global_success_rate.png')
        plt.close()

    def plot_global_computation_time(self):
        plt.figure(figsize=(10, 6))
        # Filtrer les méthodes d'assignation disponibles
        available_methods = [
            method for method in self.assignment_methods if method in self.available_methods]
        ax = sns.boxplot(x="assignment_method", y="mean_computation_time_assignment", data=self.df,
                         order=available_methods, showfliers=False, palette=self.algorithm_colors, hue="assignment_method", legend=False)
        plt.title("Global Computation Time by Assignment Method")
        plt.xlabel("Assignment Method")
        plt.ylabel("Computation Time (s)")
        plt.yscale("log")
        plt.savefig(self.plots_dir / 'global_computation_time.png')
        plt.close()

    def plot_success_rate_by_sorting_criteria(self, df_subset):
        plt.figure(figsize=(12, 8))
        # Filtrer les méthodes d'assignation disponibles
        hue_order = [assignment_method for assignment_method in self.assignment_methods if assignment_method in self.available_methods and assignment_method != "Wmin"]
        # Filtrer les critères de tri disponibles
        available_sorting_criteria = [
            criterion for criterion in self.sorting_criteria if criterion in self.available_sorting_criteria]
        ax = sns.barplot(x="sorting_criterion", y="mean_success_assignment", hue="assignment_method", data=df_subset,
                         order=available_sorting_criteria, hue_order=hue_order, errorbar=None, palette=self.algorithm_colors)
        ax.set_ylim(-0.01, 1.1)
        plt.title("Success Rate by Sorting Criterion")
        plt.xlabel("Sorting Criterion")
        plt.ylabel("Success Rate")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        self.autolabel_bars(ax)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles=handles, labels=labels, title="Assignment Method")
        plt.savefig(self.plots_dir / 'by_sorting_criterion_success_rate.png')
        plt.close()

    def plot_computation_time_by_sorting_criteria(self, df_subset):
        plt.figure(figsize=(12, 8))
        # Filtrer les méthodes d'assignation disponibles
        hue_order = [assignment_method for assignment_method in self.assignment_methods if assignment_method in self.available_methods and assignment_method != "Wmin"]
        # Filtrer les critères de tri disponibles
        available_sorting_criteria = [
            criterion for criterion in self.sorting_criteria if criterion in self.available_sorting_criteria]
        ax = sns.boxplot(x="sorting_criterion", y="mean_computation_time_assignment", hue="assignment_method", data=df_subset, order=available_sorting_criteria,
                         hue_order=hue_order, showfliers=False, palette=self.algorithm_colors)
        plt.title("Computation Time by Sorting Criterion")
        plt.xlabel("Sorting Criterion")
        plt.ylabel("Computation Time (s)")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.yscale("log")
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles=handles, labels=labels, title="Assignment Method")
        plt.savefig(self.plots_dir /
                    'by_sorting_criterion_computation_time.png')
        plt.close()

    def plot_success_rate_by_taskset_parameter(self, parameter):
        if parameter == "interference_factor":
            self.plot_success_rate_heatmap_interference(parameter)
        else:
            self.plot_success_rate_lineplot(parameter)

    def plot_success_rate_lineplot(self, parameter):
        plt.figure(figsize=(10, 6))
        # Filtrer les méthodes d'assignation disponibles
        hue_order = [
            assignment_method for assignment_method in self.assignment_methods if assignment_method in self.available_methods]
        ax = sns.lineplot(x=parameter, y="mean_success_assignment",
                          hue="assignment_method", data=self.df.dropna(subset=["mean_success_assignment"]), marker="o", hue_order=hue_order, errorbar=None, palette=self.algorithm_colors)
        ax.set_ylim(-0.01, 1.1)
        plt.title(
            f"Success Rate by {parameter.replace('_', ' ').capitalize()}")
        plt.xlabel(parameter.replace("_", " ").capitalize())
        plt.ylabel("Success Rate")
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles=handles, labels=labels, title="Assignment Method")
        plt.savefig(
            self.plots_dir / f'by_parameter_success_rate_with_parameter_{parameter}.png')
        plt.close()

    def plot_success_rate_heatmap_interference(self, parameter):
        for assignment_method in self.assignment_methods:
            if assignment_method not in self.available_methods:
                continue
            df_subset = self.df[(self.df["assignment_method"] == assignment_method) & (
                self.df[parameter].notna())].dropna(subset=["mean_success_assignment"])
            if df_subset.empty:
                continue
            plt.figure(figsize=(12, 8))
            ax = sns.heatmap(df_subset.pivot_table(index=parameter, columns="probability_factor", values="mean_success_assignment"),
                             annot=True, cmap="RdYlGn", fmt=".2f", vmin=0, vmax=1)
            plt.title(
                f"Success Rate of {assignment_method} by Interference Factor and Probability of Interference")
            plt.xlabel("Interference Factor")
            plt.ylabel("Probability of Interference")
            plt.gca().invert_yaxis()
            plt.savefig(
                self.plots_dir / f'by_parameter_success_rate_with_parameter_{parameter}_{assignment_method}.png')
            plt.close()

    def plot_computation_time_by_taskset_parameter(self, parameter):
        if parameter == "interference_factor":
            self.plot_computation_time_heatmap_interference(parameter)
        else:
            self.plot_computation_time_lineplot(parameter)

    def plot_computation_time_lineplot(self, parameter):
        plt.figure(figsize=(10, 6))
        # Filtrer les méthodes d'assignation disponibles
        hue_order = [
            assignment_method for assignment_method in self.assignment_methods if assignment_method in self.available_methods]
        ax = sns.lineplot(x=parameter, y="mean_computation_time_assignment",
                          hue="assignment_method", data=self.df.dropna(subset=["mean_computation_time_assignment"]), marker="o", hue_order=hue_order, errorbar=None, palette=self.algorithm_colors)
        plt.title(
            f"Computation Time by {parameter.replace('_', ' ').capitalize()}")
        plt.xlabel(parameter.replace("_", " ").capitalize())
        plt.ylabel("Computation Time (s)")
        plt.yscale("log")
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles=handles, labels=labels, title="Assignment Method")
        plt.savefig(
            self.plots_dir / f'by_parameter_computation_time_{parameter}.png')
        plt.close()

    def plot_computation_time_heatmap_interference(self, parameter):
        for assignment_method in self.assignment_methods:
            if assignment_method not in self.available_methods:
                continue
            df_subset = self.df[(self.df["assignment_method"] == assignment_method) & (
                self.df[parameter].notna())].dropna(subset=["mean_computation_time_assignment"])
            if df_subset.empty:
                continue
            plt.figure(figsize=(12, 8))
            ax = sns.heatmap(df_subset.pivot_table(index=parameter, columns="probability_factor", values="mean_computation_time_assignment"),
                             annot=True, cmap="RdYlBu_r", fmt=".6f", norm=LogNorm(vmin=self.min_computation_time, vmax=self.max_computation_time))
            plt.title(
                f"Computation Time of {assignment_method} by Interference Factor and Probability of Interference")
            plt.xlabel("Interference Factor")
            plt.ylabel("Probability of Interference")
            plt.gca().invert_yaxis()
            plt.savefig(
                self.plots_dir / f'by_parameter_computation_time_with_parameter_{parameter}_{assignment_method}.png')
            plt.close()

    def autolabel_bars(self, ax):
        for p in ax.patches:
            height = p.get_height()
            ax.text(p.get_x() + p.get_width() / 2., height / 2, f"{height:.2f}",
                    ha="center", va="center", rotation=90, color='black')
