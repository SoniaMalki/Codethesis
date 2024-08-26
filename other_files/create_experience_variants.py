import json
import os
from pathlib import Path
import re
from copy import deepcopy
import argparse

# Define empty assignment_parameters and scheduling_parameters structures
EMPTY_ASSIGNMENT_PARAMETERS = {
    "assignment_methods": [],
    "sorting_criteria": [],
    "solving_time_limit_milp_assignment": [],
    "solver_name_assignment": []
}

EMPTY_SCHEDULING_PARAMETERS = {
    "scheduling_algorithms": [],
    "non_preemption_time_variant2_options": [],
    "solving_time_limit_milp_scheduling": [],
    "solver_name_scheduling": []
}

# Full parameter definitions to maintain the strict order
FULL_ASSIGNMENT_METHODS = ["WorstFitAssigner",
                           "FirstFitAssigner", "BestFitAssigner", "Citta", "Wmin"]
FULL_SORTING_CRITERIA = ["wcet_ascending", "wcet_descending", "period_ascending", "period_descending",
                         "utilization_ascending", "utilization_descending", "execution_slack_ascending", "execution_slack_descending", "random_order"]
FULL_SOLVING_TIME_LIMIT_ASSIGNMENT = [300]
FULL_SOLVER_NAME_ASSIGNMENT = ["gurobi"]

FULL_SCHEDULING_ALGORITHMS = ["EarliestDeadlineFirst", "EarliestDeadlineFirstVariant1", "EarliestDeadlineFirstVariant2",
                              "DeadlineMonotonic", "DeadlineMonotonicVariant1", "DeadlineMonotonicVariant2", "CombinedScheduler", "Rhma"]
FULL_NON_PREEMPTION_OPTIONS = [
    "number_of_tasks", "wcet_of_tasks", "system_utilization"]
FULL_SOLVING_TIME_LIMIT_SCHEDULING = [300]
FULL_SOLVER_NAME_SCHEDULING = ["gurobi"]

FULL_ASSIGNMENT_PARAMETERS = {
    "assignment_methods": FULL_ASSIGNMENT_METHODS,
    "sorting_criteria": FULL_SORTING_CRITERIA,
    "solving_time_limit_milp_assignment": FULL_SOLVING_TIME_LIMIT_ASSIGNMENT,
    "solver_name_assignment": FULL_SOLVER_NAME_ASSIGNMENT
}

FULL_SCHEDULING_PARAMETERS = {
    "scheduling_algorithms": FULL_SCHEDULING_ALGORITHMS,
    "non_preemption_time_variant2_options": FULL_NON_PREEMPTION_OPTIONS,
    "solving_time_limit_milp_scheduling": FULL_SOLVING_TIME_LIMIT_SCHEDULING,
    "solver_name_scheduling": FULL_SOLVER_NAME_SCHEDULING
}


def create_reduced_experience(full_config, name, taskset_params=None, assignment_params=None, scheduling_params=None):
    """Creates a reduced experience configuration."""
    new_config = {}

    # Use deepcopy to avoid altering the original structures
    new_config["taskset_parameters"] = deepcopy(
        taskset_params if taskset_params is not None else full_config.get("taskset_parameters", {}))

    new_config["assignment_parameters"] = deepcopy(
        assignment_params if assignment_params is not None else full_config.get("assignment_parameters", FULL_ASSIGNMENT_PARAMETERS))

    new_config["scheduling_parameters"] = deepcopy(
        scheduling_params if scheduling_params is not None else full_config.get("scheduling_parameters", FULL_SCHEDULING_PARAMETERS))

    return {f"full_experience_{name}": {"config_parameters": new_config}}


def format_json_string(data):
    """Formats a JSON string for compact dictionaries and lists."""
    def compact_list_format(match):
        compacted = re.sub(r'\s+', ' ', match.group(0))
        return compacted.strip()

    json_string = json.dumps(data, indent=2, separators=(',', ': '))
    json_string = re.sub(r'\[[^\]]*\]', compact_list_format,
                         json_string, flags=re.MULTILINE)
    return json_string


def split_taskset_experiences(full_config, prefix=""):
    """Creates experience configurations for taskset generation only."""
    taskset_experiences = []
    taskset_params = full_config.get("taskset_parameters", {})
    max_utilization_factors = taskset_params.get("max_utilization_factors", [])

    # 1. Only Taskset
    taskset_experiences.append(create_reduced_experience(
        full_config, f"{prefix}only_taskset",
        assignment_params=EMPTY_ASSIGNMENT_PARAMETERS,
        scheduling_params=EMPTY_SCHEDULING_PARAMETERS))

    # 2. Only Taskset with different max_utilization_factors
    for i, util_factor in enumerate(max_utilization_factors):
        taskset_config = deepcopy(full_config)
        taskset_config["taskset_parameters"]["max_utilization_factors"] = [
            util_factor]
        taskset_experiences.append(create_reduced_experience(
            taskset_config, f"{prefix}only_taskset_{i+1}",
            assignment_params=EMPTY_ASSIGNMENT_PARAMETERS,
            scheduling_params=EMPTY_SCHEDULING_PARAMETERS))
    return taskset_experiences


def split_assignment_experiences(full_config, prefix=""):
    """Creates experience configurations for assignment methods."""
    assignment_experiences = []
    assignment_params = full_config.get("assignment_parameters", {})

    # Check if assignment methods exist and create experiences accordingly
    if "assignment_methods" in assignment_params:
        available_methods = set(assignment_params["assignment_methods"])

        # 3. Only Assignment
        assignment_experiences.append(create_reduced_experience(
            full_config, f"{prefix}only_assignment",
            assignment_params=assignment_params,
            scheduling_params=EMPTY_SCHEDULING_PARAMETERS))

        # Simple Assigners
        # ["WorstFitAssigner", "FirstFitAssigner", "BestFitAssigner"]
        simple_assigners = set(FULL_ASSIGNMENT_METHODS[:3])
        if simple_assigners & available_methods:
            assignment_experiences.append(create_reduced_experience(
                full_config, f"{prefix}only_assignment_simple_assigner",
                assignment_params={
                    "assignment_methods": [method for method in FULL_ASSIGNMENT_METHODS if method in simple_assigners & available_methods],
                    "sorting_criteria": [criterion for criterion in FULL_SORTING_CRITERIA if criterion in assignment_params.get("sorting_criteria", [])],
                    "solving_time_limit_milp_assignment": [],
                    "solver_name_assignment": []
                },
                scheduling_params=EMPTY_SCHEDULING_PARAMETERS))

        # Citta Assigners
        if "Citta" in available_methods:
            assignment_experiences.append(create_reduced_experience(
                full_config, f"{prefix}only_assignment_citta",
                assignment_params={
                    "assignment_methods": ["Citta"],
                    "sorting_criteria": [criterion for criterion in FULL_SORTING_CRITERIA if criterion in assignment_params.get("sorting_criteria", [])],
                    "solving_time_limit_milp_assignment": [300],
                    "solver_name_assignment": ["gurobi"]
                },
                scheduling_params=EMPTY_SCHEDULING_PARAMETERS))

            # Citta with different sorting criteria
            citta_sorting_criteria = {
                "wcet": ["wcet_ascending", "wcet_descending"],
                "period": ["period_ascending", "period_descending"],
                "utilization": ["utilization_ascending", "utilization_descending"],
                "execution_slack": ["execution_slack_ascending", "execution_slack_descending"],
                "random": ["random_order"],
            }
            for name, sorting in citta_sorting_criteria.items():
                if set(sorting) & set(assignment_params.get("sorting_criteria", [])):
                    assignment_experiences.append(create_reduced_experience(
                        full_config, f"{prefix}only_assignment_citta_sorting_{name}",
                        assignment_params={
                            "assignment_methods": ["Citta"],
                            "sorting_criteria": [criterion for criterion in sorting if criterion in assignment_params.get("sorting_criteria", [])],
                            "solving_time_limit_milp_assignment": [300],
                            "solver_name_assignment": ["gurobi"]
                        },
                        scheduling_params=EMPTY_SCHEDULING_PARAMETERS))

        # Wmin Assigners
        if "Wmin" in available_methods:
            assignment_experiences.append(create_reduced_experience(
                full_config, f"{prefix}only_assignment_wmin",
                assignment_params={
                    "assignment_methods": ["Wmin"],
                    "sorting_criteria": [],
                    "solving_time_limit_milp_assignment": [300],
                    "solver_name_assignment": ["gurobi"]
                },
                scheduling_params=EMPTY_SCHEDULING_PARAMETERS))

    return assignment_experiences


def split_scheduling_experiences(full_config, prefix=""):
    """Creates experience configurations for scheduling algorithms."""
    scheduling_experiences = []
    scheduling_params = full_config.get("scheduling_parameters", {})
    assignment_params = full_config.get("assignment_parameters", {})

    # Check if scheduling algorithms exist and create experiences accordingly
    if "scheduling_algorithms" in scheduling_params:
        available_algorithms = set(scheduling_params["scheduling_algorithms"])

        # 8. Only Scheduling (all algorithms)
        scheduling_experiences.append(create_reduced_experience(
            full_config, f"{prefix}only_scheduling",
            assignment_params=assignment_params,
            scheduling_params=scheduling_params))

        # Scheduling without RHMA
        if available_algorithms - {"Rhma"}:
            scheduling_experiences.append(create_reduced_experience(
                full_config, f"{prefix}only_scheduling_without_rhma",
                assignment_params=assignment_params,
                scheduling_params={
                    "scheduling_algorithms": [algorithm for algorithm in FULL_SCHEDULING_ALGORITHMS if algorithm != "Rhma" and algorithm in available_algorithms],
                    "non_preemption_time_variant2_options": [option for option in FULL_NON_PREEMPTION_OPTIONS if option in scheduling_params.get("non_preemption_time_variant2_options", [])],
                    "solving_time_limit_milp_scheduling": FULL_SOLVING_TIME_LIMIT_SCHEDULING,
                    "solver_name_scheduling": FULL_SOLVER_NAME_SCHEDULING
                }))

        # Simple Scheduling algorithms
        simple_schedulers = {"EarliestDeadlineFirst", "DeadlineMonotonic",
                             "EarliestDeadlineFirstVariant1", "DeadlineMonotonicVariant1"}
        if simple_schedulers & available_algorithms:
            # Use the original order from FULL_SCHEDULING_ALGORITHMS
            scheduling_experiences.append(create_reduced_experience(
                full_config, f"{prefix}only_scheduling_simple_scheduling",
                assignment_params=assignment_params,
                scheduling_params={
                    "scheduling_algorithms": [algorithm for algorithm in FULL_SCHEDULING_ALGORITHMS if algorithm in simple_schedulers & available_algorithms],
                    "non_preemption_time_variant2_options": [],
                    "solving_time_limit_milp_scheduling": [],
                    "solver_name_scheduling": []
                }))

        # Individual Simple Scheduling algorithms in the original order
        for scheduler in FULL_SCHEDULING_ALGORITHMS:
            if scheduler in simple_schedulers and scheduler in available_algorithms:
                scheduling_experiences.append(create_reduced_experience(
                    full_config, f"{prefix}only_scheduling_simple_scheduling_{scheduler.lower()}",
                    assignment_params=assignment_params,
                    scheduling_params={
                        "scheduling_algorithms": [scheduler],
                        "non_preemption_time_variant2_options": [],
                        "solving_time_limit_milp_scheduling": [],
                        "solver_name_scheduling": []
                    }))

        # Variant 2 algorithms
        variant2_schedulers = {
            "EarliestDeadlineFirstVariant2", "DeadlineMonotonicVariant2"}
        if variant2_schedulers & available_algorithms:
            scheduling_experiences.append(create_reduced_experience(
                full_config, f"{prefix}only_scheduling_variant_2",
                assignment_params=assignment_params,
                scheduling_params={
                    "scheduling_algorithms": [algorithm for algorithm in FULL_SCHEDULING_ALGORITHMS if algorithm in variant2_schedulers & available_algorithms],
                    "non_preemption_time_variant2_options": [option for option in FULL_NON_PREEMPTION_OPTIONS if option in scheduling_params.get("non_preemption_time_variant2_options", [])],
                    "solving_time_limit_milp_scheduling": [],
                    "solver_name_scheduling": []
                }))

        # Individual Variant 2 algorithms
        for scheduler in FULL_SCHEDULING_ALGORITHMS:
            if scheduler in variant2_schedulers and scheduler in available_algorithms:
                scheduling_experiences.append(create_reduced_experience(
                    full_config, f"{prefix}only_scheduling_variant_2_{scheduler.lower()}",
                    assignment_params=assignment_params,
                    scheduling_params={
                        "scheduling_algorithms": [scheduler],
                        "non_preemption_time_variant2_options": [option for option in FULL_NON_PREEMPTION_OPTIONS if option in scheduling_params.get("non_preemption_time_variant2_options", [])],
                        "solving_time_limit_milp_scheduling": [],
                        "solver_name_scheduling": []
                    }))

        # Combined Scheduler
        if "CombinedScheduler" in available_algorithms:
            scheduling_experiences.append(create_reduced_experience(
                full_config, f"{prefix}only_scheduling_combined",
                assignment_params=assignment_params,
                scheduling_params={
                    "scheduling_algorithms": ["CombinedScheduler"],
                    "non_preemption_time_variant2_options": [option for option in FULL_NON_PREEMPTION_OPTIONS if option in scheduling_params.get("non_preemption_time_variant2_options", [])],
                    "solving_time_limit_milp_scheduling": [],
                    "solver_name_scheduling": []
                }))

            # Split by sorting criteria
            for name in scheduling_params.get("non_preemption_time_variant2_options", []):
                scheduling_experiences.append(create_reduced_experience(
                    full_config, f"{prefix}only_scheduling_combined_sorting_criterion_{name}",
                    assignment_params=assignment_params,
                    scheduling_params={
                        "scheduling_algorithms": ["CombinedScheduler"],
                        "non_preemption_time_variant2_options": [name],
                        "solving_time_limit_milp_scheduling": [],
                        "solver_name_scheduling": []
                    }))

        # RHMA algorithm
        if "Rhma" in available_algorithms:
            scheduling_experiences.append(create_reduced_experience(
                full_config, f"{prefix}only_scheduling_rhma",
                assignment_params=assignment_params,
                scheduling_params={
                    "scheduling_algorithms": ["Rhma"],
                    "non_preemption_time_variant2_options": [option for option in FULL_NON_PREEMPTION_OPTIONS if option in scheduling_params.get("non_preemption_time_variant2_options", [])],
                    "solving_time_limit_milp_scheduling": [300],
                    "solver_name_scheduling": ["gurobi"]
                }))

            # Split by sorting criteria for RHMA
            for name in scheduling_params.get("non_preemption_time_variant2_options", []):
                scheduling_experiences.append(create_reduced_experience(
                    full_config, f"{prefix}only_scheduling_rhma_sorting_criterion_{name}",
                    assignment_params=assignment_params,
                    scheduling_params={
                        "scheduling_algorithms": ["Rhma"],
                        "non_preemption_time_variant2_options": [name],
                        "solving_time_limit_milp_scheduling": [300],
                        "solver_name_scheduling": ["gurobi"]
                    }))

    return scheduling_experiences


def split_experience(experience_data, split_by_tpt):
    """Splits a full experience configuration based on tasks_per_taskset."""
    full_config = experience_data["full_experience"]["config_parameters"]
    all_experiences = []

    # 1. Always do the base splitting first
    all_experiences.append(experience_data)  # Add original full experience
    all_experiences.extend(split_taskset_experiences(full_config))
    all_experiences.extend(split_assignment_experiences(full_config))
    all_experiences.extend(split_scheduling_experiences(full_config))

    # 2. Split by tpt if enabled
    if split_by_tpt:
        for tpt in full_config.get("taskset_parameters", {}).get("tasks_per_taskset", []):
            tpt_config = deepcopy(full_config)
            tpt_config["taskset_parameters"]["tasks_per_taskset"] = [tpt]

            # Apply all other splitting logic WITH the tpt prefix
            prefix = f"tpt_{tpt}_"
            all_experiences.extend(
                split_taskset_experiences(tpt_config, prefix))
            all_experiences.extend(
                split_assignment_experiences(tpt_config, prefix))
            all_experiences.extend(
                split_scheduling_experiences(tpt_config, prefix))

    return all_experiences


# --- Main Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Split experience configurations.')
    parser.add_argument('--split_by_tpt', action='store_true',
                        help='Enable splitting experiences by tasks_per_taskset')
    args = parser.parse_args()

    # Load the base experience JSON file
    json_path = Path(os.getenv('CODETHESIS'))
    with open(json_path / "base_experience.json", "r") as f:
        experience_data = json.load(f)

    # Split the experience configuration
    all_experiences = split_experience(experience_data, args.split_by_tpt)

    # Combine all experiences into a single dictionary
    final_experience_data = {}
    for experience in all_experiences:
        final_experience_data.update(experience)

    # Write the formatted JSON to a file
    with open(json_path / "experience.json", "w") as f:
        f.write(format_json_string(final_experience_data))
