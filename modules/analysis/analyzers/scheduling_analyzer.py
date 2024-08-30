import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import LogNorm


class SchedulingAnalyzer:
    def __init__(self, df, current_path):
        self.df = df
        self.scheduling_algorithms = ["EarliestDeadlineFirst", "EarliestDeadlineFirstVariant1",
                                      "EarliestDeadlineFirstVariant2", "DeadlineMonotonic", "DeadlineMonotonicVariant1", "DeadlineMonotonicVariant2", "CombinedScheduler", "Rhma"]
        self.non_preemptive_options = [
            "number_of_tasks", "wcet_of_tasks", "system_utilization"]
        self.taskset_parameters = ["interference_factor",
                                   "max_utilization", "task_core_ratio", "tasks_per_taskset", "number_of_cores"]
        self.current_path = current_path
        self.plots_dir = self.current_path / "scheduling"
        self.csv_dir = self.current_path / "csv_results"
        os.makedirs(self.plots_dir, exist_ok=True)

        self.df["non_preemption_option"] = self.df["scheduling_options"].apply(
            lambda x: x.get("non_preemption_time_variant2")
            if isinstance(x, dict)
            else None
        )
        self.df["task_core_ratio"] = self.df["tasks_per_taskset"] / \
            self.df["number_of_cores"]

        self.algorithm_colors = {
            "EarliestDeadlineFirst": "tab:blue",
            "EarliestDeadlineFirstVariant1": "tab:orange",
            "EarliestDeadlineFirstVariant2": "tab:green",
            "DeadlineMonotonic": "tab:red",
            "DeadlineMonotonicVariant1": "tab:purple",
            "DeadlineMonotonicVariant2": "tab:brown",
            "CombinedScheduler": "tab:pink",
            "Rhma": "tab:gray",
        }

        self.max_computation_time = np.nanmax(
            self.df["mean_computation_time_scheduling"])
        self.min_computation_time = np.nanmin(
            self.df["mean_computation_time_scheduling"])

        # Vérifier la disponibilité des algorithmes de planification dans les données
        self.available_algorithms = self.df['scheduling_algorithm'].unique()

    def analyze(self):
        self.generate_scheduling_performance_csv()
        self.generate_scheduling_by_parameter_csv()
        self.generate_non_preemption_analysis_csv()
        self.plot_global_success_rate()
        self.plot_global_computation_time()
        self.plot_global_overutilization()

        # Garder que algos qui utilisent non_preemption_time
        df_subset = self.df[self.df["scheduling_algorithm"].isin(
            ["EarliestDeadlineFirstVariant2", "DeadlineMonotonicVariant2", "CombinedScheduler", "Rhma"])]
        self.plot_success_rate_by_non_preemptive_option(df_subset)
        self.plot_computation_time_by_non_preemptive_option(df_subset)
        self.plot_overutilization_by_non_preemptive_option(df_subset)

        for parameter in self.taskset_parameters:
            self.plot_success_rate_by_taskset_parameter(parameter)
            self.plot_computation_time_by_taskset_parameter(parameter)
            self.plot_overutilization_by_taskset_parameter(parameter)

    def generate_scheduling_performance_csv(self):
        performance = self.df.groupby('scheduling_algorithm').agg({
            'mean_success_scheduling': 'mean',
            'mean_computation_time_scheduling': 'mean',
            'mean_overutilization': 'mean'
        }).reset_index()
        performance.columns = ['Algorithm', 'Success_Rate',
                               'Avg_Computation_Time', 'Avg_Increased_Utilization']
        performance.to_csv(
            self.csv_dir / 'scheduling_performance.csv', index=False)

    def generate_scheduling_by_parameter_csv(self):
        parameters = ["interference_factor", "max_utilization",
                      "task_core_ratio", "tasks_per_taskset", "number_of_cores"]
        results = []
        for param in parameters:
            param_data = self.df.groupby(['scheduling_algorithm', param]).agg({
                'mean_success_scheduling': 'mean',
                'mean_computation_time_scheduling': 'mean',
                'mean_overutilization': 'mean'
            }).reset_index()
            param_data['Parameter'] = param
            param_data.columns = ['Algorithm', 'Value', 'Success_Rate',
                                  'Avg_Computation_Time', 'Avg_Increased_Utilization', 'Parameter']
            results.append(param_data)
        pd.concat(results).to_csv(self.csv_dir /
                                  'scheduling_by_parameter.csv', index=False)

    def generate_non_preemption_analysis_csv(self):
        non_preemption = self.df[self.df['scheduling_algorithm'].isin(
            ['EarliestDeadlineFirstVariant2', 'DeadlineMonotonicVariant2', 'CombinedScheduler', 'Rhma'])]
        analysis = non_preemption.groupby(['scheduling_algorithm', 'non_preemption_option']).agg({
            'mean_success_scheduling': 'mean',
            'mean_computation_time_scheduling': 'mean',
            'mean_overutilization': 'mean'
        }).reset_index()
        analysis.columns = ['Algorithm', 'Non_Preemption_Criterion',
                            'Success_Rate', 'Avg_Computation_Time', 'Avg_Increased_Utilization']
        analysis.to_csv(
            self.csv_dir / 'non_preemption_analysis.csv', index=False)

    def plot_global_success_rate(self):
        available_algorithms = [
            algo for algo in self.scheduling_algorithms if algo in self.available_algorithms]
        if not available_algorithms:
            return

        plt.figure(figsize=(10, 6))
        ax = sns.barplot(x="scheduling_algorithm", y="mean_success_scheduling",
                         data=self.df, order=available_algorithms, errorbar=None, palette=self.algorithm_colors, hue="scheduling_algorithm", legend=False)
        ax.set_ylim(-0.01, 1.1)
        plt.title("Global Success Rate by Scheduling Algorithm")
        plt.xlabel("Scheduling Algorithm")
        plt.xticks(rotation=45, ha="right")
        plt.ylabel("Success Rate")
        self.autolabel_bars(ax)
        plt.tight_layout()
        plt.savefig(self.plots_dir / 'global_success_rate.png')
        plt.close()

    def plot_global_computation_time(self):
        available_algorithms = [
            algo for algo in self.scheduling_algorithms if algo in self.available_algorithms]
        if not available_algorithms:
            return

        plt.figure(figsize=(10, 6))
        ax = sns.boxplot(x="scheduling_algorithm", y="mean_computation_time_scheduling", data=self.df,
                         order=available_algorithms, showfliers=False, palette=self.algorithm_colors, hue="scheduling_algorithm", legend=False)
        plt.title("Global Computation Time by Scheduling Algorithm")
        plt.xlabel("Scheduling Algorithm")
        plt.ylabel("Computation Time (s)")
        plt.xticks(rotation=45, ha="right")
        plt.yscale("log")
        plt.tight_layout()
        plt.savefig(self.plots_dir / 'global_computation_time.png')
        plt.close()

    def plot_global_overutilization(self):
        available_algorithms = [
            algo for algo in self.scheduling_algorithms if algo in self.available_algorithms]
        if not available_algorithms:
            return

        plt.figure(figsize=(10, 6))
        ax = sns.boxplot(x="scheduling_algorithm", y="mean_overutilization", data=self.df,
                         order=available_algorithms, showfliers=False, palette=self.algorithm_colors, hue="scheduling_algorithm", legend=False)
        plt.title("Global Overutilization by Scheduling Algorithm")
        plt.xlabel("Scheduling Algorithm")
        plt.ylabel("Overutilization (%)")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(self.plots_dir / 'global_overutilization.png')
        plt.close()

    def plot_success_rate_by_non_preemptive_option(self, df_subset):
        available_algorithms = [
            algo for algo in ["EarliestDeadlineFirstVariant2", "DeadlineMonotonicVariant2", "CombinedScheduler", "Rhma"] if algo in self.available_algorithms]
        if not available_algorithms:
            return

        plt.figure(figsize=(12, 8))
        hue_order = [
            scheduling_algorithm for scheduling_algorithm in available_algorithms]
        ax = sns.barplot(x="non_preemption_option", y="mean_success_scheduling", hue="scheduling_algorithm", data=df_subset,
                         order=self.non_preemptive_options, hue_order=hue_order, errorbar=None, palette=self.algorithm_colors)
        ax.set_ylim(-0.01, 1.1)
        plt.title("Success Rate by Non-Preemption Option")
        plt.xlabel("Non-Preemption Option")
        plt.ylabel("Success Rate")
        plt.xticks(rotation=45, ha="right")
        self.autolabel_bars(ax)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles=handles, labels=labels, title="Scheduling Algorithm")
        plt.tight_layout()
        plt.savefig(self.plots_dir /
                    'by_non_preemption_option_success_rate.png')
        plt.close()

    def plot_computation_time_by_non_preemptive_option(self, df_subset):
        available_algorithms = [
            algo for algo in ["EarliestDeadlineFirstVariant2", "DeadlineMonotonicVariant2", "CombinedScheduler", "Rhma"] if algo in self.available_algorithms]
        if not available_algorithms:
            return

        plt.figure(figsize=(12, 8))
        hue_order = [
            scheduling_algorithm for scheduling_algorithm in available_algorithms]
        ax = sns.boxplot(x="non_preemption_option", y="mean_computation_time_scheduling", hue="scheduling_algorithm", data=df_subset, order=self.non_preemptive_options,
                         hue_order=hue_order, showfliers=False, palette=self.algorithm_colors)
        plt.title("Computation Time by Non-Preemption Option")
        plt.xlabel("Non-Preemption Option")
        plt.ylabel("Computation Time (s)")
        plt.xticks(rotation=45, ha="right")
        plt.yscale("log")
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles=handles, labels=labels, title="Scheduling Algorithm")
        plt.tight_layout()
        plt.savefig(self.plots_dir /
                    'by_non_preemption_option_computation_time.png')
        plt.close()

    def plot_overutilization_by_non_preemptive_option(self, df_subset):
        available_algorithms = [
            algo for algo in ["EarliestDeadlineFirstVariant2", "DeadlineMonotonicVariant2", "CombinedScheduler", "Rhma"] if algo in self.available_algorithms]
        if not available_algorithms:
            return

        plt.figure(figsize=(12, 8))
        hue_order = [
            scheduling_algorithm for scheduling_algorithm in available_algorithms]
        ax = sns.boxplot(x="non_preemption_option", y="mean_overutilization", hue="scheduling_algorithm", data=df_subset, order=self.non_preemptive_options,
                         hue_order=hue_order, showfliers=False, palette=self.algorithm_colors)
        plt.title("Overutilization by Non-Preemption Option")
        plt.xlabel("Non-Preemption Option")
        plt.ylabel("Overutilization (%)")
        plt.xticks(rotation=45, ha="right")
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles=handles, labels=labels, title="Scheduling Algorithm")
        plt.tight_layout()
        plt.savefig(self.plots_dir /
                    'by_non_preemption_option_overutilization.png')
        plt.close()

    def plot_success_rate_by_taskset_parameter(self, parameter):
        if parameter == "interference_factor":
            self.plot_success_rate_heatmap_interference(parameter)
        else:
            self.plot_success_rate_lineplot(parameter)

    def plot_success_rate_lineplot(self, parameter):
        available_algorithms = [
            algo for algo in self.scheduling_algorithms if algo in self.available_algorithms]
        if not available_algorithms:
            return

        plt.figure(figsize=(10, 6))
        ax = sns.lineplot(x=parameter, y="mean_success_scheduling",
                          hue="scheduling_algorithm", data=self.df.dropna(subset=["mean_success_scheduling"]), marker="o", hue_order=available_algorithms, errorbar=None, palette=self.algorithm_colors)
        plt.title(
            f"Success Rate by {parameter.replace('_', ' ').capitalize()}")
        plt.xlabel(parameter.replace("_", " ").capitalize())
        plt.ylabel("Success Rate")
        ax.set_ylim(-0.01, 1.1)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles=handles, labels=labels, title="Scheduling Algorithm")
        plt.tight_layout()
        plt.savefig(
            self.plots_dir / f'by_parameter_success_rate_with_parameter_{parameter}.png')
        plt.close()

    def plot_success_rate_heatmap_interference(self, parameter):
        for scheduling_algorithm in self.scheduling_algorithms:
            if scheduling_algorithm not in self.available_algorithms:
                continue

            df_subset = self.df[(self.df["scheduling_algorithm"] == scheduling_algorithm) & (
                self.df[parameter].notna())].dropna(subset=["mean_success_scheduling"])
            if df_subset.empty:
                continue
            plt.figure(figsize=(12, 8))
            ax = sns.heatmap(df_subset.pivot_table(index=parameter, columns="probability_factor", values="mean_success_scheduling"),
                             annot=True, cmap="RdYlGn", fmt=".2f", vmin=0, vmax=1)
            plt.title(
                f"Success Rate of {scheduling_algorithm} by Interference Factor and Probability of Interference")
            plt.xlabel("Interference Factor")
            plt.ylabel("Probability of Interference")
            plt.gca().invert_yaxis()
            plt.tight_layout()
            plt.savefig(
                self.plots_dir / f'by_parameter_success_rate_with_parameter_{parameter}_{scheduling_algorithm}.png')
            plt.close()

    def plot_computation_time_by_taskset_parameter(self, parameter):
        if parameter == "interference_factor":
            self.plot_computation_time_heatmap_interference(parameter)
        else:
            self.plot_computation_time_lineplot(parameter)

    def plot_computation_time_lineplot(self, parameter):
        available_algorithms = [
            algo for algo in self.scheduling_algorithms if algo in self.available_algorithms]
        if not available_algorithms:
            return

        plt.figure(figsize=(10, 6))
        ax = sns.lineplot(x=parameter, y="mean_computation_time_scheduling",
                          hue="scheduling_algorithm", data=self.df.dropna(subset=["mean_computation_time_scheduling"]), marker="o", hue_order=available_algorithms, errorbar=None, palette=self.algorithm_colors)
        plt.title(
            f"Computation Time by {parameter.replace('_', ' ').capitalize()}")
        plt.xlabel(parameter.replace("_", " ").capitalize())
        plt.ylabel("Computation Time (s)")
        plt.yscale("log")
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles=handles, labels=labels, title="Scheduling Algorithm")
        plt.tight_layout()
        plt.savefig(
            self.plots_dir / f'by_parameter_computation_time_with_parameter_{parameter}.png')
        plt.close()

    def plot_computation_time_heatmap_interference(self, parameter):
        for scheduling_algorithm in self.scheduling_algorithms:
            if scheduling_algorithm not in self.available_algorithms:
                continue

            df_subset = self.df[(self.df["scheduling_algorithm"] == scheduling_algorithm) & (
                self.df[parameter].notna())].dropna(subset=["mean_computation_time_scheduling"])
            if df_subset.empty:
                continue
            plt.figure(figsize=(12, 8))
            vmin = self.min_computation_time if self.min_computation_time > 0 else 1e-6
            ax = sns.heatmap(df_subset.pivot_table(index=parameter, columns="probability_factor", values="mean_computation_time_scheduling"),
                             annot=True, cmap="RdYlBu_r", fmt=".6f", norm=LogNorm(vmin=vmin, vmax=self.max_computation_time))
            plt.title(
                f"Computation Time of {scheduling_algorithm} by Interference Factor and Probability of Interference")
            plt.xlabel("Interference Factor")
            plt.ylabel("Probability of Interference")
            plt.gca().invert_yaxis()
            plt.tight_layout()
            plt.savefig(
                self.plots_dir / f'by_parameter_computation_time_with_parameter_{parameter}_{scheduling_algorithm}.png')
            plt.close()

    def plot_overutilization_by_taskset_parameter(self, parameter):
        if parameter == "interference_factor":
            self.plot_overutilization_heatmap_interference(parameter)
        else:
            self.plot_overutilization_lineplot(parameter)

    def plot_overutilization_lineplot(self, parameter):
        available_algorithms = [
            algo for algo in self.scheduling_algorithms if algo in self.available_algorithms]
        if not available_algorithms:
            return

        plt.figure(figsize=(10, 6))
        ax = sns.lineplot(x=parameter, y="mean_overutilization", hue="scheduling_algorithm",
                          data=self.df.dropna(subset=["mean_overutilization"]), marker="o", hue_order=available_algorithms, errorbar=None, palette=self.algorithm_colors)
        plt.title(
            f"Overutilization by {parameter.replace('_', ' ').capitalize()}")
        plt.xlabel(parameter.replace("_", " ").capitalize())
        plt.ylabel("Overutilization (%)")
        plt.yscale("log")
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles=handles, labels=labels, title="Scheduling Algorithm")
        plt.tight_layout()
        plt.savefig(
            self.plots_dir / f'by_parameter_overutilization_with_parameter_{parameter}.png')
        plt.close()

    def plot_overutilization_heatmap_interference(self, parameter):
        for scheduling_algorithm in self.scheduling_algorithms:
            if scheduling_algorithm not in self.available_algorithms:
                continue

            df_subset = self.df[(self.df["scheduling_algorithm"] == scheduling_algorithm) & (
                self.df[parameter].notna())].dropna(subset=["mean_overutilization"])
            if df_subset.empty:
                continue
            plt.figure(figsize=(12, 8))
            vmin = self.min_computation_time if self.min_computation_time > 0 else 1e-6
            ax = sns.heatmap(df_subset.pivot_table(index=parameter, columns="probability_factor", values="mean_overutilization"),
                             annot=True, cmap="RdYlBu_r", fmt=".6f", norm=LogNorm(vmin=vmin, vmax=self.max_computation_time))
            plt.title(
                f"Overutilization of {scheduling_algorithm} by Interference Factor and Probability of Interference")
            plt.xlabel("Interference Factor")
            plt.ylabel("Probability of Interference")
            plt.gca().invert_yaxis()
            plt.tight_layout()
            plt.savefig(
                self.plots_dir / f'by_parameter_overutilization_with_parameter_{parameter}_{scheduling_algorithm}.png')
            plt.close()

    def autolabel_bars(self, ax):
        for p in ax.patches:
            height = p.get_height()
            ax.text(p.get_x() + p.get_width() / 2., height / 2, f"{height:.2f}",
                    ha="center", va="center", rotation=90, color='black')
