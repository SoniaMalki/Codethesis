import json
import re
from copy import deepcopy
import time

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

FULL_ASSIGNMENT_PARAMETERS = {
    "assignment_methods": ["WorstFitAssigner", "FirstFitAssigner", "BestFitAssigner", "Citta", "Wmin"],
    "sorting_criteria": ["wcet_ascending", "wcet_descending", "period_ascending", "period_descending", "utilization_ascending", "utilization_descending", "execution_slack_ascending", "execution_slack_descending", "random_order"],
    "solving_time_limit_milp_assignment": [300],
    "solver_name_assignment": ["gurobi"]
}

FULL_SCHEDULING_PARAMETERS = {
    "scheduling_algorithms": ["EarliestDeadlineFirst", "EarliestDeadlineFirstVariant1", "EarliestDeadlineFirstVariant2", "DeadlineMonotonic", "DeadlineMonotonicVariant1", "DeadlineMonotonicVariant2", "CombinedScheduler", "Rhma"],
    "non_preemption_time_variant2_options": ["number_of_tasks", "wcet_of_tasks", "system_utilization"],
    "solving_time_limit_milp_scheduling": [300],
    "solver_name_scheduling": ["gurobi"]
}


def create_reduced_experience(full_config, name, taskset_params=None, assignment_params=None, scheduling_params=None):
    """Creates a reduced experience configuration.

    Args:
        full_config: The full configuration dictionary.
        name: A descriptive name for the new reduced configuration.
        taskset_params:  A dictionary of taskset parameters to include. If None, 
                         use the taskset parameters from the full config.
        assignment_params: A dictionary of assignment parameters to include. 
                           If None, use FULL_ASSIGNMENT_PARAMETERS.
        scheduling_params: A dictionary of scheduling parameters to include. 
                           If None, use FULL_SCHEDULING_PARAMETERS.

    Returns:
        A dictionary containing the reduced configuration under the 
        key "full_experience_<name>".
    """
    print(full_config)
    print(name)
    print(taskset_params)
    print(assignment_params)
    print(scheduling_params)
    new_config = {}

    # Add taskset parameters
    if taskset_params is None:
        new_config["taskset_parameters"] = deepcopy(
            full_config["taskset_parameters"])
    else:
        new_config["taskset_parameters"] = taskset_params

    # Add assignment parameters
    if assignment_params is None:
        new_config["assignment_parameters"] = deepcopy(
            FULL_ASSIGNMENT_PARAMETERS)
    else:
        new_config["assignment_parameters"] = assignment_params

    # Add scheduling parameters
    if scheduling_params is None:
        new_config["scheduling_parameters"] = deepcopy(
            FULL_SCHEDULING_PARAMETERS)
    else:
        new_config["scheduling_parameters"] = scheduling_params

    return {f"full_experience_{name}": {"config_parameters": new_config}}


def format_json_string(data):
    """Formats a JSON string for compact dictionaries and lists.

    Args:
        data: The data to be formatted as a JSON string.

    Returns:
        A formatted JSON string.
    """
    def compact_list_format(match):
        """Compacts a list within the JSON string."""
        compacted = re.sub(r'\s+', ' ', match.group(0))
        return compacted.strip()

    json_string = json.dumps(data, indent=2, separators=(',', ': '))
    json_string = re.sub(r'\[[^\]]*\]', compact_list_format,
                         json_string, flags=re.MULTILINE)
    return json_string


def split_taskset_experiences(full_config):
    """Creates experience configurations for taskset generation only."""
    taskset_experiences = []

    # 1. Only Taskset
    taskset_experiences.append(create_reduced_experience(
        full_config, "only_taskset",
        assignment_params=EMPTY_ASSIGNMENT_PARAMETERS,
        scheduling_params=EMPTY_SCHEDULING_PARAMETERS))

    # 2. Only Taskset with different max_utilization_factors
    for i, util_factor in enumerate(full_config["taskset_parameters"]["max_utilization_factors"]):
        taskset_config = deepcopy(full_config)
        taskset_config["taskset_parameters"]["max_utilization_factors"] = [
            util_factor]
        taskset_experiences.append(create_reduced_experience(
            taskset_config, f"only_taskset_{i+1}",
            assignment_params=EMPTY_ASSIGNMENT_PARAMETERS,
            scheduling_params=EMPTY_SCHEDULING_PARAMETERS))
    return taskset_experiences


def split_assignment_experiences(full_config):
    """Creates experience configurations for assignment methods."""
    assignment_experiences = []

    # 3. Only Assignment
    assignment_experiences.append(create_reduced_experience(
        full_config, "only_assignment",
        assignment_params=full_config["assignment_parameters"],
        scheduling_params=EMPTY_SCHEDULING_PARAMETERS))

    # 4. Only Assignment with Simple Assigners
    assignment_experiences.append(create_reduced_experience(full_config, "only_assignment_simple_assigner",
                                                            assignment_params={"assignment_methods": ["WorstFitAssigner", "FirstFitAssigner", "BestFitAssigner"],
                                                                               "sorting_criteria": full_config["assignment_parameters"]["sorting_criteria"],
                                                                               "solving_time_limit_milp_assignment": [],  # Added back the key
                                                                               "solver_name_assignment": []},  # Added back the key
                                                            scheduling_params=EMPTY_SCHEDULING_PARAMETERS))
    # 5. Only Assignment with Citta
    assignment_experiences.append(create_reduced_experience(full_config, "only_assignment_citta",
                                                            assignment_params={"assignment_methods": ["Citta"],
                                                                               "sorting_criteria": full_config["assignment_parameters"]["sorting_criteria"],
                                                                               "solving_time_limit_milp_assignment": [300],
                                                                               "solver_name_assignment": ["gurobi"]},
                                                            scheduling_params=EMPTY_SCHEDULING_PARAMETERS))

    # 6. Only Assignment with Citta, split by sorting criteria
    citta_sorting = {
        "wcet": ["wcet_ascending", "wcet_descending"],
        "period": ["period_ascending", "period_descending"],
        "utilization": ["utilization_ascending", "utilization_descending"],
        "execution_slack": ["execution_slack_ascending", "execution_slack_descending"],
        "random": ["random_order"],
    }
    for name, sorting in citta_sorting.items():
        assignment_experiences.append(create_reduced_experience(full_config, f"only_assignment_citta_sorting_{name}",
                                                                assignment_params={"assignment_methods": ["Citta"],
                                                                                   "sorting_criteria": sorting,
                                                                                   "solving_time_limit_milp_assignment": [300],
                                                                                   "solver_name_assignment": ["gurobi"]},
                                                                scheduling_params=EMPTY_SCHEDULING_PARAMETERS))

    # 7. Only Assignment with Wmin
    assignment_experiences.append(create_reduced_experience(full_config, "only_assignment_wmin",
                                                            assignment_params={"assignment_methods": ["Wmin"],
                                                                               "sorting_criteria": [],
                                                                               "solving_time_limit_milp_assignment": [300],
                                                                               "solver_name_assignment": ["gurobi"]},
                                                            scheduling_params=EMPTY_SCHEDULING_PARAMETERS))
    return assignment_experiences


def split_scheduling_experiences(full_config, include_citta=True):
    """Creates experience configurations for scheduling algorithms."""
    scheduling_experiences = []

    # 8. Only Scheduling (all algorithms)
    scheduling_experiences.append(create_reduced_experience(
        full_config, "only_scheduling" if include_citta else "without_citta_only_scheduling",
        assignment_params=full_config["assignment_parameters"],
        scheduling_params=full_config["scheduling_parameters"]))

    # 9. Only Scheduling with Simple Scheduling algorithms
    scheduling_experiences.append(create_reduced_experience(
        full_config,
        "only_scheduling_simple_scheduling" if include_citta else "without_citta_only_scheduling_simple_scheduling",
        assignment_params=full_config["assignment_parameters"],
        scheduling_params={"scheduling_algorithms": ["EarliestDeadlineFirst", "EarliestDeadlineFirstVariant1",
                                                     "DeadlineMonotonic", "DeadlineMonotonicVariant1"],
                           "non_preemption_time_variant2_options": [],
                           "solving_time_limit_milp_scheduling": [],
                           "solver_name_scheduling": []}))

    # 10. Only Scheduling with individual Simple Scheduling algorithms
    simple_schedulers = ["EarliestDeadlineFirst", "EarliestDeadlineFirstVariant1",
                         "DeadlineMonotonic", "DeadlineMonotonicVariant1"]
    for scheduler in simple_schedulers:
        scheduling_experiences.append(create_reduced_experience(
            full_config,
            f"only_scheduling_simple_scheduling_{scheduler.lower()}" if include_citta else f"without_citta_only_scheduling_simple_scheduling_{scheduler.lower()}",
            assignment_params=full_config["assignment_parameters"],
            scheduling_params={"scheduling_algorithms": [scheduler],
                               "non_preemption_time_variant2_options": [],
                               "solving_time_limit_milp_scheduling": [],
                               "solver_name_scheduling": []}))

    # 11. Only Scheduling with Variant 2 algorithms
    scheduling_experiences.append(create_reduced_experience(
        full_config,
        "only_scheduling_variant_2" if include_citta else "without_citta_only_scheduling_variant_2",
        assignment_params=full_config["assignment_parameters"],
        scheduling_params={"scheduling_algorithms": ["EarliestDeadlineFirstVariant2", "DeadlineMonotonicVariant2"],
                           "non_preemption_time_variant2_options": ["number_of_tasks", "wcet_of_tasks", "system_utilization"],
                           "solving_time_limit_milp_scheduling": [],
                           "solver_name_scheduling": []}))

    # 12. Only Scheduling with individual Variant 2 algorithms
    variant2_schedulers = [
        "EarliestDeadlineFirstVariant2", "DeadlineMonotonicVariant2"]
    for scheduler in variant2_schedulers:
        scheduling_experiences.append(create_reduced_experience(
            full_config,
            f"only_scheduling_variant_2_{scheduler.lower()}" if include_citta else f"without_citta_only_scheduling_variant_2_{scheduler.lower()}",
            assignment_params=full_config["assignment_parameters"],
            scheduling_params={"scheduling_algorithms": [scheduler],
                               "non_preemption_time_variant2_options": ["number_of_tasks", "wcet_of_tasks", "system_utilization"],
                               "solving_time_limit_milp_scheduling": [],
                               "solver_name_scheduling": []}))

    # 13. Only Scheduling with CombinedScheduler
    scheduling_experiences.append(create_reduced_experience(
        full_config,
        "only_scheduling_combined" if include_citta else "without_citta_only_scheduling_combined",
        assignment_params=full_config["assignment_parameters"],
        scheduling_params={"scheduling_algorithms": ["CombinedScheduler"],
                           "non_preemption_time_variant2_options": ["number_of_tasks", "wcet_of_tasks", "system_utilization"],
                           "solving_time_limit_milp_scheduling": [],
                           "solver_name_scheduling": []}))

    # 14. Only Scheduling with CombinedScheduler, split by sorting criteria
    for name in ["number_of_tasks", "wcet_of_tasks", "system_utilization"]:
        scheduling_experiences.append(create_reduced_experience(
            full_config,
            f"only_scheduling_combined_sorting_criterion_{name}" if include_citta else f"without_citta_only_scheduling_combined_sorting_criterion_{name}",
            assignment_params=full_config["assignment_parameters"],
            scheduling_params={"scheduling_algorithms": ["CombinedScheduler"],
                               "non_preemption_time_variant2_options": [name],
                               "solving_time_limit_milp_scheduling": [],
                               "solver_name_scheduling": []}))

    # 15. Only Scheduling with RHMA
    scheduling_experiences.append(create_reduced_experience(
        full_config,
        "only_scheduling_rhma" if include_citta else "without_citta_only_scheduling_rhma",
        assignment_params=full_config["assignment_parameters"],
        scheduling_params={"scheduling_algorithms": ["Rhma"],
                           "non_preemption_time_variant2_options": ["number_of_tasks", "wcet_of_tasks", "system_utilization"],
                           "solving_time_limit_milp_scheduling": [300],
                           "solver_name_scheduling": ["gurobi"]}))

    # 16. Only Scheduling with RHMA, split by sorting criteria
    for name in ["number_of_tasks", "wcet_of_tasks", "system_utilization"]:
        scheduling_experiences.append(create_reduced_experience(
            full_config,
            f"only_scheduling_rhma_sorting_criterion_{name}" if include_citta else f"without_citta_only_scheduling_rhma_sorting_criterion_{name}",
            assignment_params=full_config["assignment_parameters"],
            scheduling_params={"scheduling_algorithms": ["Rhma"],
                               "non_preemption_time_variant2_options": [name],
                               "solving_time_limit_milp_scheduling": [300],
                               "solver_name_scheduling": ["gurobi"]})
        )
    return scheduling_experiences


def split_experience(experience_data):
    """Splits a full experience configuration into smaller configurations."""
    full_config = experience_data["full_experience"]["config_parameters"]
    all_experiences = [experience_data]  # Start with the full experience

    all_experiences.extend(split_taskset_experiences(full_config))
    all_experiences.extend(split_assignment_experiences(full_config))

    # Create deepcopy here!
    no_citta_config = deepcopy(full_config)
    # Remove Citta for the without_citta experiences
    no_citta_config["assignment_parameters"]["assignment_methods"] = [
        "WorstFitAssigner", "FirstFitAssigner", "BestFitAssigner", "Wmin"]

    all_experiences.extend(split_scheduling_experiences(
        full_config, include_citta=True))
    all_experiences.extend(split_scheduling_experiences(
        no_citta_config, include_citta=False))

    return all_experiences


# --- Main Execution ---
if __name__ == "__main__":
    # Load the base experience JSON file
    with open("base_experience.json", "r") as f:
        experience_data = json.load(f)

    # Split the experience configuration
    all_experiences = split_experience(experience_data)

    # Combine all experiences into a single dictionary
    final_experience_data = {}
    for experience in all_experiences:
        final_experience_data.update(experience)

    # Write the formatted JSON to a file
    with open("experience.json", "w") as f:
        f.write(format_json_string(final_experience_data))
