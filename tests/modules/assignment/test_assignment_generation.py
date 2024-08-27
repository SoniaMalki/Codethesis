from pathlib import Path
import random
import numpy as np
import pytest
from modules.assignment.assignment_algorithms import citta
from modules.assignment.assignment_set import AssignmentSet
from modules.assignment.assignment_generator import AssignmentGenerator
from modules.assignment.assignment_loader_saver import AssignmentLoaderSaver
from modules.taskset.task_parameters_generator.prime_matrix_generator import PrimeMatrixGenerator
from modules.taskset.taskset_set_generator import TasksetSetGenerator
from modules.taskset.taskset_set_manual import TasksetSetManual

import tempfile


@pytest.fixture(scope="function", autouse=True)
def use_temporary_prime_matrix_path():
    global prime_path
    with tempfile.TemporaryDirectory() as temp_dir:
        prime_path = Path(temp_dir)
        yield


np.random.seed(42)
random.seed(42)

assignment_methods_with_criteria = [
    "Citta", "BestFitAssigner", "FirstFitAssigner", "WorstFitAssigner"]
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
        "sorting_criterion": sorting_criterion,
        "assignment_method": assignment_method,
        "number_of_cores": 2,
        "assignment_options": {
            "solving_time_limit_MILP": 10
        }
    }
    return taskset_action, taskset_id, taskset_parameters, assignment_parameters


def create_expected_assignment_output_manual_1(assignment_method, sorting_criterion):
    if assignment_method in assignment_methods_with_criteria:
        assignment_method = (assignment_method, sorting_criterion)
    expected_assignment = {
        ("BestFitAssigner", "wcet_ascending"): [(1, [[0, 2, 1], [3]])],
        ("BestFitAssigner", "wcet_descending"): [(1, [[1, 3, 0], [2]])],
        ("BestFitAssigner", "period_ascending"): [(1, [[0, 2, 3], [1]])],
        ("BestFitAssigner", "period_descending"): [(1, [[1, 3, 2], [0]])],
        ("BestFitAssigner", "utilization_ascending"): [(1, [[2, 1, 0], [3]])],
        ("BestFitAssigner", "utilization_descending"): [(1, [[0, 3, 1], [2]])],
        ("BestFitAssigner", "execution_slack_ascending"): [(1, [[0, 2, 3], [1]])],
        ("BestFitAssigner", "execution_slack_descending"): [(1, [[1, 3, 2], [0]])],
        ("BestFitAssigner", "random_order"): [(1, [[1, 3, 0], [2]])],
        ("FirstFitAssigner", "wcet_ascending"): [(1, [[0, 2, 1], [3]])],
        ("FirstFitAssigner", "wcet_descending"): [(1, [[1, 3, 0], [2]])],
        ("FirstFitAssigner", "period_ascending"): [(1, [[0, 2, 3], [1]])],
        ("FirstFitAssigner", "period_descending"): [(1, [[1, 3, 2], [0]])],
        ("FirstFitAssigner", "utilization_ascending"): [(1, [[2, 1, 0], [3]])],
        ("FirstFitAssigner", "utilization_descending"): [(1, [[0, 3, 1], [2]])],
        ("FirstFitAssigner", "execution_slack_ascending"): [(1, [[0, 2, 3], [1]])],
        ("FirstFitAssigner", "execution_slack_descending"): [(1, [[1, 3, 2], [0]])],
        ("FirstFitAssigner", "random_order"): [(1, [[1, 3, 0], [2]])],
        ("WorstFitAssigner", "wcet_ascending"): [(1, [[0, 3], [2, 1]])],
        ("WorstFitAssigner", "wcet_descending"): [(1, [[1, 0], [3, 2]])],
        ("WorstFitAssigner", "period_ascending"): [(1, [[0, 1], [2, 3]])],
        ("WorstFitAssigner", "period_descending"): [(1, [[1, 2], [3, 0]])],
        ("WorstFitAssigner", "utilization_ascending"): [(1, [[2, 0], [1, 3]])],
        ("WorstFitAssigner", "utilization_descending"): [(1, [[0, 1], [3, 2]])],
        ("WorstFitAssigner", "execution_slack_ascending"): [(1, [[0, 1], [2, 3]])],
        ("WorstFitAssigner", "execution_slack_descending"): [(1, [[1, 2], [3, 0]])],
        ("WorstFitAssigner", "random_order"): [(1, [[1, 0], [3, 2]])],
        ("Citta", "wcet_ascending"): [(1, [[0, 2], [1, 3]])],
        ("Citta", "wcet_descending"): [(1, [[1, 3, 2], [0]])],
        ("Citta", "period_ascending"): [(1, [[0, 2], [3, 1]])],
        ("Citta", "period_descending"): [(1, [[1, 3, 2], [0]])],
        ("Citta", "utilization_ascending"): [(1, [[2, 1, 3], [0]])],
        ("Citta", "utilization_descending"): [(1, [[0, 3], [1, 2]])],
        ("Citta", "execution_slack_ascending"): [(1, [[0, 2], [3, 1]])],
        ("Citta", "execution_slack_descending"): [(1, [[1, 3, 2], [0]])],
        ("Citta", "random_order"): [(1, [[1, 3, 2], [0]])],
        "Wmin": [(1, [[0], [1, 2, 3]])]
    }
    return expected_assignment[assignment_method]


def prepare_input_data_generate_1(assignment_method, sorting_criterion=""):
    taskset_action = "generate"
    taskset_id = "taskset_generate_1"
    taskset_parameters = {
        "taskset_repetition": 1,
        "probability_factor": 0.1,
        "max_utilization": 0.2,
        "tasks_per_taskset": 4,
        "interference_factor": 0.2,
        "taskset_options": {
            "deadline_option": "leq_period",
            "max_hyperperiod": 100000,
            "max_prime": 20,
            "gen_limit_exponent": 2
        }
    }
    assignment_parameters = {
        "assignment_id": "assignment_generate_1",
        "taskset_id": "taskset_generate_1",
        "sorting_criterion": sorting_criterion,
        "assignment_method": assignment_method,
        "number_of_cores": 2,
        "assignment_options": {
            "solving_time_limit_MILP": 10
        }
    }
    return taskset_action, taskset_id, taskset_parameters, assignment_parameters


def create_expected_assignment_output_generate_1(assignment_method, sorting_criterion):
    if assignment_method in assignment_methods_with_criteria:
        assignment_method = (assignment_method, sorting_criterion)
    expected_assignment = {
        ("BestFitAssigner", "wcet_ascending"): [(1, [[0, 2, 1, 3], []])],
        ("BestFitAssigner", "wcet_descending"): [(1, [[3, 1, 2, 0], []])],
        ("BestFitAssigner", "period_ascending"): [(1, [[0, 2, 1, 3], []])],
        ("BestFitAssigner", "period_descending"): [(1, [[1, 3, 0, 2], []])],
        ("BestFitAssigner", "utilization_ascending"): [(1, [[0, 1, 3, 2], []])],
        ("BestFitAssigner", "utilization_descending"): [(1, [[2, 3, 1, 0], []])],
        ("BestFitAssigner", "execution_slack_ascending"): [(1, [[2, 0, 3, 1], []])],
        ("BestFitAssigner", "execution_slack_descending"): [(1, [[1, 3, 0, 2], []])],
        ("BestFitAssigner", "random_order"): [(1, [[3, 2, 0, 1], []])],
        ("FirstFitAssigner", "wcet_ascending"): [(1, [[0, 2, 1, 3], []])],
        ("FirstFitAssigner", "wcet_descending"): [(1, [[3, 1, 2, 0], []])],
        ("FirstFitAssigner", "period_ascending"): [(1, [[0, 2, 1, 3], []])],
        ("FirstFitAssigner", "period_descending"): [(1, [[1, 3, 0, 2], []])],
        ("FirstFitAssigner", "utilization_ascending"): [(1, [[0, 1, 3, 2], []])],
        ("FirstFitAssigner", "utilization_descending"): [(1, [[2, 3, 1, 0], []])],
        ("FirstFitAssigner", "execution_slack_ascending"): [(1, [[2, 0, 3, 1], []])],
        ("FirstFitAssigner", "execution_slack_descending"): [(1, [[1, 3, 0, 2], []])],
        ("FirstFitAssigner", "random_order"): [(1, [[3, 2, 0, 1], []])],
        ("WorstFitAssigner", "wcet_ascending"): [(1, [[0, 1, 3], [2]])],
        ("WorstFitAssigner", "wcet_descending"): [(1, [[3, 0], [1, 2]])],
        ("WorstFitAssigner", "period_ascending"): [(1, [[0, 1, 3], [2]])],
        ("WorstFitAssigner", "period_descending"): [(1, [[1, 0, 2], [3]])],
        ("WorstFitAssigner", "utilization_ascending"): [(1, [[0, 3], [1, 2]])],
        ("WorstFitAssigner", "utilization_descending"): [(1, [[2, 0], [3, 1]])],
        ("WorstFitAssigner", "execution_slack_ascending"): [(1, [[2], [0, 3, 1]])],
        ("WorstFitAssigner", "execution_slack_descending"): [(1, [[1, 0, 2], [3]])],
        ("WorstFitAssigner", "random_order"): [(1, [[3, 0, 1], [2]])],
        ("Citta", "wcet_ascending"): [(1, [[0, 2, 1, 3], []])],
        ("Citta", "wcet_descending"): [(1, [[3, 1, 2, 0], []])],
        ("Citta", "period_ascending"): [(1, [[0, 2, 1, 3], []])],
        ("Citta", "period_descending"): [(1, [[1, 3, 0, 2], []])],
        ("Citta", "utilization_ascending"): [(1, [[0, 1, 3, 2], []])],
        ("Citta", "utilization_descending"): [(1, [[2, 3, 1, 0], []])],
        ("Citta", "execution_slack_ascending"): [(1, [[2, 0, 3, 1], []])],
        ("Citta", "execution_slack_descending"): [(1, [[1, 3, 0, 2], []])],
        ("Citta", "random_order"): [(1, [[3, 2, 0, 1], []])],
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
    max_hyperperiod = taskset_parameters["taskset_options"]["max_hyperperiod"]
    max_prime = taskset_parameters["taskset_options"]["max_prime"]
    gen_limit_exponent = taskset_parameters["taskset_options"]["gen_limit_exponent"]
    PrimeMatrixGenerator(
        main_path=prime_path, max_hyperperiod=max_hyperperiod, max_prime=max_prime, gen_limit_exponent=gen_limit_exponent)
    generator = TasksetSetGenerator(
        prime_path, taskset_id, **taskset_parameters)
    return generator.generate_taskset_set()


def create_assignment(taskset, assignment_parameters):
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
