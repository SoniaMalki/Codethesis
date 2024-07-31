import json
import itertools
from pathlib import Path


class ConfigGenerator:
    def __init__(self, config_dir):
        self.config_dir = Path(config_dir) / "config_files"
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def generate_tasksets(self):
        tasksets = {}

        taskset_repetitions = [1]
        tasks_per_taskset = [10]
        interference_factors = [0.2]
        probability_factors = [0.4]
        max_utilization_factors = [0.3]
        deadline_options = ["eq_period"]
        prime_exponent_hyperperiod_combinations = [
            (10000, 7, 3)
        ]
        number_of_cores_list = [8]

        taskset_index = 1
        for repetition, tasks, interference, probability, util_factor, deadline, (hyperperiod, prime, exponent) in itertools.product(
            taskset_repetitions, tasks_per_taskset, interference_factors, probability_factors, max_utilization_factors,
            deadline_options, prime_exponent_hyperperiod_combinations
        ):
            for cores in number_of_cores_list:
                taskset_id = f"taskset_generate_{taskset_index}_c{cores}"
                tasksets[taskset_id] = {
                    "taskset": {
                        "action": "generate",
                        "taskset_id": taskset_id,
                        "parameters": {
                            "taskset_repetition": repetition,
                            "tasks_per_taskset": tasks,
                            "interference_factor": interference,
                            "probability_factor": probability,
                            "max_utilization": util_factor * cores,
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
        return tasksets

    def generate_assignments(self, tasksets):
        assignments = {}

        assignment_methods = ["Citta", "Wmin"]
        sorting_criteria = ["wcet_ascending"]
        solving_time_limit_milp_assignment = [300]

        assignment_index = 1
        for taskset_key, taskset_data in tasksets.items():
            cores = int(taskset_key.split('_c')[1])
            for method, sorting, solving_time in itertools.product(
                    assignment_methods, sorting_criteria, solving_time_limit_milp_assignment
            ):
                assignment_id = f"assignment_generate_{assignment_index}_c{cores}"
                assignments[assignment_id] = {
                    "taskset": {
                        "action": "open",
                        "taskset_id": taskset_key,
                        "parameters": {
                            "none": "none"
                        }
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
                                "solving_time_limit_MILP": solving_time,
                                "solver_name": "glpk"
                            }
                        }
                    },
                    "scheduling": {
                        "action": "none"
                    }
                }
                assignment_index += 1
        return assignments

    def generate_schedulings(self, assignments):
        schedulings = {}

        scheduling_algorithms = ["EarliestDeadlineFirst",
                                 "EarliestDeadlineFirstVariant1", "Rhma", "CombinedScheduler"]
        non_preemption_time_variant2_options = [
            "number_of_tasks", "wcet_of_tasks"]
        solving_time_limit_milp_scheduling = [300]

        scheduling_index = 1
        for assignment_key, assignment_data in assignments.items():
            for algorithm, non_preemption, solving_time in itertools.product(
                    scheduling_algorithms, non_preemption_time_variant2_options, solving_time_limit_milp_scheduling
            ):
                cores = assignment_data["assignment"]["parameters"]["number_of_cores"]
                scheduling_id = f"scheduling_generate_{scheduling_index}_c{cores}"
                schedulings[scheduling_id] = {
                    "taskset": {
                        "action": "open",
                        "taskset_id": assignment_data["taskset"]["taskset_id"],
                        "parameters": {
                            "none": "none"
                        }
                    },
                    "assignment": {
                        "action": "open",
                        "assignment_id": assignment_key,
                        "taskset_id": assignment_data["taskset"]["taskset_id"],
                        "parameters": {
                            "none": "none"
                        }
                    },
                    "scheduling": {
                        "action": "generate",
                        "scheduling_id": scheduling_id,
                        "taskset_id": assignment_data["taskset"]["taskset_id"],
                        "assignment_id": assignment_key,
                        "parameters": {
                            "scheduling_algorithm": algorithm,
                            "scheduling_options": {
                                "non_preemption_time_variant2": non_preemption,
                                "solving_time_limit_MILP": solving_time,
                                "solver_name": "glpk"
                            }
                        }
                    }
                }
                scheduling_index += 1
        return schedulings

    def save_to_json(self, data, filename):
        with open(self.config_dir / filename, "w") as f:
            json.dump(data, f, indent=4)

    def generate_all_configs(self):
        tasksets = self.generate_tasksets()
        self.save_to_json(tasksets, "tasksets.json")

        assignments = self.generate_assignments(tasksets)
        self.save_to_json(assignments, "assignments.json")

        schedulings = self.generate_schedulings(assignments)
        self.save_to_json(schedulings, "schedulings.json")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 config_generator.py <path_to_config_dir>")
        sys.exit(1)

    config_dir = sys.argv[1]
    generator = ConfigGenerator(config_dir)
    generator.generate_all_configs()
    print(f"Configurations generated in {config_dir}")
