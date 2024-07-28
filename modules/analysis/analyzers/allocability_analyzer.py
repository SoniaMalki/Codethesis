import matplotlib.pyplot as plt
import seaborn as sns


class AllocabilityAnalyzer:
    def __init__(self, df):
        self.df = df

    def analyze(self):
        self.plot_assignability_rate_by_interference_factor()
        self.plot_assignability_rate_by_utilization_and_cores()
        self.plot_wmin_citta_similarity_by_interference_factor()
        self.plot_assignability_and_computation_time()
        self.plot_assignability_by_taskset_parameters()

    def calculate_assignability_rates(self):
        return self.df.groupby("assignment_method")["mean_success_assignment"].mean()

    def calculate_mean_computation_time(self):
        return self.df.groupby("assignment_method")["mean_computation_time_assignment"].mean()

    def plot_assignability_rates(self, assignability_rates):
        plt.figure(figsize=(10, 6))
        sns.barplot(x=assignability_rates.index, y=assignability_rates.values)
        plt.title("Mean assignability/assignment method")
        plt.xlabel("Assignment Method")
        plt.ylabel("Assignability")
        plt.show()

    def plot_mean_computation_time(self, mean_computation_time):
        plt.figure(figsize=(10, 6))
        sns.barplot(x=mean_computation_time.index,
                    y=mean_computation_time.values)
        plt.title("Mean assignation time")
        plt.xlabel("Assignment Method")
        plt.ylabel("Mean assignation time (s)")
        plt.show()

    def plot_assignability_rate_by_interference_factor(self):
        print(self.df.columns)
        plt.figure(figsize=(10, 6))
        sns.lineplot(x="interference_factor", y="mean_success_assignment",
                     hue="assignment_method", data=self.df, marker="o")
        plt.title("Taux d'allocabilité en fonction du facteur d'interférence")
        plt.xlabel("Facteur d'interférence")
        plt.ylabel("Taux d'allocabilité")
        plt.show()

    def plot_assignability_rate_by_utilization_and_cores(self):
        for assignment_method in self.df["assignment_method"].unique():
            df_subset = self.df[self.df["assignment_method"]
                                == assignment_method]
            plt.figure(figsize=(12, 8))
            sns.heatmap(df_subset.pivot_table(index="number_of_cores", columns="max_utilization",
                        values="mean_success_assignment"), annot=True, cmap="coolwarm", fmt=".2f")
            plt.title(
                f"Taux d'allocabilité pour {assignment_method} (Utilisation x Nombre de cœurs)")
            plt.xlabel("Utilisation maximale")
            plt.ylabel("Nombre de cœurs")
            plt.show()

    def plot_wmin_citta_similarity_by_interference_factor(self):
        similarity_rates = self.calculate_wmin_citta_similarity()
        plt.figure(figsize=(10, 6))
        for sorting_criterion, rates in similarity_rates.items():
            plt.plot(rates.keys(), rates.values(),
                     marker="o", label=sorting_criterion)
        plt.title(
            "Taux de similarité Wmin/CITTA en fonction du facteur d'interférence")
        plt.xlabel("Facteur d'interférence")
        plt.ylabel("Taux de similarité")
        plt.legend()
        plt.show()

    def calculate_wmin_citta_similarity(self):
        similarity_rates = {}
        for sorting_criterion in self.df["sorting_criterion"].unique():
            similarity_rates[sorting_criterion] = {}
            for interference_factor in self.df["interference_factor"].unique():
                df_wmin = self.df[(self.df["assignment_method"] == "Wmin") & (
                    self.df["interference_factor"] == interference_factor)]
                df_citta = self.df[(self.df["assignment_method"] == "Citta") & (
                    self.df["sorting_criterion"] == sorting_criterion) & (self.df["interference_factor"] == interference_factor)]

                if len(df_wmin) != len(df_citta):
                    print(
                        f"Attention : Nombre de lignes différent pour Wmin ({len(df_wmin)}) et Citta ({len(df_citta)}) avec le critère de tri {sorting_criterion} et le facteur d'interférence {interference_factor}")
                    continue

                common_allocations = 0
                for i in range(len(df_wmin)):
                    if df_wmin["assignment_list"].iloc[i] == df_citta["assignment_list"].iloc[i]:
                        common_allocations += 1
                similarity_rates[sorting_criterion][interference_factor] = common_allocations / len(
                    df_wmin)
        return similarity_rates

    def plot_assignability_and_computation_time(self):
        assignability_rates = self.calculate_assignability_rates()
        mean_computation_time = self.calculate_mean_computation_time()

        fig, ax1 = plt.subplots(figsize=(10, 6))

        ax1.bar(assignability_rates.index, assignability_rates.values,
                color="tab:blue", label="Taux d'allocabilité")
        ax1.set_xlabel("Allocateur")
        ax1.set_ylabel("Taux d'allocabilité", color="tab:blue")
        ax1.tick_params(axis="y", labelcolor="tab:blue")

        ax2 = ax1.twinx()
        ax2.bar(mean_computation_time.index, mean_computation_time.values,
                color="tab:orange", label="Temps de calcul moyen")
        ax2.set_ylabel("Temps de calcul moyen (s)", color="tab:orange")
        ax2.tick_params(axis="y", labelcolor="tab:orange")

        plt.title("Taux d'allocabilité et temps de calcul moyen par allocateur")
        fig.tight_layout()
        plt.show()

    def plot_assignability_by_taskset_parameters(self):
        parameters = ["tasks_per_taskset",
                      "max_hyperperiod", "deadline_option"]
        for parameter in parameters:
            plt.figure(figsize=(10, 6))
            sns.barplot(x=parameter, y="mean_success_assignment",
                        hue="assignment_method", data=self.df)
            plt.title(f"Taux d'allocabilité en fonction de {parameter}")
            plt.xlabel(parameter.replace("_", " ").capitalize())
            plt.ylabel("Taux d'allocabilité")
            plt.show()
