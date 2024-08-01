import json
import itertools
from pathlib import Path


class ConfigGenerator:
    def __init__(self, config_dir, experience_data):
        self.config_dir = Path(config_dir) / "config_files"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.experience_data = experience_data

        self.taskset_repetitions = self.experience_data.get("taskset_parameters", {}).get(
            "taskset_repetitions", [1]
        )
        self.tasks_per_taskset = self.experience_data.get("taskset_parameters", {}).get(
            "tasks_per_taskset", [4]
        )
        self.interference_factors = self.experience_data.get("taskset_parameters", {}).get(
            "interference_factors", [0]
        )
        self.probability_factors = self.experience_data.get("taskset_parameters", {}).get(
            "probability_factors", [0]
        )
        self.max_utilization_factors = self.experience_data.get("taskset_parameters", {}).get(
            "max_utilization_factors", [0.2]
        )
        self.deadline_options = self.experience_data.get("taskset_parameters", {}).get(
            "deadline_options", ["eq_period"]
        )
        self.prime_exponent_hyperperiod_combinations = self.experience_data.get(
            "taskset_parameters", {}
        ).get("prime_exponent_hyperperiod_combinations", [(10000, 7, 3)])
        self.number_of_cores_list = self.experience_data.get("taskset_parameters", {}).get(
            "number_of_cores_list", [2]
        )

        self.assignment_methods = self.experience_data.get("assignment_parameters", {}).get(
            "assignment_methods",
            ["WorstFitAssigner"],
        )
        self.sorting_criteria = self.experience_data.get("assignment_parameters", {}).get(
            "sorting_criteria",
            [
                "random_order",
            ],
        )
        self.solving_time_limit_milp_assignment = self.experience_data.get(
            "assignment_parameters", {}
        ).get("solving_time_limit_milp_assignment", [300])

        # Paramètres des schedulings
        self.scheduling_algorithms = self.experience_data.get("scheduling_parameters", {}).get(
            "scheduling_algorithms",
            [
                "EarliestDeadlineFirst"
            ],
        )
        self.non_preemption_time_variant2_options = self.experience_data.get(
            "scheduling_parameters", {}
        ).get(
            "non_preemption_time_variant2_options",
            ["number_of_tasks"],
        )
        self.solving_time_limit_milp_scheduling = self.experience_data.get(
            "scheduling_parameters", {}
        ).get("solving_time_limit_milp_scheduling", [300])

    def generate_tasksets(self):
        tasksets = {}

        taskset_index = 1
        for repetition, tasks, interference, probability, util_factor, deadline, (
            hyperperiod,
            prime,
            exponent,
        ) in itertools.product(
            self.taskset_repetitions,
            self.tasks_per_taskset,
            self.interference_factors,
            self.probability_factors,
            self.max_utilization_factors,
            self.deadline_options,
            self.prime_exponent_hyperperiod_combinations,
        ):
            for cores in self.number_of_cores_list:
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
                                "gen_limit_exponent": exponent,
                            },
                        },
                    },
                    "assignment": {"action": "none"},
                    "scheduling": {"action": "none"},
                }
                taskset_index += 1
        return tasksets

    def generate_assignments(self, tasksets):
        assignments = {}

        assignment_index = 1
        for taskset_key, taskset_data in tasksets.items():
            cores = int(taskset_key.split("_c")[1])
            for method, sorting, solving_time in itertools.product(
                self.assignment_methods,
                self.sorting_criteria,
                self.solving_time_limit_milp_assignment,
            ):
                assignment_id = f"assignment_generate_{assignment_index}_c{cores}"
                assignments[assignment_id] = {
                    "taskset": {
                        "action": "open",
                        "taskset_id": taskset_key,
                        "parameters": {"none": "none"},
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
                                "solver_name": "gurobi",
                            },
                        },
                    },
                    "scheduling": {"action": "none"},
                }
                assignment_index += 1
        return assignments

    def generate_schedulings(self, assignments):
        schedulings = {}

        scheduling_index = 1
        for assignment_key, assignment_data in assignments.items():
            for algorithm, non_preemption, solving_time in itertools.product(
                self.scheduling_algorithms,
                self.non_preemption_time_variant2_options,
                self.solving_time_limit_milp_scheduling,
            ):
                cores = assignment_data["assignment"]["parameters"]["number_of_cores"]
                scheduling_id = f"scheduling_generate_{scheduling_index}_c{cores}"
                schedulings[scheduling_id] = {
                    "taskset": {
                        "action": "open",
                        "taskset_id": assignment_data["taskset"]["taskset_id"],
                        "parameters": {"none": "none"},
                    },
                    "assignment": {
                        "action": "open",
                        "assignment_id": assignment_key,
                        "taskset_id": assignment_data["taskset"]["taskset_id"],
                        "parameters": {"none": "none"},
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
                                "solver_name": "gurobi",
                            },
                        },
                    },
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

    if len(sys.argv) != 3:
        print(
            "Usage: python3 config_generator.py <path_to_config_dir> <experience_json_path>"
        )
        sys.exit(1)

    config_dir = sys.argv[1]
    experience_json_path = sys.argv[2]

    with open(experience_json_path, "r") as f:
        experience_data = json.load(f)

    generator = ConfigGenerator(config_dir, experience_data)
    generator.generate_all_configs()
    print(f"Configurations generated in {config_dir}")
