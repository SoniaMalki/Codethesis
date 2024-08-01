
import json
import itertools
from pathlib import Path


class ConfigGenerator:
    def __init__(self, config_dir, experience_data):
        self.config_dir = Path(config_dir) / "config_files"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.experience_data = experience_data

        # Récupérer tous les paramètres depuis experience_data
        for param_section in ["taskset_parameters", "assignment_parameters", "scheduling_parameters"]:
            for param_name, param_value in self.experience_data[param_section].items():
                setattr(self, param_name, param_value)

        # Vérification de tous les paramètres obligatoires
        required_params = [
            "taskset_repetitions",
            "tasks_per_taskset",
            "interference_factors",
            "probability_factors",
            "max_utilization_factors",
            "deadline_options",
            "prime_exponent_hyperperiod_combinations",
            "number_of_cores_list",
            "assignment_methods",
            "sorting_criteria",
            "scheduling_algorithms",
            "non_preemption_time_variant2_options",
            "solving_time_limit_milp_assignment",
            "solving_time_limit_milp_scheduling"
        ]
        for param_name in required_params:
            if getattr(self, param_name) is None:
                raise ValueError(
                    f"Paramètre obligatoire manquant dans experience.json: {param_name}")

        # Dictionnaire pour les paramètres optionnels
        self.optional_params = {
            "sorting_criteria": {
                method: self.sorting_criteria if method != "Wmin" else [""]
                for method in self.assignment_methods
            },
            "solving_time_limit_milp_assignment": {
                method: self.solving_time_limit_milp_assignment
                if method in ["Wmin", "Citta"]
                else [""]
                for method in self.assignment_methods
            },
            "solver_name_assignment": {
                method: self.solver_name_assignment
                if method in ["Wmin", "Citta"]
                else [""]
                for method in self.assignment_methods
            },
            "non_preemption_time_variant2_options": {
                algorithm: self.non_preemption_time_variant2_options
                if algorithm
                in [
                    "EarliestDeadlineFirstVariant2",
                    "DeadlineMonotonicVariant2",
                    "CombinedScheduler",
                    "Rhma",
                ]
                else [""]
                for algorithm in self.scheduling_algorithms
            },
            "solving_time_limit_milp_scheduling": {
                algorithm: self.solving_time_limit_milp_scheduling
                if algorithm == "Rhma"
                else [""]
                for algorithm in self.scheduling_algorithms
            },
            "solver_name_scheduling": {
                algorithm: self.solver_name_scheduling
                if algorithm == "Rhma"
                else [""]
                for algorithm in self.scheduling_algorithms
            },
        }

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
            for method in self.assignment_methods:
                for sorting, solving_time, solver_name in itertools.product(  # Boucles pour sorting, solving_time, solver_name
                    self.optional_params["sorting_criteria"][method],
                    self.optional_params["solving_time_limit_milp_assignment"][method],
                    self.optional_params["solver_name_assignment"][method],
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
                                    "solver_name": solver_name,
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
            cores = assignment_data["assignment"]["parameters"]["number_of_cores"]
            for algorithm in self.scheduling_algorithms:
                for non_preemption, solving_time, solver_name in itertools.product(  # Boucles pour non_preemption, solving_time, solver_name
                    self.optional_params["non_preemption_time_variant2_options"][algorithm],
                    self.optional_params["solving_time_limit_milp_scheduling"][algorithm],
                    self.optional_params["solver_name_scheduling"][algorithm],
                ):
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
                                    "solver_name": solver_name,
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
