import numpy as np
import pytest
from modules.assignment.assignment_set import AssignmentSet
from modules.assignment.assignment_generator import AssignmentGenerator
from modules.assignment.assignment_loader_saver import AssignmentLoaderSaver
from modules.taskset.taskset_set_generator import TasksetSetGenerator
from modules.taskset.taskset_set_manual import TasksetSetManual
# Configuration initiale des tests


def prepare_input_data_1(assignment_method):
    taskset_parameters = {
        "taskset_id": "taskset_17",
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
        "assignment_id": "assignment_17",
        "taskset_id": "taskset_17",
        "citta_criteria": ["utilization_descending"],
        "assignment_method": [assignment_method],
        "number_of_cores": 2
    }
    return taskset_parameters, assignment_parameters


def create_expected_assignment_input_1_wfdu():
    return [(1, [[0, 1], [3, 2]])]


def create_expected_assignment_input_1_ffdu():
    return [(1, [[0, 3, 1], [2]])]


def create_expected_assignment_input_1_bfdu():
    return [(1, [[0, 3, 1], [2]])]


def create_expected_assignment_input_1_citta():
    return [(1, [[0, 3], [1, 2]])]


def create_expected_assignment_input_1_wmin():
    return [(1, [[0], [1, 2, 3]])]


def create_taskset(taskset_parameters):
    generator = TasksetSetManual(**taskset_parameters)
    return generator.create_taskset_set()


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


@pytest.mark.parametrize("input_data, expected_assigment", [
    (prepare_input_data_1("WFDU"), create_expected_assignment_input_1_wfdu()),
    (prepare_input_data_1("FFDU"), create_expected_assignment_input_1_ffdu()),
    (prepare_input_data_1("BFDU"), create_expected_assignment_input_1_bfdu()),
    (prepare_input_data_1("CITTA"), create_expected_assignment_input_1_citta()),
    (prepare_input_data_1("Wmin"), create_expected_assignment_input_1_wmin())
])
def test_assignment(input_data, expected_assigment):
    taskset_parameters, assignment_parameters = input_data
    taskset = create_taskset(taskset_parameters)
    assignment = create_assignment(taskset, assignment_parameters)
    verify_assignment(assignment, expected_assigment)
