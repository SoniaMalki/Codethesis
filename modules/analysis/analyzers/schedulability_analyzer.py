import matplotlib.pyplot as plt
import seaborn as sns


class SchedulabilityAnalyzer:
    def __init__(self, df):
        self.df = df

    def analyze(self):
        self.plot_schedulability_rate_by_scheduler()
        self.plot_schedulability_rate_by_combination()
        self.plot_schedulability_rate_by_utilization()
        self.plot_computation_time_by_scheduler()
        self.plot_computation_time_by_combination()

    def calculate_schedulability_rates(self):
        return self.df.groupby("scheduling_algorithm")["mean_success_scheduling"].mean()

    def calculate_schedulability_rates_by_combination(self):
        return self.df.groupby(["assignment_method", "scheduling_algorithm"])["mean_success_scheduling"].mean()

    def calculate_mean_computation_time(self):
        return self.df.groupby("scheduling_algorithm")["mean_computation_time_scheduling"].mean()

    def calculate_mean_computation_time_by_combination(self):
        return self.df.groupby(["assignment_method", "scheduling_algorithm"])["mean_computation_time_scheduling"].mean()

    def plot_schedulability_rate_by_scheduler(self):
        schedulability_rates = self.calculate_schedulability_rates()
        plt.figure(figsize=(10, 6))
        sns.barplot(x=schedulability_rates.index,
                    y=schedulability_rates.values)
        plt.title("Mean schedulability rate by scheduler")
        plt.xlabel("Scheduler")
        plt.ylabel("Schedulability rate")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()

    def plot_schedulability_rate_by_combination(self):
        schedulability_rates_by_combination = self.calculate_schedulability_rates_by_combination()
        plt.figure(figsize=(12, 8))
        sns.heatmap(schedulability_rates_by_combination.unstack(),
                    annot=True, cmap="coolwarm", fmt=".2f")
        plt.title("Mean schedulability rate by allocator/scheduler combination")
        plt.xlabel("Scheduler")
        plt.ylabel("Allocator")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()

    def plot_schedulability_rate_by_utilization(self):
        plt.figure(figsize=(10, 6))
        sns.lineplot(x="max_utilization", y="mean_success_scheduling",
                     hue="scheduling_algorithm", data=self.df, marker="o")
        plt.title("Schedulability rate by utilization")
        plt.xlabel("Utilization")
        plt.ylabel("Schedulability rate")
        plt.show()

    def plot_computation_time_by_scheduler(self):
        mean_computation_time = self.calculate_mean_computation_time()
        plt.figure(figsize=(10, 6))
        sns.barplot(x=mean_computation_time.index,
                    y=mean_computation_time.values)
        plt.title("Mean computation time by scheduler")
        plt.xlabel("Scheduler")
        plt.ylabel("Computation time (s)")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()

    def plot_computation_time_by_combination(self):
        mean_computation_time_by_combination = self.calculate_mean_computation_time_by_combination()
        plt.figure(figsize=(12, 8))
        sns.heatmap(mean_computation_time_by_combination.unstack(),
                    annot=True, cmap="coolwarm", fmt=".2f")
        plt.title("Mean computation time by allocator/scheduler combination")
        plt.xlabel("Scheduler")
        plt.ylabel("Allocator")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()
