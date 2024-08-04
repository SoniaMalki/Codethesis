import os
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.colors import LogNorm


class SchedulingByAssignmentAnalyzer:
    def __init__(self, df, current_path):
        self.df = df
        self.scheduling_algorithms = ["EarliestDeadlineFirst", "EarliestDeadlineFirstVariant1",
                                      "EarliestDeadlineFirstVariant2", "DeadlineMonotonic", "DeadlineMonotonicVariant1", "DeadlineMonotonicVariant2", "CombinedScheduler", "Rhma"]
        self.non_preemptive_options = [
            "number_of_tasks", "wcet_of_tasks", "system_utilization"]
        self.taskset_parameters = ["interference_factor",
                                   "max_utilization", "task_core_ratio", "tasks_per_taskset", "number_of_cores"]
        self.assignment_methods = ["FirstFitAssigner", "BestFitAssigner",
                                   "WorstFitAssigner", "Wmin", "Citta"]
        self.sorting_criteria = ["wcet_ascending", "wcet_descending", "period_ascending", "period_descending",
                                 "utilization_ascending", "utilization_descending", "execution_slack_ascending", "execution_slack_descending", "random_order"]
        self.current_path = current_path
        self.plots_dir = self.current_path / \
            "plots" / "scheduling_by_assignment"
        os.makedirs(self.plots_dir, exist_ok=True)

        self.df["non_preemption_option"] = self.df["scheduling_options"].apply(
            lambda x: x.get("non_preemption_time_variant2")
            if isinstance(x, dict)
            else None
        )
        self.df["task_core_ratio"] = self.df["tasks_per_taskset"] / \
            self.df["number_of_cores"]

        self.df["assignment_scheduling_combination"] = self.df["scheduling_algorithm"] + \
            "_" + self.df["assignment_method"]

        self.algorithm_colors = {
            "EarliestDeadlineFirst_FirstFitAssigner": "tab:blue",
            "EarliestDeadlineFirst_BestFitAssigner": "tab:orange",
            "EarliestDeadlineFirst_WorstFitAssigner": "tab:green",
            "EarliestDeadlineFirst_Wmin": "tab:red",
            "EarliestDeadlineFirst_Citta": "tab:purple",
            "EarliestDeadlineFirstVariant1_FirstFitAssigner": "tab:cyan",
            "EarliestDeadlineFirstVariant1_BestFitAssigner": "tab:pink",
            "EarliestDeadlineFirstVariant1_WorstFitAssigner": "tab:olive",
            "EarliestDeadlineFirstVariant1_Wmin": "tab:brown",
            "EarliestDeadlineFirstVariant1_Citta": "tab:gray",
            "EarliestDeadlineFirstVariant2_FirstFitAssigner": "blue",
            "EarliestDeadlineFirstVariant2_BestFitAssigner": "orange",
            "EarliestDeadlineFirstVariant2_WorstFitAssigner": "green",
            "EarliestDeadlineFirstVariant2_Wmin": "red",
            "EarliestDeadlineFirstVariant2_Citta": "purple",
            "DeadlineMonotonic_FirstFitAssigner": "darkblue",
            "DeadlineMonotonic_BestFitAssigner": "darkorange",
            "DeadlineMonotonic_WorstFitAssigner": "darkgreen",
            "DeadlineMonotonic_Wmin": "darkred",
            "DeadlineMonotonic_Citta": "indigo",
            "DeadlineMonotonicVariant1_FirstFitAssigner": "teal",
            "DeadlineMonotonicVariant1_BestFitAssigner": "salmon",
            "DeadlineMonotonicVariant1_WorstFitAssigner": "lime",
            "DeadlineMonotonicVariant1_Wmin": "firebrick",
            "DeadlineMonotonicVariant1_Citta": "dimgray",
            "DeadlineMonotonicVariant2_FirstFitAssigner": "dodgerblue",
            "DeadlineMonotonicVariant2_BestFitAssigner": "coral",
            "DeadlineMonotonicVariant2_WorstFitAssigner": "forestgreen",
            "DeadlineMonotonicVariant2_Wmin": "crimson",
            "DeadlineMonotonicVariant2_Citta": "darkslateblue",
            "CombinedScheduler_FirstFitAssigner": "deepskyblue",
            "CombinedScheduler_BestFitAssigner": "sandybrown",
            "CombinedScheduler_WorstFitAssigner": "mediumseagreen",
            "CombinedScheduler_Wmin": "indianred",
            "CombinedScheduler_Citta": "mediumpurple",
            "Rhma_FirstFitAssigner": "lightskyblue",
            "Rhma_BestFitAssigner": "peru",
            "Rhma_WorstFitAssigner": "yellowgreen",
            "Rhma_Wmin": "lightcoral",
            "Rhma_Citta": "plum",
        }

        self.max_computation_time = np.nanmax(
            self.df["mean_computation_time_scheduling"])
        self.min_computation_time = np.nanmin(
            self.df["mean_computation_time_scheduling"])

    def analyze(self):
        self.plot_global_success_rate()
        self.plot_global_computation_time()
        self.plot_global_overutilization()

        df_subset = self.df[self.df["assignment_method"] != "Wmin"]
        for sorting_criterion in self.sorting_criteria:
            df_subset_2 = df_subset[df_subset["sorting_criterion"]
                                    == sorting_criterion]
            self.plot_success_rate_by_sorting_criteria(
                df_subset_2, sorting_criterion)
            self.plot_computation_time_by_sorting_criteria(
                df_subset_2, sorting_criterion)

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
        ax = sns.barplot(x="assignment_scheduling_combination", y="mean_success_scheduling",
                         data=self.df, order=[
                             f"{s}_{a}" for s in self.scheduling_algorithms for a in self.assignment_methods], errorbar=None, palette=self.algorithm_colors, hue="assignment_scheduling_combination", legend=False)
        ax.set_ylim(-0.01, 1.1)
        plt.title("Global Success Rate")
        plt.xlabel("Scheduling/Assignment Combination")
        plt.xticks(rotation=90, ha="right")
        plt.ylabel("Success Rate")
        self.autolabel_bars(ax)
        plt.tight_layout()
        plt.savefig(self.plots_dir / 'global_success_rate.png')
        plt.close()

    def plot_global_computation_time(self):
        plt.figure(figsize=(10, 6))
        ax = sns.boxplot(x="assignment_scheduling_combination", y="mean_computation_time_scheduling", data=self.df,
                         order=[
                             f"{s}_{a}" for s in self.scheduling_algorithms for a in self.assignment_methods], showfliers=False, palette=self.algorithm_colors, hue="assignment_scheduling_combination", legend=False)
        plt.title("Global Computation Time")
        plt.xlabel("Scheduling/Assignment Combination")
        plt.ylabel("Computation Time (s)")
        plt.xticks(rotation=90, ha="right")
        plt.yscale("log")
        plt.tight_layout()
        plt.savefig(self.plots_dir / 'global_computation_time.png')
        plt.close()

    def plot_global_overutilization(self):
        plt.figure(figsize=(10, 6))
        ax = sns.boxplot(x="assignment_scheduling_combination", y="mean_overutilization", data=self.df,
                         order=[
                             f"{s}_{a}" for s in self.scheduling_algorithms for a in self.assignment_methods], showfliers=False, palette=self.algorithm_colors, hue="assignment_scheduling_combination", legend=False)
        plt.title("Global Overutilization")
        plt.xlabel("Scheduling/Assignment Combination")
        plt.ylabel("Overutilization (%)")
        plt.xticks(rotation=90, ha="right")
        plt.tight_layout()
        plt.savefig(self.plots_dir / 'global_overutilization.png')
        plt.close()

    def plot_success_rate_by_non_preemptive_option(self, df_subset):
        plt.figure(figsize=(12, 8))
        ax = sns.barplot(x="non_preemption_option", y="mean_success_scheduling", hue="assignment_scheduling_combination", data=df_subset,
                         order=self.non_preemptive_options, errorbar=None, palette=self.algorithm_colors)
        ax.set_ylim(-0.01, 1.1)
        plt.title("Success Rate by Non-Preemption Option")
        plt.xlabel("Non-Preemption Option")
        plt.ylabel("Success Rate")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        self.autolabel_bars(ax)
        plt.legend(title="Scheduling/Assignment Combination",
                   bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.savefig(
            self.plots_dir / 'by_non_preemption_option_success_rate.png', bbox_inches='tight')
        plt.close()

    def plot_computation_time_by_non_preemptive_option(self, df_subset):
        plt.figure(figsize=(12, 8))
        ax = sns.boxplot(x="non_preemption_option", y="mean_computation_time_scheduling", hue="assignment_scheduling_combination", data=df_subset, order=self.non_preemptive_options,
                         showfliers=False, palette=self.algorithm_colors)
        plt.title("Computation Time by Non-Preemption Option")
        plt.xlabel("Non-Preemption Option")
        plt.ylabel("Computation Time (s)")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.yscale("log")
        plt.legend(title="Scheduling/Assignment Combination",
                   bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.savefig(
            self.plots_dir / 'by_non_preemption_option_computation_time.png', bbox_inches='tight')
        plt.close()

    def plot_overutilization_by_non_preemptive_option(self, df_subset):
        plt.figure(figsize=(12, 8))
        ax = sns.boxplot(x="non_preemption_option", y="mean_overutilization", hue="assignment_scheduling_combination", data=df_subset, order=self.non_preemptive_options,
                         showfliers=False, palette=self.algorithm_colors)
        plt.title("Overutilization by Non-Preemption Option")
        plt.xlabel("Non-Preemption Option")
        plt.ylabel("Overutilization (%)")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.legend(title="Scheduling/Assignment Combination",
                   bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.savefig(
            self.plots_dir / 'by_non_preemption_option_overutilization.png', bbox_inches='tight')
        plt.close()

    def plot_success_rate_by_taskset_parameter(self, parameter):
        if parameter == "interference_factor":
            self.plot_success_rate_heatmap_interference(parameter)
        else:
            self.plot_success_rate_lineplot(parameter)

    def plot_success_rate_lineplot(self, parameter):
        plt.figure(figsize=(10, 6))
        ax = sns.lineplot(x=parameter, y="mean_success_scheduling",
                          hue="assignment_scheduling_combination", data=self.df.dropna(subset=["mean_success_scheduling"]), marker="o", errorbar=None, palette=self.algorithm_colors)
        plt.title(
            f"Success Rate by {parameter.replace('_', ' ').capitalize()}")
        plt.xlabel(parameter.replace("_", " ").capitalize())
        plt.ylabel("Success Rate")
        plt.legend(title="Scheduling/Assignment Combination",
                   bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.savefig(
            self.plots_dir / f'by_parameter_success_rate_with_parameter_{parameter}.png', bbox_inches='tight')
        plt.close()

    def plot_success_rate_heatmap_interference(self, parameter):
        plt.figure(figsize=(12, 8))
        ax = sns.heatmap(self.df.dropna(subset=["mean_success_scheduling"]).pivot_table(index=parameter, columns="probability_factor", values="mean_success_scheduling", aggfunc='mean', dropna=True),
                         annot=True, cmap="viridis", fmt=".2f", vmin=0, vmax=1)
        plt.title(
            f"Success Rate by Interference Factor and Probability of Interference")
        plt.xlabel("Interference Factor")
        plt.ylabel("Probability of Interference")
        plt.gca().invert_yaxis()
        plt.savefig(
            self.plots_dir / f'by_parameter_success_rate_with_parameter_{parameter}.png')
        plt.close()

    def plot_computation_time_by_taskset_parameter(self, parameter):
        if parameter == "interference_factor":
            self.plot_computation_time_heatmap_interference(parameter)
        else:
            self.plot_computation_time_lineplot(parameter)

    def plot_computation_time_lineplot(self, parameter):
        plt.figure(figsize=(10, 6))
        ax = sns.lineplot(x=parameter, y="mean_computation_time_scheduling",
                          hue="assignment_scheduling_combination", data=self.df.dropna(subset=["mean_computation_time_scheduling"]), marker="o", errorbar=None, palette=self.algorithm_colors)
        plt.title(
            f"Computation Time by {parameter.replace('_', ' ').capitalize()}")
        plt.xlabel(parameter.replace("_", " ").capitalize())
        plt.ylabel("Computation Time (s)")
        plt.yscale("log")
        plt.legend(title="Scheduling/Assignment Combination",
                   bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.savefig(
            self.plots_dir / f'by_parameter_computation_time_with_parameter_{parameter}.png', bbox_inches='tight')
        plt.close()

    def plot_computation_time_heatmap_interference(self, parameter):
        plt.figure(figsize=(12, 8))
        vmin = self.min_computation_time if self.min_computation_time > 0 else 1e-6
        ax = sns.heatmap(self.df.dropna(subset=["mean_computation_time_scheduling"]).pivot_table(index=parameter, columns="probability_factor", values="mean_computation_time_scheduling", aggfunc='mean', dropna=True),
                         annot=True, cmap="viridis", fmt=".6f", norm=LogNorm(vmin=vmin, vmax=self.max_computation_time))
        plt.title(
            f"Computation Time by Interference Factor and Probability of Interference")
        plt.xlabel("Interference Factor")
        plt.ylabel("Probability of Interference")
        plt.gca().invert_yaxis()
        plt.savefig(
            self.plots_dir / f'by_parameter_computation_time_with_parameter_{parameter}.png')
        plt.close()

    def plot_overutilization_by_taskset_parameter(self, parameter):
        if parameter == "interference_factor":
            self.plot_overutilization_heatmap_interference(parameter)
        else:
            self.plot_overutilization_lineplot(parameter)

    def plot_overutilization_lineplot(self, parameter):
        plt.figure(figsize=(10, 6))
        ax = sns.lineplot(x=parameter, y="mean_overutilization", hue="assignment_scheduling_combination",
                          data=self.df.dropna(subset=["mean_overutilization"]), marker="o", errorbar=None, palette=self.algorithm_colors)
        plt.title(
            f"Overutilization by {parameter.replace('_', ' ').capitalize()}")
        plt.xlabel(parameter.replace("_", " ").capitalize())
        plt.ylabel("Overutilization (%)")
        plt.yscale("log")
        plt.legend(title="Scheduling/Assignment Combination",
                   bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.savefig(
            self.plots_dir / f'by_parameter_overutilization_with_{parameter}.png', bbox_inches='tight')
        plt.close()

    def plot_overutilization_heatmap_interference(self, parameter):
        plt.figure(figsize=(12, 8))
        vmin = self.min_computation_time if self.min_computation_time > 0 else 1e-6
        ax = sns.heatmap(self.df.dropna(subset=["mean_overutilization"]).pivot_table(index=parameter, columns="probability_factor", values="mean_overutilization", aggfunc='mean', dropna=True),
                         annot=True, cmap="viridis", fmt=".6f", norm=LogNorm(vmin=vmin, vmax=self.max_computation_time))
        plt.title(
            f"Overutilization by Interference Factor and Probability of Interference")
        plt.xlabel("Interference Factor")
        plt.ylabel("Probability of Interference")
        plt.gca().invert_yaxis()
        plt.savefig(
            self.plots_dir / f'by_parameter_overutilization_with_parameter_{parameter}.png')
        plt.close()

    def plot_success_rate_by_sorting_criteria(self, df_subset, sorting_criterion):
        plt.figure(figsize=(12, 8))
        assignment_without_wmin = [
            assignment for assignment in self.assignment_methods if assignment != "Wmin"]
        ax = sns.barplot(x="assignment_scheduling_combination", y="mean_success_scheduling", data=df_subset, order=[
                         f"{s}_{a}" for s in self.scheduling_algorithms for a in assignment_without_wmin], errorbar=None, palette=self.algorithm_colors, hue="assignment_scheduling_combination", legend=False)  # scheduling en premier
        ax.set_ylim(-0.01, 1.1)
        plt.title(
            f"Success Rate by Scheduling/Assignment, Sorting Criterion: {sorting_criterion.replace('_',' ').capitalize()}")
        plt.xlabel("Scheduling/Assignment Combination")
        plt.xticks(rotation=90, ha="right")
        plt.ylabel("Success Rate")
        self.autolabel_bars(ax)
        plt.tight_layout()
        plt.savefig(self.plots_dir /
                    f'by_sorting_criterion_success_rate_with_{sorting_criterion}.png')
        plt.close()

    def plot_computation_time_by_sorting_criteria(self, df_subset, sorting_criterion):
        plt.figure(figsize=(12, 8))
        assignment_without_wmin = [
            assignment for assignment in self.assignment_methods if assignment != "Wmin"]
        ax = sns.boxplot(x="assignment_scheduling_combination", y="mean_computation_time_scheduling", data=df_subset, order=[
                         f"{s}_{a}" for s in self.scheduling_algorithms for a in assignment_without_wmin], showfliers=False, palette=self.algorithm_colors, hue="assignment_scheduling_combination", legend=False)
        plt.title(
            f"Computation Time by Scheduling/Assignment, Sorting Criterion: {sorting_criterion.replace('_',' ').capitalize()}")
        plt.xlabel("Scheduling/Assignment Combination")
        plt.ylabel("Computation Time (s)")
        plt.xticks(rotation=90, ha="right")
        plt.yscale("log")
        plt.tight_layout()
        plt.savefig(self.plots_dir /
                    f'by_sorting_criterion_computation_time_with_{sorting_criterion}.png')
        plt.close()

    def autolabel_bars(self, ax):
        for p in ax.patches:
            height = p.get_height()
            ax.text(p.get_x() + p.get_width() / 2., height / 2, f"{height:.2f}",
                    ha="center", va="center", rotation=90, color='black')
