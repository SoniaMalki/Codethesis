import random
import numpy as np
import pytest
from modules.assignment.assignment_algorithms import citta
from modules.assignment.assignment_set import AssignmentSet
from modules.assignment.assignment_generator import AssignmentGenerator
from modules.assignment.assignment_loader_saver import AssignmentLoaderSaver
from modules.taskset.taskset_set_generator import TasksetSetGenerator
from modules.taskset.taskset_set_manual import TasksetSetManual
# Configuration initiale des tests

random.seed(42)
np.random.seed(42)

# Taskset 1


def prepare_input_data_manual_1(assignment_method, citta_criteria=""):
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
        "citta_criteria": [citta_criteria],
        "assignment_method": [assignment_method],
        "number_of_cores": 2
    }
    return taskset_action, taskset_id, taskset_parameters, assignment_parameters


def create_expected_assignment_output_manual_1(assignment_method):
    expected_assignment = {
        "WFDU": [(1, [[0, 1], [3, 2]])],
        "FFDU": [(1, [[0, 3, 1], [2]])],
        "BFDU": [(1, [[0, 3, 1], [2]])],
        "CITTA": [(1, [[0, 3], [1, 2]])],
        "Wmin": [(1, [[0], [1, 2, 3]])]
    }

    return expected_assignment[assignment_method]


def prepare_input_data_generate_1(assignment_method, citta_critera=""):
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
        "citta_criteria": [citta_critera],
        "assignment_method": [assignment_method],
        "number_of_cores": 2
    }
    return taskset_action, taskset_id, taskset_parameters, assignment_parameters


def create_expected_assignment_output_generate_1(assignment_method):
    expected_assignment = {
        "WFDU": [(1, [[2, 0], [3, 1]])],
        "FFDU": [(1, [[2, 3, 1, 0], []])],
        "BFDU": [(1, [[2, 3, 1, 0], []])],
        "CITTA": [(1, [[2, 1, 0], [3]])],
        "Wmin": [(1, [[], [0, 1, 2, 3]])]
    }

    return expected_assignment[assignment_method]


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
        citta_criteria=assignment_parameters["citta_criteria"],
        number_of_cores=assignment_parameters["number_of_cores"]
    )
    assignment = generator.generate_assignment_set()
    return assignment


def shape_interference(taskset_set_obj):
    new_interference = []
    for taskset in taskset_set_obj:
        taskset_interference = np.max(taskset.interference, axis=1)
        # Modif au niveau Taskset Set
        new_interference.append(taskset_interference)
        taskset.interference = taskset_interference  # Modif au niveau Taskset
        for task_index, task in enumerate(taskset):
            # Modif au niveau Task
            task.interference = taskset_interference[task_index]

    taskset_set_obj.interference = np.array(new_interference)
    return taskset_set_obj


def verify_assignment(assignment, expected_assignment):
    for result, exp_ass in zip(assignment, expected_assignment):
        # Vérification des résultats
        assert result.success == exp_ass[0]
        assert result.assignment == exp_ass[1]


@ pytest.mark.parametrize("input_data, expected_assigment", [
    (prepare_input_data_manual_1("WFDU"),
     create_expected_assignment_output_manual_1("WFDU")),
    (prepare_input_data_manual_1("FFDU"),
     create_expected_assignment_output_manual_1("FFDU")),
    (prepare_input_data_manual_1("BFDU"),
     create_expected_assignment_output_manual_1("BFDU")),
    (prepare_input_data_manual_1("CITTA", "utilization_descending"),
     create_expected_assignment_output_manual_1("CITTA")),
    (prepare_input_data_manual_1("Wmin"),
     create_expected_assignment_output_manual_1("Wmin")),
    (prepare_input_data_generate_1("WFDU"),
     create_expected_assignment_output_generate_1("WFDU")),
    (prepare_input_data_generate_1("FFDU"),
     create_expected_assignment_output_generate_1("FFDU")),
    (prepare_input_data_generate_1("BFDU"),
     create_expected_assignment_output_generate_1("BFDU")),
    (prepare_input_data_generate_1("CITTA", "utilization_descending"),
     create_expected_assignment_output_generate_1("CITTA")),
    (prepare_input_data_generate_1("Wmin"),
     create_expected_assignment_output_generate_1("Wmin"))
])
def test_assignment(input_data, expected_assigment):
    taskset_action, taskset_id, taskset_parameters, assignment_parameters = input_data
    if taskset_action == "manual":
        taskset = create_taskset_manual(taskset_id, taskset_parameters)
    elif taskset_action == "generate":
        taskset = create_taskset_generate(taskset_id, taskset_parameters)
    else:
        print("Invalid parameter")
    assignment = create_assignment(taskset, assignment_parameters)
    verify_assignment(assignment, expected_assigment)
