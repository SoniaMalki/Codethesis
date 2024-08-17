import json
from copy import deepcopy
import pprint
import re


def create_reduced_experience(config, name, **keys_to_remove):
    """Creates a reduced experience configuration by removing specified keys.

    Args:
        config: The original configuration dictionary.
        name: A descriptive name for the new reduced configuration.
        **keys_to_remove: Keyword arguments specifying keys to remove. 
                          Empty lists indicate keys to delete entirely.

    Returns:
        A dictionary containing the reduced configuration under the 
        key "full_experience_<name>".
    """
    new_config = deepcopy(config)
    for key1, value1 in keys_to_remove.items():
        if isinstance(value1, dict):
            for key2, value2 in value1.items():
                if value2 == [] and key2 in new_config.get(key1, {}):
                    del new_config[key1][key2]
        elif value1 == [] and key1 in new_config:
            del new_config[key1]
    return {f"full_experience_{name}": {"config_parameters": new_config}}


def split_taskset_experiences(full_config):
    """Creates experience configurations for taskset generation only."""
    taskset_experiences = []
    # 1. Only Taskset
    taskset_experiences.append(create_reduced_experience(
        full_config, "only_taskset", assignment_parameters=[], scheduling_parameters=[])
    )

    # 2. Only Taskset with different max_utilization_factors
    for i, util_factor in enumerate(full_config["taskset_parameters"]["max_utilization_factors"]):
        taskset_config = deepcopy(full_config["taskset_parameters"])
        taskset_config["max_utilization_factors"] = [util_factor]
        taskset_experiences.append(create_reduced_experience(
            {"taskset_parameters": taskset_config}, f"only_taskset_{i+1}",
            assignment_parameters=[], scheduling_parameters=[])
        )
    return taskset_experiences


def split_assignment_experiences(full_config):
    """Creates experience configurations for assignment methods."""
    assignment_experiences = []
    # 3. Only Assignment
    assignment_experiences.append(create_reduced_experience(
        full_config, "only_assignment", scheduling_parameters=[])
    )

    # 4. Only Assignment with Simple Assigners
    assignment_experiences.append(create_reduced_experience(
        full_config, "only_assignment_simple_assigner",
        assignment_parameters={"assignment_methods": ["WorstFitAssigner", "FirstFitAssigner", "BestFitAssigner"],
                               "solving_time_limit_milp_assignment": [],
                               "solver_name_assignment": []},
        scheduling_parameters=[])
    )

    # 5. Only Assignment with Citta, split by sorting criteria
    citta_sorting = {
        "wcet": ["wcet_ascending", "wcet_descending"],
        "period": ["period_ascending", "period_descending"],
        "utilization": ["utilization_ascending", "utilization_descending"],
        "execution_slack": ["execution_slack_ascending", "execution_slack_descending"],
        "random": ["random_order"],
    }

    for name, sorting in citta_sorting.items():
        assignment_experiences.append(create_reduced_experience(
            full_config, f"only_assignment_citta_sorting_{name}",
            assignment_parameters={"assignment_methods": ["Citta"],
                                   "sorting_criteria": sorting},
            scheduling_parameters=[])
        )

    # 6. Only Assignment with Wmin
    assignment_experiences.append(create_reduced_experience(
        full_config, "only_assignment_wmin",
        assignment_parameters={"assignment_methods": ["Wmin"],
                               "sorting_criteria": []},
        scheduling_parameters=[])
    )
    return assignment_experiences


def split_scheduling_experiences(full_config, include_citta=True):
    """Creates experience configurations for scheduling algorithms."""
    scheduling_experiences = []
    assignment_methods = full_config["assignment_parameters"]["assignment_methods"]
    if not include_citta:
        assignment_methods = [m for m in assignment_methods if m != "Citta"]

    scheduling_config = deepcopy(full_config)
    scheduling_config["assignment_parameters"]["assignment_methods"] = assignment_methods

    # 7. Only Scheduling (All algorithms)
    scheduling_experiences.append(create_reduced_experience(
        scheduling_config, "only_scheduling" if include_citta else "without_citta_only_scheduling")
    )

    # 8. Only Scheduling with simple scheduling algorithms
    scheduling_experiences.append(create_reduced_experience(
        scheduling_config,
        "only_scheduling_simple_scheduling" if include_citta else "without_citta_only_scheduling_simple_scheduling",
        scheduling_parameters={"scheduling_algorithms": ["EarliestDeadlineFirst", "EarliestDeadlineFirstVariant1",
                                                         "DeadlineMonotonic", "DeadlineMonotonicVariant1"],
                               "non_preemption_time_variant2_options": [],
                               "solving_time_limit_milp_scheduling": [],
                               "solver_name_scheduling": []})
    )

    # 9. Only Scheduling with individual simple scheduling algorithms
    simple_schedulers = ["EarliestDeadlineFirst", "EarliestDeadlineFirstVariant1",
                         "DeadlineMonotonic", "DeadlineMonotonicVariant1"]
    for scheduler in simple_schedulers:
        scheduling_experiences.append(create_reduced_experience(
            scheduling_config,
            f"only_scheduling_simple_scheduling_{scheduler.lower()}" if include_citta else f"without_citta_only_scheduling_simple_scheduling_{scheduler.lower()}",
            scheduling_parameters={"scheduling_algorithms": [scheduler],
                                   "non_preemption_time_variant2_options": [],
                                   "solving_time_limit_milp_scheduling": [],
                                   "solver_name_scheduling": []})
        )

    # 10. Only Scheduling with Variant 2 algorithms
    scheduling_experiences.append(create_reduced_experience(
        scheduling_config,
        "only_scheduling_variant_2" if include_citta else "without_citta_only_scheduling_variant_2",
        scheduling_parameters={"scheduling_algorithms": ["EarliestDeadlineFirstVariant2", "DeadlineMonotonicVariant2"],
                               "solving_time_limit_milp_scheduling": [],
                               "solver_name_scheduling": []})
    )

    # 11. Only Scheduling with individual Variant 2 algorithms
    variant2_schedulers = [
        "EarliestDeadlineFirstVariant2", "DeadlineMonotonicVariant2"]
    for scheduler in variant2_schedulers:
        scheduling_experiences.append(create_reduced_experience(
            scheduling_config,
            f"only_scheduling_variant_2_{scheduler.lower()}" if include_citta else f"without_citta_only_scheduling_variant_2_{scheduler.lower()}",
            scheduling_parameters={"scheduling_algorithms": [scheduler],
                                   "solving_time_limit_milp_scheduling": [],
                                   "solver_name_scheduling": []})
        )

    # 12. Only Scheduling with CombinedScheduler, split by sorting criteria
    for name in ["number_of_tasks", "wcet_of_tasks", "system_utilization"]:
        scheduling_experiences.append(create_reduced_experience(
            scheduling_config,
            f"only_scheduling_combined_sorting_criterion_{name}" if include_citta else f"without_citta_only_scheduling_combined_sorting_criterion_{name}",
            scheduling_parameters={"scheduling_algorithms": ["CombinedScheduler"],
                                   "non_preemption_time_variant2_options": [name],
                                   "solving_time_limit_milp_scheduling": [],
                                   "solver_name_scheduling": []})
        )
    scheduling_experiences.append(create_reduced_experience(
        scheduling_config,
        "only_scheduling_combined" if include_citta else "without_citta_only_scheduling_combined",
        scheduling_parameters={"scheduling_algorithms": ["CombinedScheduler"],
                               "solving_time_limit_milp_scheduling": [],
                               "solver_name_scheduling": []})
    )

    # 13. Only Scheduling with RHMA, split by sorting criteria
    for name in ["number_of_tasks", "wcet_of_tasks", "system_utilization"]:
        scheduling_experiences.append(create_reduced_experience(
            scheduling_config,
            f"only_scheduling_rhma_sorting_criterion_{name}" if include_citta else f"without_citta_only_scheduling_rhma_sorting_criterion_{name}",
            scheduling_parameters={"scheduling_algorithms": ["Rhma"],
                                   "non_preemption_time_variant2_options": [name]})
        )
    scheduling_experiences.append(create_reduced_experience(
        scheduling_config,
        "only_scheduling_rhma" if include_citta else "without_citta_only_scheduling_rhma",
        scheduling_parameters={"scheduling_algorithms": ["Rhma"]})
    )

    return scheduling_experiences


def split_experience(experience_data):
    """Splits a full experience configuration into smaller configurations.

    Args:
        experience_data: A dictionary containing the full experience configuration.

    Returns:
        A dictionary containing the full experience configuration and all 
        the split configurations.
    """
    full_config = experience_data["full_experience"]["config_parameters"]
    all_experiences = [experience_data]  # Start with the full experience

    all_experiences.extend(split_taskset_experiences(full_config))
    all_experiences.extend(split_assignment_experiences(full_config))
    all_experiences.extend(split_scheduling_experiences(
        full_config, include_citta=True))
    all_experiences.extend(split_scheduling_experiences(
        full_config, include_citta=False))

    return all_experiences


def format_json_string(data):
    """Formats a JSON string for compact dictionaries and lists.

    Args:
        data: The data to be formatted as a JSON string.

    Returns:
        A formatted JSON string.
    """
    def compact_list_format(match):
        """Compacts a list within the JSON string."""
        # Remove line breaks and extra spaces from the matched list string
        compacted = re.sub(r'\s+', ' ', match.group(0))
        return compacted.strip()

    json_string = json.dumps(data, indent=2, separators=(',', ': '))
    # Use a regular expression to find and format lists
    json_string = re.sub(r'\[[^\]]*\]', compact_list_format,
                         json_string, flags=re.MULTILINE)
    return json_string


# --- Main Execution ---
if __name__ == "__main__":
    # Load the experience JSON file
    with open("base_experience.json", "r") as f:
        experience_data = json.load(f)

    # Split the experience configuration
    all_experiences = split_experience(experience_data)

    # Combine all experiences into a single dictionary
    final_experience_data = {}
    for experience in all_experiences:
        final_experience_data.update(experience)

    # Write the complete experience JSON to a file
    # Write the complete experience JSON to a file
    with open("experience.json", "w") as f:
        f.write(format_json_string(final_experience_data))
