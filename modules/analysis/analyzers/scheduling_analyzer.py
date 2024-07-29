import os
import matplotlib.pyplot as plt
import seaborn as sns


class SchedulingAnalyzer:
    def __init__(self, df, current_path):
        self.df = df
        self.scheduling_algorithms = ["EarliestDeadlineFirst", "EarliestDeadlineFirstVariant1", "EarliestDeadlineFirstVariant2",
                                      "DeadlineMonotonic", "DeadlineMonotonicVariant1", "DeadlineMonotonicVariant2", "CombinedScheduler", "Rhma"]
        self.non_preemptive_options = [
            "number_of_tasks", "wcet_of_tasks", "system_utilization"]
        self.taskset_parameters = ["interference_factor",
                                   "max_utilization", "task_core_ratio"]
        self.current_path = current_path
        self.plots_dir = self.current_path / "plots" / "scheduling"
        os.makedirs(self.plots_dir, exist_ok=True)

        self.df["non_preemption_option"] = self.df["scheduling_options"].apply(
            lambda x: x.get("non_preemption_time_variant2") if isinstance(
                x, dict) else None
        )

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

    def plot_global_success_rate(self):
        plt.figure(figsize=(10, 6))
        sns.barplot(x="scheduling_algorithm",
                    y="mean_success_scheduling", data=self.df)
        plt.title("Taux de succès global par algorithme de scheduling")
        plt.xlabel("Algorithme de scheduling")
        plt.ylabel("Taux de succès")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(self.plots_dir / 'global_success_rate.png')
        plt.close()

    def plot_global_computation_time(self):
        plt.figure(figsize=(10, 6))
        sns.boxplot(x="scheduling_algorithm",
                    y="mean_computation_time_scheduling", data=self.df)
        plt.title("Temps de calcul global par algorithme de scheduling")
        plt.xlabel("Algorithme de scheduling")
        plt.ylabel("Temps de calcul (s)")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(self.plots_dir / 'global_computation_time.png')
        plt.close()

    def plot_global_overutilization(self):
        plt.figure(figsize=(10, 6))
        sns.boxplot(x="scheduling_algorithm",
                    y="mean_overutilization", data=self.df)
        plt.title(
            "Augmentation d'utilisation globale par algorithme de scheduling")
        plt.xlabel("Algorithme de scheduling")
        plt.ylabel("Augmentation d'utilisation (%)")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(self.plots_dir / 'global_overutilization.png')
        plt.close()

    def plot_success_rate_by_non_preemptive_option(self, df_subset):
        plt.figure(figsize=(12, 8))
        sns.barplot(x="non_preemption_option",
                    y="mean_success_scheduling", hue="scheduling_algorithm", data=df_subset)
        plt.title(
            "Taux de succès en fonction de non_preemptive_time_variant_2")
        plt.xlabel("non_preemption_time_variant_2")
        plt.ylabel("Taux de succès")
        plt.savefig(
            self.plots_dir / 'success_rate_by_non_preemptive_option.png')
        plt.close()

    def plot_computation_time_by_non_preemptive_option(self, df_subset):
        plt.figure(figsize=(12, 8))
        sns.boxplot(x="non_preemption_option",
                    y="mean_computation_time_scheduling", hue="scheduling_algorithm", data=df_subset)
        plt.title(
            "Temps de calcul moyen en fonction de non_preemptive_time_variant_2")
        plt.xlabel("non_preemption_time_variant_2")
        plt.ylabel("Temps de calcul (s)")
        plt.savefig(
            self.plots_dir / 'computation_time_by_non_preemptive_option.png')
        plt.close()

    def plot_overutilization_by_non_preemptive_option(self, df_subset):
        plt.figure(figsize=(12, 8))
        sns.boxplot(x="non_preemption_option",
                    y="mean_overutilization", hue="scheduling_algorithm", data=df_subset)
        plt.title(
            "Augmentation d'utilisation moyenne en fonction de non_preemptive_time_variant_2")
        plt.xlabel("non_preemption_time_variant_2")
        plt.ylabel("Augmentation d'utilisation (%)")
        plt.savefig(
            self.plots_dir / 'overutilization_by_non_preemptive_option.png')
        plt.close()
