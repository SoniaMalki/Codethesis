import os
import matplotlib.pyplot as plt
import seaborn as sns


class AssignmentAnalyzer:
    def __init__(self, df, current_path):
        self.df = df
        self.assignment_methods = ["FirstFitAssigner", "BestFitAssigner",
                                   "WorstFitAssigner", "Wmin", "Citta"]
        self.sorting_criteria = ["wcet_ascending", "wcet_descending", "period_ascending", "period_descending",
                                 "utilization_ascending", "utilization_descending", "execution_slack_ascending", "execution_slack_descending", "random_order"]
        self.taskset_parameters = ["interference_factor", "max_utilization",
                                   "task_core_ratio", "tasks_per_taskset", "number_of_cores"]
        self.current_path = current_path
        self.plots_dir = self.current_path / "plots" / "assignment"
        os.makedirs(self.plots_dir, exist_ok=True)

        self.df["task_core_ratio"] = self.df["tasks_per_taskset"] / \
            self.df["number_of_cores"]

    def analyze(self):
        self.plot_global_success_rate()
        self.plot_global_computation_time()

        # Exclure Wmin des analyses par critère de tri
        df_subset = self.df[self.df["assignment_method"] != "Wmin"]
        self.plot_success_rate_by_sorting_criteria(df_subset)
        self.plot_computation_time_by_sorting_criteria(df_subset)

        for parameter in self.taskset_parameters:
            self.plot_success_rate_by_taskset_parameter(parameter)
            self.plot_computation_time_by_taskset_parameter(parameter)

    def plot_global_success_rate(self):
        plt.figure(figsize=(10, 6))
        ax = sns.barplot(x="assignment_method", y="mean_success_assignment",
                         data=self.df, order=self.assignment_methods)
        plt.title("Taux de succès global par algorithme d'assignation")
        plt.xlabel("Algorithme d'assignation")
        plt.ylabel("Taux de succès")
        self.autolabel_bars(ax)
        plt.savefig(self.plots_dir / 'global_success_rate.png')
        plt.close()

    def plot_global_computation_time(self):
        plt.figure(figsize=(10, 6))
        ax = sns.boxplot(x="assignment_method", y="mean_computation_time_assignment", data=self.df,
                         order=self.assignment_methods, showfliers=False)
        plt.title("Temps de calcul global par algorithme d'assignation")
        plt.xlabel("Algorithme d'assignation")
        plt.ylabel("Temps de calcul (s)")
        plt.yscale("log")
        plt.savefig(self.plots_dir / 'global_computation_time.png')
        plt.close()

    def plot_success_rate_by_sorting_criteria(self, df_subset):
        plt.figure(figsize=(12, 8))
        hue_order = [
            assignment_method for assignment_method in self.assignment_methods if assignment_method != "Wmin"]
        ax = sns.barplot(x="sorting_criterion", y="mean_success_assignment", hue="assignment_method", data=df_subset,
                         order=self.sorting_criteria, hue_order=hue_order)
        plt.title("Taux de succès en fonction du critère de tri")
        plt.xlabel("Critère de tri")
        plt.ylabel("Taux de succès")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        self.autolabel_bars(ax)
        plt.savefig(self.plots_dir / 'success_rate_by_sorting_criteria.png')
        plt.close()

    def plot_computation_time_by_sorting_criteria(self, df_subset):
        plt.figure(figsize=(12, 8))
        hue_order = [
            assignment_method for assignment_method in self.assignment_methods if assignment_method != "Wmin"]
        ax = sns.boxplot(x="sorting_criterion", y="mean_computation_time_assignment", hue="assignment_method", data=df_subset, order=self.sorting_criteria,
                         hue_order=hue_order, showfliers=False)
        plt.title("Temps de calcul en fonction du critère de tri")
        plt.xlabel("Critère de tri")
        plt.ylabel("Temps de calcul (s)")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.yscale("log")
        plt.savefig(self.plots_dir /
                    'computation_time_by_sorting_criteria.png')
        plt.close()

    def plot_success_rate_by_taskset_parameter(self, parameter):
        if parameter == "interference_factor":
            self.plot_success_rate_heatmap_interference(parameter)
        else:
            self.plot_success_rate_lineplot(parameter)

    def plot_success_rate_lineplot(self, parameter):
        plt.figure(figsize=(10, 6))
        ax = sns.lineplot(x=parameter, y="mean_success_assignment",
                          hue="assignment_method", data=self.df, marker="o", hue_order=self.assignment_methods)
        plt.title(
            f"Taux de succès en fonction de {parameter.replace('_', ' ').capitalize()}")
        plt.xlabel(parameter.replace("_", " ").capitalize())
        plt.ylabel("Taux de succès")
        plt.savefig(self.plots_dir / f'success_rate_by_{parameter}.png')
        plt.close()

    def plot_success_rate_heatmap_interference(self, parameter):
        for assignment_method in self.assignment_methods:
            df_subset = self.df[(self.df["assignment_method"] == assignment_method) & (
                self.df[parameter].notna())]
            if df_subset.empty:
                continue
            plt.figure(figsize=(12, 8))
            ax = sns.heatmap(df_subset.pivot_table(index=parameter, columns="probability_factor", values="mean_success_assignment"),
                             annot=True, cmap="coolwarm", fmt=".2f")
            plt.title(
                f"Taux de succès de {assignment_method} en fonction de {parameter.replace('_', ' ').capitalize()} et de la probabilité d'interférence")
            plt.xlabel(parameter.replace("_", " ").capitalize())
            plt.ylabel("Probabilité d'interférence")
            plt.gca().invert_yaxis()
            plt.savefig(
                self.plots_dir / f'{assignment_method}_success_rate_by_{parameter}_and_probability.png')
            plt.close()

    def plot_computation_time_by_taskset_parameter(self, parameter):
        if parameter == "interference_factor":
            self.plot_computation_time_heatmap_interference(parameter)
        else:
            self.plot_computation_time_lineplot(parameter)

    def plot_computation_time_lineplot(self, parameter):
        plt.figure(figsize=(10, 6))
        ax = sns.lineplot(x=parameter, y="mean_computation_time_assignment",
                          hue="assignment_method", data=self.df, marker="o", hue_order=self.assignment_methods)
        plt.title(
            f"Temps de calcul moyen en fonction de {parameter.replace('_', ' ').capitalize()}")
        plt.xlabel(parameter.replace("_", " ").capitalize())
        plt.ylabel("Temps de calcul moyen (s)")
        plt.savefig(self.plots_dir / f'computation_time_by_{parameter}.png')
        plt.close()

    def plot_computation_time_heatmap_interference(self, parameter):
        for assignment_method in self.assignment_methods:
            df_subset = self.df[(self.df["assignment_method"] == assignment_method) & (
                self.df[parameter].notna())]
            if df_subset.empty:
                continue
            plt.figure(figsize=(12, 8))
            ax = sns.heatmap(df_subset.pivot_table(index=parameter, columns="probability_factor", values="mean_computation_time_assignment"),
                             annot=True, cmap="coolwarm", fmt=".2f")
            plt.title(
                f"Temps de calcul moyen de {assignment_method} en fonction de {parameter.replace('_', ' ').capitalize()} et de la probabilité d'interférence")
            plt.xlabel(parameter.replace("_", " ").capitalize())
            plt.ylabel("Probabilité d'interférence")
            plt.gca().invert_yaxis()
            plt.savefig(
                self.plots_dir / f'{assignment_method}_computation_time_by_{parameter}_and_probability.png')
            plt.close()

    def autolabel_bars(self, ax):
        for p in ax.patches:
            height = p.get_height()
            ax.text(
                p.get_x() + p.get_width() / 2.,
                height / 2,
                f"{height:.2f}",
                ha="center",
                va="center",
                rotation=90,
                color='black'
            )
