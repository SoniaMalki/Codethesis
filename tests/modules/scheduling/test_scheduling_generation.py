import os
from pathlib import Path
import random
import numpy as np
import pytest
from modules.assignment.assignment_generator import AssignmentGenerator
from modules.scheduling.scheduling_loader_saver import SchedulingLoaderSaver
from modules.scheduling.scheduling_set import SchedulingSet
from modules.scheduling.scheduling import Scheduling
from modules.scheduling.composite_scheduling import CompositeScheduling
from modules.assignment.assignment_set import AssignmentSet
from modules.assignment.assignment import Assignment
from modules.scheduling.scheduling_generator import SchedulingGenerator
from modules.taskset.taskset_set_generator import TasksetSetGenerator
from modules.taskset.taskset_set_manual import TasksetSetManual

save_results = False
np.random.seed(42)
random.seed(42)

scheduling_algorithms_without_combination = [
    "EarliestDeadlineFirst",
    "EarliestDeadlineFirstVariant1",
    "EarliestDeadlineFirstVariant2",
    "DeadlineMonotonic",
    "DeadlineMonotonicVariant1",
    "DeadlineMonotonicVariant2"
]
scheduling_algorithms_with_combination = [
    "CombinedScheduler",
    "Rhma"
]
scheduling_algorithms = scheduling_algorithms_with_combination + \
    scheduling_algorithms_without_combination
experiences = ["manual_1"]


def prepare_input_data_manual_1(scheduling_algorithm):
    taskset_id = "taskset_manual_1"
    taskset_action = "manual"
    taskset_parameters = {
        "wcet_list": [2, 3, 2, 3],
        "deadline_list": [6, 10, 7, 9],
        "period_list": [6, 10, 7, 9],
        "interference_list": [
            [0, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0]
        ],
        "utilization_list": [0.3333, 0.3, 0.2857, 0.3333]
    }
    assignment_parameters = {
        "assignment_id": "assignment_manual_1",
        "taskset_id": "taskset_manual_1",
        "citta_criteria": [""],
        "assignment_method": ["WFDU"],
        "number_of_cores": 2
    }
    scheduling_parameters = {
        "assignment_id": "assignment_manual_1",
        "taskset_id": "taskset_manual_1",
        "scheduling_id": "scheduling_manual_1",
        "scheduling_algorithms": [scheduling_algorithm]
    }
    return taskset_action, taskset_id, taskset_parameters, assignment_parameters, scheduling_parameters


def prepare_input_data_generate_1(scheduling_algorithm):
    taskset_id = "taskset_generate_1"
    taskset_action = "generate"
    taskset_parameters = {
        "taskset_repetition": 1,
        "list_of_probability_factors": [0.1],
        "list_of_max_utilization": [0.2],
        "tasks_per_taskset": 4,
        "list_of_interference_factors": [0.2]
    }
    assignment_parameters = {
        "assignment_id": "assignment_generate_1",
        "taskset_id": "taskset_generate_1",
        "citta_criteria": [""],
        "assignment_method": ["WFDU"],
        "number_of_cores": 2
    }
    scheduling_parameters = {
        "assignment_id": "assignment_generate_1",
        "taskset_id": "taskset_generate_1",
        "scheduling_id": "scheduling_generate_1",
        "scheduling_algorithms": [scheduling_algorithm]
    }
    return taskset_action, taskset_id, taskset_parameters, assignment_parameters, scheduling_parameters


def prepare_input_data(experience, scheduling_algorithm):
    if experience == "manual_1":
        return prepare_input_data_manual_1(scheduling_algorithm=scheduling_algorithm)
    elif experience == "generate_1":
        return prepare_input_data_generate_1(scheduling_algorithm=scheduling_algorithm)


def prepare_output_data(scheduling_loader_saver, experience, scheduling, scheduling_parameters, scheduling_algorithm):
    save_test_results(scheduling_loader_saver, scheduling,
                      scheduling_parameters, experience, scheduling_algorithm)
    expected_scheduling = scheduling_loader_saver.load_test_expected_result(
        scheduling_parameters["scheduling_id"],
        experience,
        scheduling_algorithm,
    )
    return expected_scheduling


def create_taskset_manual(taskset_id, taskset_parameters):
    generator = TasksetSetManual(taskset_id, **taskset_parameters)
    return generator.create_taskset_set()


def create_taskset_generate(taskset_id, taskset_parameters):
    generator = TasksetSetGenerator(taskset_id, **taskset_parameters)
    return generator.generate_taskset_set()


def create_assignment(taskset, assignment_parameters):
    generator = AssignmentGenerator(
        taskset_set_obj=taskset,
        taskset_id=assignment_parameters["taskset_id"],
        assignment_id=assignment_parameters["assignment_id"],
        assignment_method=assignment_parameters["assignment_method"],
        citta_criteria=assignment_parameters["citta_criteria"],
        number_of_cores=assignment_parameters["number_of_cores"]
    )
    assignment = generator.generate_assignment_set()
    return assignment


def create_scheduling(taskset, assignment, scheduling_parameters):
    generator = SchedulingGenerator(
        taskset_set_obj=taskset,
        assignment_set_obj=assignment,
        taskset_id=scheduling_parameters["taskset_id"],
        assignment_id=scheduling_parameters["assignment_id"],
        scheduling_id=scheduling_parameters["scheduling_id"],
        scheduling_algorithms=scheduling_parameters["scheduling_algorithms"]
    )
    scheduling = generator.generate_scheduling_set()
    return scheduling


def shape_interference(taskset_set_obj):
    new_interference = []
    for taskset in taskset_set_obj:
        taskset_interference = np.max(taskset.interference, axis=1)
        new_interference.append(taskset_interference)
        taskset.interference = taskset_interference
        for task_index, task in enumerate(taskset):
            task.interference = taskset_interference[task_index]
    taskset_set_obj.interference = np.array(new_interference)
    return taskset_set_obj


def verify_scheduling(scheduling, expected_scheduling):
    for result, exp_s in zip(scheduling, expected_scheduling):
        assert result.success == exp_s.success
        assert result.schedule == exp_s.schedule


@pytest.fixture(autouse=True)
def reset_random_seed():
    np.random.seed(42)
    random.seed(42)


def generate_param_combinations():
    combinations = []
    for algorithm in scheduling_algorithms:
        for experience in experiences:
            combinations.append((algorithm, experience))
    return combinations


def save_test_results(scheduling_loader_saver, scheduling, scheduling_parameters, experience, scheduling_algorithm):
    if save_results:
        # Sauvegarder les résultats pour la première exécution du test
        scheduling_loader_saver.save_test_expected_result(
            scheduling,
            scheduling_parameters["scheduling_id"],
            experience,
            scheduling_algorithm,
        )


@pytest.mark.parametrize("scheduling_algorithm,experience", generate_param_combinations(), ids=lambda val: f"{val}")
def test_scheduling(scheduling_algorithm, experience):
    input_data = prepare_input_data(
        experience, scheduling_algorithm)
    taskset_action, taskset_id, taskset_parameters, assignment_parameters, scheduling_parameters = input_data
    scheduling_loader_saver = SchedulingLoaderSaver(Path(os.getcwd()))

    if taskset_action == "manual":
        taskset = create_taskset_manual(taskset_id, taskset_parameters)
    elif taskset_action == "generate":
        taskset = create_taskset_generate(taskset_id, taskset_parameters)
    else:
        raise ValueError("Invalid parameter")
    assignment = create_assignment(taskset, assignment_parameters)
    if assignment_parameters["assignment_method"][0].lower() != "wmin":
        shape_interference(taskset)
    scheduling = create_scheduling(taskset, assignment, scheduling_parameters)

    expected_scheduling = prepare_output_data(
        scheduling_loader_saver, experience, scheduling, scheduling_parameters, scheduling_algorithm)

    if expected_scheduling is not None:
        verify_scheduling(scheduling, expected_scheduling)
    else:
        assert False, "Résultats de scheduling attendus non trouvés, veuillez les créer."
