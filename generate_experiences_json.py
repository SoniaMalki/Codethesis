import json
import itertools

def generate_experiences():
    experiences = {}

    # Paramètres de Taskset
    taskset_repetitions = [1] #, 2, 4, 8, 16]
    tasks_per_taskset = [10] #, 20]
    interference_factors = [0.2] #, 0.8]
    probability_factors = [0.1] #, 0.4]
    max_utilization_factors = [0.2] #, 0.4, 0.6, 0.8, 1.0] # Facteurs d'utilisation
    deadline_options = ["eq_period"] #, "leq_period"]
    max_hyperperiods = [10] #, 100, 1000]
    max_primes = [2] #, 3, 5, 7, 11, 13, 17, 19, 23]
    gen_limit_exponents = [2] #, 3, 4, 5]

    # Paramètres d'Assignment
    assignment_methods = ["CITTA"] #, "WorstFitAssigner", "FirstFitAssigner", "BestFitAssigner", "Wmin"]
    sorting_criteria = ["wcet_ascending"] #, "wcet_descending", "period_ascending",
                       #"period_descending", "utilization_ascending", "utilization_descending", 
                       #"execution_slack_ascending", "execution_slack_descending", "random_order"]
    number_of_cores_list = [2] #, 4, 8]
    solving_time_limit_milp_assignment = [2] #, 5, 10] 

    # Paramètres de Scheduling
    scheduling_algorithms = ["EarliestDeadlineFirst"] #, "EarliestDeadlineFirstVariant1", "EarliestDeadlineFirstVariant2",
                             #"DeadlineMonotonic", "DeadlineMonotonicVariant1", "DeadlineMonotonicVariant2", 
                             #"CombinedScheduler", "Rhma"]
    non_preemption_time_variant2_options = ["number_of_tasks"] #, "wcet_of_tasks", "system_utilization"]
    solving_time_limit_milp_scheduling = [1] #, 2, 5]  

    # Générer les combinaisons de paramètres pour Taskset
    taskset_index = 1
    for repetition, tasks, interference, probability, util_factor, deadline, hyperperiod, prime, exponent in itertools.product(
        taskset_repetitions, tasks_per_taskset, interference_factors, probability_factors, max_utilization_factors,
        deadline_options, max_hyperperiods, max_primes, gen_limit_exponents
    ):
        for cores in number_of_cores_list:  # Boucle sur les nombres de cœurs
            taskset_id = f"taskset_generate_{taskset_index}_c{cores}"
            experiences[taskset_id] = {
                "taskset": {
                    "action": "generate",
                    "taskset_id": taskset_id,
                    "parameters": {
                        "taskset_repetition": repetition,
                        "tasks_per_taskset": tasks,
                        "interference_factor": interference,
                        "probability_factor": probability,
                        "max_utilization": util_factor * cores,  # Utilisation liée au nombre de cœurs
                        "taskset_options": {
                            "deadline_option": deadline,
                            "max_hyperperiod": hyperperiod,
                            "max_prime": prime,
                            "gen_limit_exponent": exponent
                        }
                    }
                },
                "assignment": {
                    "action": "none"
                },
                "scheduling": {
                    "action": "none"
                }
            }
            taskset_index += 1

    # Ouvrir chaque taskset et générer les combinaisons de paramètres pour Assignment
    assignment_index = 1
    # Correction : Itérer sur une copie des clés du dictionnaire
    for taskset_key in list(experiences.keys()):  
        for method, sorting, cores, solving_time in itertools.product(
            assignment_methods, sorting_criteria, number_of_cores_list, solving_time_limit_milp_assignment
        ):
            if cores == int(taskset_key.split('_c')[1]): # Vérification du nombre de cœurs
                assignment_id = f"assignment_generate_{assignment_index}_c{cores}"
                experiences[assignment_id] = {
                    "taskset": {
                        "action": "open",
                        "taskset_id": taskset_key
                    },
                    "assignment": {
                        "action": "generate",
                        "assignment_id": assignment_id,
                        "taskset_id": taskset_key,
                        "parameters": {
                            "sorting_criterion": sorting,
                            "assignment_method": method,
                            "number_of_cores": cores,
                            "assignment_options": {
                                "solving_time_limit_MILP": solving_time
                            }
                        }
                    },
                    "scheduling": {
                        "action": "none"
                    }
                }
                assignment_index += 1

    # Ouvrir chaque assignment et générer les combinaisons de paramètres pour Scheduling
    scheduling_index = 1
    # Correction : Itérer sur une copie des clés du dictionnaire
    for assignment_key in list(experiences.keys())[(len(experiences) // 2) + 1:]:  
        for algorithm, non_preemption, solving_time in itertools.product(
            scheduling_algorithms, non_preemption_time_variant2_options, solving_time_limit_milp_scheduling
        ):
            scheduling_id = f"scheduling_generate_{scheduling_index}_c{experiences[assignment_key]['assignment']['number_of_cores']}"
            experiences[scheduling_id] = {
                "taskset": {
                    "action": "open",
                    "taskset_id": experiences[assignment_key]["assignment"]["taskset_id"]
                },
                "assignment": {
                    "action": "open",
                    "assignment_id": assignment_key,
                    "taskset_id": experiences[assignment_key]["assignment"]["taskset_id"]
                },
                "scheduling": {
                    "action": "generate",
                    "scheduling_id": scheduling_id,
                    "taskset_id": experiences[assignment_key]["assignment"]["taskset_id"],
                    "assignment_id": assignment_key,
                    "parameters": {
                        "scheduling_algorithm": algorithm,
                        "scheduling_options": {
                            "non_preemption_time_variant2": non_preemption,
                            "solving_time_limit_MILP": solving_time
                        }
                    }
                }
            }
            scheduling_index += 1

    return experiences

# Générer le fichier experiences.json
experiences = generate_experiences()
with open("./config_files/experiences.json", "w") as f:
    json.dump(experiences, f, indent=4)