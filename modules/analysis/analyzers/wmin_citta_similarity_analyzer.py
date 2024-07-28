import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


class WminCittaSimilarityAnalyzer:
    def __init__(self, df):
        self.df = df

    def analyze(self):
        similarity_rates = self.calculate_wmin_citta_similarity()
        self.plot_wmin_citta_similarity(similarity_rates)

    def calculate_wmin_citta_similarity(self):
        similarity_rates = {}
        for sorting_criterion in self.df["sorting_criterion"].unique():
            similarity_rates[sorting_criterion] = {}
            for interference_factor in self.df["interference_factor"].unique():
                df_wmin = self.df[(self.df["assignment_method"] == "Wmin") & (
                    self.df["interference_factor"] == interference_factor)]
                df_citta = self.df[(self.df["assignment_method"] == "Citta") & (self.df["sorting_criterion"] == sorting_criterion) & (
                    self.df["interference_factor"] == interference_factor)]

                if len(df_wmin) != len(df_citta):
                    print(
                        f"Attention : Nombre de lignes différent pour Wmin ({len(df_wmin)}) et Citta ({len(df_citta)}) avec le critère de tri {sorting_criterion} et le facteur d'interférence {interference_factor}"
                    )
                    continue
                common_allocations = 0
                for i in range(len(df_wmin)):
                    if np.array_equal(df_wmin["assignment_list"].iloc[i], df_citta["assignment_list"].iloc[i]):
                        common_allocations += 1
                similarity_rates[sorting_criterion][
                    interference_factor
                ] = common_allocations / len(df_wmin)
        return similarity_rates

    def plot_wmin_citta_similarity(self, similarity_rates):
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
