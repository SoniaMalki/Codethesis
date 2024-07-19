
from sympy import primerange
import random
from pathlib import Path

from modules.taskset.task_parameters_generator.prime_matrix_loader_saver import PrimeMatrixLoaderSaver


class PrimeMatrixGenerator:
    def __init__(self, main_path, max_hyperperiod, max_prime, gen_limit_exponent):
        self.main_path = main_path
        self.loader_saver = PrimeMatrixLoaderSaver(main_path)
        self.max_hyperperiod = max_hyperperiod
        self.max_prime = max_prime
        self.generation_limit = max_hyperperiod**gen_limit_exponent
        self.prime_matrix = self.load_or_generate_matrix()
        self.calculate_hyperperiod = self.calculate_hyperperiod()

    def load_or_generate_matrix(self):
        try:
            return self.loader_saver.load(self.max_hyperperiod, self.max_prime, self.generation_limit)
        except FileNotFoundError:
            prime_matrix = self.generate_matrix()
            self.loader_saver.save(
                prime_matrix, self.max_hyperperiod, self.max_prime, self.generation_limit)
            return prime_matrix

    def calculate_hyperperiod(self, matrix=None):
        if matrix is None:
            matrix = self.prime_matrix
        max_values = [max(row) for row in matrix if row]
        result = 1
        for value in max_values:
            result *= value
        return result

    def generate_matrix(self):
        self.prime_matrix = self.generate_initial_matrix()
        self.prime_matrix = self.prune_matrix()
        self.prime_matrix = self.add_duplicates_to_matrix(
            max_length=20, max_duplicates=6)
        return self.prime_matrix

    def generate_initial_matrix(self):
        primes = list(primerange(2, self.max_prime))
        prime_matrix = []

        for i, prime in enumerate(primes):
            row = [prime ** 0]  # Start with [1]
            prime_matrix.append(row)

            for j in range(len(prime_matrix)):
                exponent = len(prime_matrix[j])
                prime_matrix[j].append(primes[j] ** exponent)

                if self.calculate_hyperperiod(prime_matrix) > self.generation_limit:
                    return prime_matrix
        return prime_matrix

    def prune_matrix(self):
        while self.calculate_hyperperiod() > self.max_hyperperiod:
            max_values = [(max(row), idx)
                          for idx, row in enumerate(self.prime_matrix) if row]
            max_values.sort(reverse=True)

            max_val, max_index = max_values[0]
            self.prime_matrix[max_index].pop()

            if self.calculate_hyperperiod() <= self.max_hyperperiod:
                break

        self.prime_matrix = [row for row in self.prime_matrix if not (
            len(row) == 1 and row[0] == 1)]
        return self.prime_matrix

    def display_matrix_details(self, header_message):
        print(header_message)
        for row in self.prime_matrix:
            print(row, " | Len row: ", len(row))
        print("Hyperperiode:", self.calculate_hyperperiod)

    def add_duplicates_to_matrix(self, max_length, max_duplicates):
        for row in self.prime_matrix:
            num_duplicates = random.randint(1, max_length // 2)
            for _ in range(num_duplicates):
                value_to_duplicate = random.choice(row)
                num_copies = random.randint(1, max_duplicates)
                for _ in range(num_copies):
                    row.insert(random.randint(0, len(row)), value_to_duplicate)
            row.sort()
        return self.prime_matrix


# Example usage
if __name__ == "__main__":
    matrix_obj = PrimeMatrixGenerator(main_path=Path("."))
    matrix_obj.display_matrix_details("Final matrix:")
