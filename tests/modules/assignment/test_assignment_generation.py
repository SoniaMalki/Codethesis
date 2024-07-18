import random
import numpy as np
import pytest
from modules.assignment.assignment_algorithms import citta
from modules.assignment.assignment_set import AssignmentSet
from modules.assignment.assignment_generator import AssignmentGenerator
from modules.assignment.assignment_loader_saver import AssignmentLoaderSaver
from modules.taskset.taskset_set_generator import TasksetSetGenerator
from modules.taskset.taskset_set_manual import TasksetSetManual

np.random.seed(42)
random.seed(42)

assignment_methods_with_criteria = ["CITTA", "BFDU", "FFDU", "WFDU"]
assignment_methods_without_criteria = ["Wmin"]
sorting_criterion_list = ["wcet_ascending", "wcet_descending", "period_ascending", "period_descending", "utilization_ascending",
                          "utilization_descending", "execution_slack_ascending", "execution_slack_descending", "random_order"]
experiences = ["manual_1", "generate_1"]


def prepare_input_data_manual_1(assignment_method, sorting_criterion=""):
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
        "sorting_criterion": [sorting_criterion],
        "assignment_method": [assignment_method],
        "number_of_cores": 2,
        "assignment_options": {}
    }
    return taskset_action, taskset_id, taskset_parameters, assignment_parameters


def create_expected_assignment_output_manual_1(assignment_method, sorting_criterion):
    if assignment_method in assignment_methods_with_criteria:
        assignment_method = (assignment_method, sorting_criterion)
    expected_assignment = {
        ("BFDU", "wcet_ascending"): [(1, [[0, 2, 1], [3]])],
        ("BFDU", "wcet_descending"): [(1, [[1, 3, 0], [2]])],
        ("BFDU", "period_ascending"): [(1, [[0, 2, 3], [1]])],
        ("BFDU", "period_descending"): [(1, [[1, 3, 2], [0]])],
        ("BFDU", "utilization_ascending"): [(1, [[2, 1, 0], [3]])],
        ("BFDU", "utilization_descending"): [(1, [[0, 3, 1], [2]])],
        ("BFDU", "execution_slack_ascending"): [(1, [[0, 2, 3], [1]])],
        ("BFDU", "execution_slack_descending"): [(1, [[1, 3, 2], [0]])],
        ("BFDU", "random_order"): [(1, [[1, 3, 0], [2]])],
        ("FFDU", "wcet_ascending"): [(1, [[0, 2, 1], [3]])],
        ("FFDU", "wcet_descending"): [(1, [[1, 3, 0], [2]])],
        ("FFDU", "period_ascending"): [(1, [[0, 2, 3], [1]])],
        ("FFDU", "period_descending"): [(1, [[1, 3, 2], [0]])],
        ("FFDU", "utilization_ascending"): [(1, [[2, 1, 0], [3]])],
        ("FFDU", "utilization_descending"): [(1, [[0, 3, 1], [2]])],
        ("FFDU", "execution_slack_ascending"): [(1, [[0, 2, 3], [1]])],
        ("FFDU", "execution_slack_descending"): [(1, [[1, 3, 2], [0]])],
        ("FFDU", "random_order"): [(1, [[1, 3, 0], [2]])],
        ("WFDU", "wcet_ascending"): [(1, [[0, 3], [2, 1]])],
        ("WFDU", "wcet_descending"): [(1, [[1, 0], [3, 2]])],
        ("WFDU", "period_ascending"): [(1, [[0, 1], [2, 3]])],
        ("WFDU", "period_descending"): [(1, [[1, 2], [3, 0]])],
        ("WFDU", "utilization_ascending"): [(1, [[2, 0], [1, 3]])],
        ("WFDU", "utilization_descending"): [(1, [[0, 1], [3, 2]])],
        ("WFDU", "execution_slack_ascending"): [(1, [[0, 1], [2, 3]])],
        ("WFDU", "execution_slack_descending"): [(1, [[1, 2], [3, 0]])],
        ("WFDU", "random_order"): [(1, [[1, 0], [3, 2]])],
        ("CITTA", "wcet_ascending"): [(1, [[0, 2], [1, 3]])],
        ("CITTA", "wcet_descending"): [(1, [[1, 3, 2], [0]])],
        ("CITTA", "period_ascending"): [(1, [[0, 2], [3, 1]])],
        ("CITTA", "period_descending"): [(1, [[1, 3, 2], [0]])],
        ("CITTA", "utilization_ascending"): [(1, [[2, 1, 3], [0]])],
        ("CITTA", "utilization_descending"): [(1, [[0, 3], [1, 2]])],
        ("CITTA", "execution_slack_ascending"): [(1, [[0, 2], [3, 1]])],
        ("CITTA", "execution_slack_descending"): [(1, [[1, 3, 2], [0]])],
        ("CITTA", "random_order"): [(1, [[1, 3, 2], [0]])],
        "Wmin": [(1, [[0], [1, 2, 3]])]
    }
    return expected_assignment[assignment_method]


def prepare_input_data_generate_1(assignment_method, sorting_criterion=""):
    taskset_action = "generate"
    taskset_id = "taskset_generate_1"
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
        "sorting_criterion": [sorting_criterion],
        "assignment_method": [assignment_method],
        "number_of_cores": 2,
        "assignment_options": {}
    }
    return taskset_action, taskset_id, taskset_parameters, assignment_parameters


def create_expected_assignment_output_generate_1(assignment_method, sorting_criterion):
    if assignment_method in assignment_methods_with_criteria:
        assignment_method = (assignment_method, sorting_criterion)
    expected_assignment = {
        ("BFDU", "wcet_ascending"): [(1, [[0, 2, 1, 3], []])],
        ("BFDU", "wcet_descending"): [(1, [[3, 1, 0, 2], []])],
        ("BFDU", "period_ascending"): [(1, [[2, 0, 1, 3], []])],
        ("BFDU", "period_descending"): [(1, [[3, 0, 1, 2], []])],
        ("BFDU", "utilization_ascending"): [(1, [[0, 1, 3, 2], []])],
        ("BFDU", "utilization_descending"): [(1, [[2, 3, 1, 0], []])],
        ("BFDU", "execution_slack_ascending"): [(1, [[2, 1, 0, 3], []])],
        ("BFDU", "execution_slack_descending"): [(1, [[3, 0, 1, 2], []])],
        ("BFDU", "random_order"): [(1, [[3, 2, 0, 1], []])],
        ("FFDU", "wcet_ascending"): [(1, [[0, 2, 1, 3], []])],
        ("FFDU", "wcet_descending"): [(1, [[3, 1, 0, 2], []])],
        ("FFDU", "period_ascending"): [(1, [[2, 0, 1, 3], []])],
        ("FFDU", "period_descending"): [(1, [[3, 0, 1, 2], []])],
        ("FFDU", "utilization_ascending"): [(1, [[0, 1, 3, 2], []])],
        ("FFDU", "utilization_descending"): [(1, [[2, 3, 1, 0], []])],
        ("FFDU", "execution_slack_ascending"): [(1, [[2, 1, 0, 3], []])],
        ("FFDU", "execution_slack_descending"): [(1, [[3, 0, 1, 2], []])],
        ("FFDU", "random_order"): [(1, [[3, 2, 0, 1], []])],
        ("WFDU", "wcet_ascending"): [(1, [[0, 1, 3], [2]])],
        ("WFDU", "wcet_descending"): [(1, [[3], [1, 0, 2]])],
        ("WFDU", "period_ascending"): [(1, [[2], [0, 1, 3]])],
        ("WFDU", "period_descending"): [(1, [[3], [0, 1, 2]])],
        ("WFDU", "utilization_ascending"): [(1, [[0, 3], [1, 2]])],
        ("WFDU", "utilization_descending"): [(1, [[2, 0], [3, 1]])],
        ("WFDU", "execution_slack_ascending"): [(1, [[2], [1, 0, 3]])],
        ("WFDU", "execution_slack_descending"): [(1, [[3], [0, 1, 2]])],
        ("WFDU", "random_order"): [(1, [[3, 0, 1], [2]])],
        ("CITTA", "wcet_ascending"): [(1, [[0, 2, 1], [3]])],
        ("CITTA", "wcet_descending"): [(1, [[3], [1, 0, 2]])],
        ("CITTA", "period_ascending"): [(1, [[2, 0, 1], [3]])],
        ("CITTA", "period_descending"): [(1, [[3], [0, 1, 2]])],
        ("CITTA", "utilization_ascending"): [(1, [[0, 1, 2], [3]])],
        ("CITTA", "utilization_descending"): [(1, [[2, 1, 0], [3]])],
        ("CITTA", "execution_slack_ascending"): [(1, [[2, 1, 0], [3]])],
        ("CITTA", "execution_slack_descending"): [(1, [[3], [0, 1, 2]])],
        ("CITTA", "random_order"): [(1, [[3], [2, 0, 1]])],
        "Wmin": [(1, [[], [0, 1, 2, 3]])]
    }
    return expected_assignment[assignment_method]


def prepare_input_data(experience, assignment_method, sorting_criterion=""):
    if experience == "manual_1":
        return prepare_input_data_manual_1(assignment_method=assignment_method, sorting_criterion=sorting_criterion)
    elif experience == "generate_1":
        return prepare_input_data_generate_1(assignment_method=assignment_method, sorting_criterion=sorting_criterion)


def prepare_output_data(experience, assignment_method, sorting_criterion=""):
    if experience == "manual_1":
        return create_expected_assignment_output_manual_1(assignment_method=assignment_method, sorting_criterion=sorting_criterion)
    elif experience == "generate_1":
        return create_expected_assignment_output_generate_1(assignment_method=assignment_method, sorting_criterion=sorting_criterion)


def create_taskset_manual(taskset_id, taskset_parameters):
    generator = TasksetSetManual(taskset_id, **taskset_parameters)
    return generator.create_taskset_set()


def create_taskset_generate(taskset_id, taskset_parameters):
    generator = TasksetSetGenerator(taskset_id, **taskset_parameters)
    return generator.generate_taskset_set()


def create_assignment(taskset, assignment_parameters):
    if assignment_parameters["assignment_method"][0].lower() == 'wmin':
        taskset = shape_interference(taskset)
    generator = AssignmentGenerator(
        taskset_set_obj=taskset,
        taskset_id=assignment_parameters["taskset_id"],
        assignment_id=assignment_parameters["assignment_id"],
        assignment_method=assignment_parameters["assignment_method"],
        sorting_criterion=assignment_parameters["sorting_criterion"],
        number_of_cores=assignment_parameters["number_of_cores"],
        assignment_options=assignment_parameters["assignment_options"]
    )
    assignment = generator.generate_assignment_set()
    return assignment


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


def verify_assignment(assignment, expected_assignment):
    for result, exp_ass in zip(assignment, expected_assignment):
        assert result.success == exp_ass[0]
        assert result.assignment == exp_ass[1]


@pytest.fixture(autouse=True)
def reset_random_seed():
    np.random.seed(42)
    random.seed(42)

# Générer les combinaisons de paramètres nécessaires


def generate_param_combinations():
    combinations = []
    for method in assignment_methods_without_criteria:
        for experience in experiences:
            combinations.append((method, "", experience))
    for method in assignment_methods_with_criteria:
        for criteria in sorting_criterion_list:
            for experience in experiences:
                combinations.append((method, criteria, experience))
    return combinations

# Paramétrage des tests avec pytest.mark.parametrize


@pytest.mark.parametrize("assignment_method,sorting_criterion,experience", generate_param_combinations(), ids=lambda val: f"{val}")
def test_assignment(assignment_method, sorting_criterion, experience):
    input_data = prepare_input_data(
        experience, assignment_method, sorting_criterion)
    taskset_action, taskset_id, taskset_parameters, assignment_parameters = input_data
    expected_assignment = prepare_output_data(
        experience=experience, assignment_method=assignment_method, sorting_criterion=sorting_criterion)

    if taskset_action == "manual":
        taskset = create_taskset_manual(taskset_id, taskset_parameters)
    elif taskset_action == "generate":
        taskset = create_taskset_generate(taskset_id, taskset_parameters)
    else:
        raise ValueError("Invalid parameter")
    assignment = create_assignment(taskset, assignment_parameters)
    verify_assignment(assignment, expected_assignment)
