from sympy import primerange
import random
import os
import pickle
from pathlib import Path


class PrimeMatrixLoaderSaver:
    def __init__(self, main_path):
        self.matrix_path = main_path / "results" / "prime_matrices"

    def get_matrix_filename(self, max_hyperperiod, max_prime, gen_limit_exponent):
        return f"prime_matrix_{max_hyperperiod}_{max_prime}_{gen_limit_exponent}.pkl"

    def load(self, max_hyperperiod, max_prime, gen_limit_exponent):
        matrix_filename = self.get_matrix_filename(
            max_hyperperiod, max_prime, gen_limit_exponent)
        with open(self.matrix_path / matrix_filename, 'rb') as f:
            prime_matrix = pickle.load(f)
        return prime_matrix

    def save(self, prime_matrix, max_hyperperiod, max_prime, gen_limit_exponent):
        os.makedirs(self.matrix_path, exist_ok=True)
        matrix_filename = self.get_matrix_filename(
            max_hyperperiod, max_prime, gen_limit_exponent)
        with open(self.matrix_path / matrix_filename, 'wb') as f:
            pickle.dump(prime_matrix, f)
