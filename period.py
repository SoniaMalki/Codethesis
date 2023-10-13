import random
import math
from time import sleep

def generate_random_distribution(lst, criterion, num_samples):
    if criterion == "small":
        probabilities = [1 / (math.sqrt(i + 1)) for i in range(len(lst))]  # Higher chance for smaller numbers
    elif criterion == "average":
        center_index = len(lst) // 2
        probabilities = [1 / (math.sqrt(abs(i - center_index) + 1)) for i in range(len(lst))]  # Higher chance for the middle number
    elif criterion == "high":
        probabilities = [1 / (math.sqrt(len(lst) - i)) for i in range(len(lst))]  # Higher chance for larger numbers
    else:
        raise ValueError("Invalid criterion")

    sum_probabilities = sum(probabilities)
    normalized_probabilities = [p / sum_probabilities for p in probabilities]

    random_samples = random.choices(lst, normalized_probabilities, k=num_samples)
    random_samples.sort()  
    return random_samples



def calculate_distribution(prime, max_exponent, criteria, limite, num_columns):
    res = []
    lst = [nb for nb in range(0, max_exponent+1)]
    exponent_distribution = generate_random_distribution(lst, criteria, num_columns)
    for exponent in exponent_distribution:
        res.extend([prime ** exponent ])


    
    return res

def generate_M(primes, max_exponent, criteria, limite, num_columns):
    M = []
    for prime in primes:
        distribution = calculate_distribution(prime, max_exponent, criteria, limite, num_columns)
        M.append(distribution)
    return M


def algorithm_1(M):
    period = 1
    for i in M:
        p = round(random.uniform(1, len(i)))
        period *= i[p-1]  # -1 because list index starts from 0
    return period

# Define the primes, maximum exponent, and criteria based on the example provided
primes = [2, 3, 5, 7]
max_exponent = 2
num_columns = 10
limite = 100
criterion = "small"
# Generate the matrix M
M = generate_M(primes, max_exponent, criterion, limite, num_columns)

# Print the matrix M
for row in M:
    print(row)
periods = []
avg = 1
for i in range(10):
    period = algorithm_1(M)
    periods.append(period)
print(periods)

low = math.lcm(*periods)
print("llcm", low)