import matplotlib.pyplot as plt
import seaborn as sns


class CittaAnalyzer:
    def __init__(self, df):
        self.df = df
        self.df_citta = self.df[self.df["assignment_method"] == "Citta"]

    def analyze_acceptance_ratio(self):
        citta_acceptance_rate = self.calculate_citta_acceptance_rate()
        self.plot_citta_acceptance_rate(citta_acceptance_rate)

    def calculate_citta_acceptance_rate(self):
        pass  # TODO

    def plot_citta_acceptance_rate(self, citta_acceptance_rate):
        pass  # TODO

    def analyze_prediction_accuracy(self):
        pass  # TODO

    def calculate_citta_prediction_accuracy(self):
        pass  # TODO

    def calculate_citta_false_negative_rate(self):
        pass  # TODO

    def calculate_citta_false_positive_rate(self):
        pass  # TODO

    def plot_citta_prediction_accuracy(self, citta_prediction_accuracy):
        pass  # TODO
