import os
import matplotlib.pyplot as plt
import numpy as np
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

    def analyze(self):
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

    def plot_global_success_rate(self):
        plt.figure(figsize=(10, 6))
        ax = sns.barplot(x="scheduling_algorithm", y="mean_success_scheduling",
                         data=self.df, order=self.scheduling_algorithms, errorbar=None, palette=self.algorithm_colors, hue="scheduling_algorithm", legend=False)
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
        plt.figure(figsize=(10, 6))
        ax = sns.boxplot(x="scheduling_algorithm", y="mean_computation_time_scheduling", data=self.df,
                         order=self.scheduling_algorithms, showfliers=False, palette=self.algorithm_colors, hue="scheduling_algorithm", legend=False)
        plt.title("Global Computation Time by Scheduling Algorithm")
        plt.xlabel("Scheduling Algorithm")
        plt.ylabel("Computation Time (s)")
        plt.xticks(rotation=45, ha="right")
        plt.yscale("log")
        plt.tight_layout()
        plt.savefig(self.plots_dir / 'global_computation_time.png')
        plt.close()

    def plot_global_overutilization(self):
        plt.figure(figsize=(10, 6))
        ax = sns.boxplot(x="scheduling_algorithm", y="mean_overutilization", data=self.df,
                         order=self.scheduling_algorithms, showfliers=False, palette=self.algorithm_colors, hue="scheduling_algorithm", legend=False)
        plt.title("Global Overutilization by Scheduling Algorithm")
        plt.xlabel("Scheduling Algorithm")
        plt.ylabel("Overutilization (%)")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(self.plots_dir / 'global_overutilization.png')
        plt.close()

    def plot_success_rate_by_non_preemptive_option(self, df_subset):
        plt.figure(figsize=(12, 8))
        hue_order = [
            scheduling_algorithm for scheduling_algorithm in self.scheduling_algorithms if scheduling_algorithm in ["EarliestDeadlineFirstVariant2", "DeadlineMonotonicVariant2", "CombinedScheduler", "Rhma"]]
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
        plt.figure(figsize=(12, 8))
        hue_order = [
            scheduling_algorithm for scheduling_algorithm in self.scheduling_algorithms if scheduling_algorithm in ["EarliestDeadlineFirstVariant2", "DeadlineMonotonicVariant2", "CombinedScheduler", "Rhma"]]
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
        plt.figure(figsize=(12, 8))
        hue_order = [
            scheduling_algorithm for scheduling_algorithm in self.scheduling_algorithms if scheduling_algorithm in ["EarliestDeadlineFirstVariant2", "DeadlineMonotonicVariant2", "CombinedScheduler", "Rhma"]]
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
        plt.figure(figsize=(10, 6))
        ax = sns.lineplot(x=parameter, y="mean_success_scheduling",
                          hue="scheduling_algorithm", data=self.df.dropna(subset=["mean_success_scheduling"]), marker="o", hue_order=self.scheduling_algorithms, errorbar=None, palette=self.algorithm_colors)
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
        plt.figure(figsize=(10, 6))
        ax = sns.lineplot(x=parameter, y="mean_computation_time_scheduling",
                          hue="scheduling_algorithm", data=self.df.dropna(subset=["mean_computation_time_scheduling"]), marker="o", hue_order=self.scheduling_algorithms, errorbar=None, palette=self.algorithm_colors)
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
        plt.figure(figsize=(10, 6))
        ax = sns.lineplot(x=parameter, y="mean_overutilization", hue="scheduling_algorithm",
                          data=self.df.dropna(subset=["mean_overutilization"]), marker="o", hue_order=self.scheduling_algorithms, errorbar=None, palette=self.algorithm_colors)
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
