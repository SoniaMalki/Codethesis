from sympy import primerange
import random

class MatrixM:
    def __init__(self, hyperperiod_limit=100000, max_prime=20, generation_limit_exponent=2):
        self.hyperperiod_limit = hyperperiod_limit
        self.max_prime = max_prime
        self.generation_limit = hyperperiod_limit**generation_limit_exponent
        self.matrix = []
        self.generate_matrix()
        self.hyperperiod = self.hyperperiod()


    def hyperperiod(self, matrix=None):
        if matrix is None:
            matrix = self.matrix
        max_values = [max(row) for row in matrix if row]
        result = 1
        for value in max_values:
            result *= value
        return result

    def generate_matrix(self):
        self.matrix = self.generate_matrix_before_pruning()
        self.matrix = self.prune_matrix()
        self.matrix = self.duplicate_elements(max_length=20, max_duplicates=6)

    def generate_matrix_before_pruning(self):
        primes = list(primerange(2, self.max_prime))
        matrix = []

        for i, prime in enumerate(primes):
            new_row = [prime ** 0]  # Commencer avec [1]
            matrix.append(new_row)
            
            for j in range(len(matrix)):
                exponent = len(matrix[j])
                matrix[j].append(primes[j] ** exponent)
                
                if self.hyperperiod(matrix) > self.generation_limit:
                    return matrix
        return matrix

    def prune_matrix(self):
        while self.hyperperiod() > self.hyperperiod_limit:
            max_values = [(max(row), idx) for idx, row in enumerate(self.matrix) if row]
            max_values.sort(reverse=True)
            
            max_val, max_idx = max_values[0]
            self.matrix[max_idx].pop()
            
            if self.hyperperiod() <= self.hyperperiod_limit:
                break

        self.matrix = [row for row in self.matrix if not (len(row) == 1 and row[0] == 1)]
        return self.matrix

    def display_matrix_with_len_hyperperiod(self, message):
        print(message)
        for row in self.matrix:
            print(row, " | Len row: " ,len(row))
        print("Hyperperiode:", self.hyperperiod)

    def duplicate_elements(self, max_length, max_duplicates):
        for row in self.matrix:
            num_duplicates = random.randint(1, max_length // 2)
            for _ in range(num_duplicates):
                value_to_duplicate = random.choice(row)
                num_copies = random.randint(1, max_duplicates)
                for _ in range(num_copies):
                    row.insert(random.randint(0, len(row)), value_to_duplicate)
            row.sort()
        return self.matrix

# Exemple d'utilisation
if __name__ == "__main__":
    matrix_obj = MatrixM()
    matrix_obj.display_matrix_with_len_hyperperiod("Final matrix:")
