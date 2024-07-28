import matplotlib.pyplot as plt
import seaborn as sns


class OverutilizationAnalyzer:
    def __init__(self, df):
        self.df = df

    def analyze(self):
        self.plot_mean_overutilization_heatmap()
        self.plot_mean_overutilization_by_utilization()

    def calculate_mean_overutilization(self):
        return self.df.groupby(["assignment_method", "scheduling_algorithm"])["mean_overutilization"].mean()

    def plot_mean_overutilization_heatmap(self):
        mean_overutilization = self.calculate_mean_overutilization()
        plt.figure(figsize=(12, 8))
        sns.heatmap(mean_overutilization.unstack(),
                    annot=True, cmap="coolwarm", fmt=".2f")
        plt.title("Mean overutilization by allocator/scheduler combination")
        plt.xlabel("Scheduler")
        plt.ylabel("Allocator")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()

    def plot_mean_overutilization_by_utilization(self):
        plt.figure(figsize=(10, 6))
        sns.lineplot(x="max_utilization", y="mean_overutilization",
                     hue="scheduling_algorithm", data=self.df, marker="o")
        plt.title("Mean overutilization by utilization")
        plt.xlabel("Utilization")
        plt.ylabel("Mean overutilization")
        plt.show()
