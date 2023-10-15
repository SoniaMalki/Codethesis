from modules.experience import Experience
from modules.taskset_set_generation import TasksetSetGeneration
import math
import random

class MatrixGeneration:
	def __init__(self, _primes, _max_exponent, _criteria, _limite, _num_columns):
		#parameters that stay the same
		self.primes = _primes
		self.max_exponent = _max_exponent
		self.criteria = _criteria
		self.limite = _limite
		self.num_columns = _num_columns


	def __repr__(self):
		return ("MatrixGeneration("
			f"_primes={self.primes}, "
			f"_max_exponent={self.max_exponent}, "
			f"_criteria={self.criteria}, "
			f"_limite={self.limite}, "
			f"_num_columns={self.num_columns}"
		")"
		)


	def generate_random_distribution(self, lst):
		if self.criteria == "small":
			probabilities = [1 / (math.sqrt(i + 1)) for i in range(len(lst))]  # Higher chance for smaller numbers
		elif self.criteria == "average":
			center_index = len(lst) // 2
			probabilities = [1 / (math.sqrt(abs(i - center_index) + 1)) for i in range(len(lst))]  # Higher chance for the middle number
		elif self.criteria == "high":
			probabilities = [1 / (math.sqrt(len(lst) - i)) for i in range(len(lst))]  # Higher chance for larger numbers
		else:
			raise ValueError("Invalid criterion")

		sum_probabilities = sum(probabilities)
		normalized_probabilities = [p / sum_probabilities for p in probabilities]

		random_samples = random.choices(lst, normalized_probabilities, k= self.num_columns)
		random_samples.sort()  
		return random_samples


	def calculate_distribution(self, prime):
		res = []
		lst = [nb for nb in range(0, self.max_exponent+1)]
		exponent_distribution = self.generate_random_distribution(lst)
		for exponent in exponent_distribution:
			res.extend([prime ** exponent ])
		
		return res


	def try_generate_matrix(self):
		M = []
		for prime in self.primes:
			distribution = self.calculate_distribution(prime)
			M.append(distribution)
		return M


	def generate_matrix(self):

		valid = False

		while not valid:
			print("----------")
			M = self.try_generate_matrix()
			print(M)
			max_matrixes = []
			for i in M:
				max_n = max(i)
				max_matrixes.append(max_n)
			print(max_matrixes)
			print(math.lcm(*max_matrixes))
			if math.lcm(*max_matrixes) <= self.limite:
				valid = True

		return M


