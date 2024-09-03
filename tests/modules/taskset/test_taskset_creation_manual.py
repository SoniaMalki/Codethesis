import numpy as np
import pytest
from modules.taskset.task import Task
from modules.taskset.taskset_set_manual import TasksetSetManual

# Test N1


def prepare_input_data():
    """Prepare and return input data for the test."""
    return {
        "taskset_id": "taskset_manual_test",
        "wcet_list": [1, 3],
        "deadline_list": [4, 5],
        "period_list": [4, 5],
        "interference_list": [[0, 1], [1, 0]],
        "utilization_list": [0.3333, 0.3]
    }


def expected_taskset_set_structure():
    """Prepare and return expected TasksetSet structure for the test."""
    return {
        'taskset_id': 'taskset_manual_test',
        'wcet': np.array([1, 3]),
        'deadline': np.array([4, 5]),
        'period': np.array([4, 5]),
        'interference': np.array([[0, 1], [1, 0]]),
        'utilization': np.array([0.3333, 0.3])
    }


def expected_taskset_structure():
    """Prepare and return expected Taskset structure for the test."""
    return [{
        'taskset_number': 0,
        'wcet': np.array([1, 3]),
        'deadline': np.array([4, 5]),
        'period': np.array([4, 5]),
        'interference': np.array([[0, 1], [1, 0]]),
        'utilization': np.array([0.3333, 0.3]),
        'hyperperiod': 20,
        'N': np.array([5, 4]),
        'activation': [np.array([1, 2, 3, 4, 5]), np.array([1, 2, 3, 4])],
        'absolute_deadline': [{1: 5, 2: 9, 3: 13, 4: 17, 5: 21}, {1: 6, 2: 11, 3: 16, 4: 21}],
    }]


def expected_task_structure():
    """Prepare and return expected Task structures for the test."""
    return [
        {'task_number': 0, 'wcet': 1, 'deadline': 4, 'period': 4, 'interference': [
            0, 1], 'utilization': 0.3333, 'absolute_deadline': {1: 5, 2: 9, 3: 13, 4: 17, 5: 21}},
        {'task_number': 1, 'wcet': 3, 'deadline': 5, 'period': 5,
            'interference': [1, 0], 'utilization': 0.3, 'absolute_deadline': {1: 6, 2: 11, 3: 16, 4: 21}}
    ]

# Test N2


def prepare_input_data2():
    """Prepare and return a second set of input data for the test."""
    return {
        "taskset_id": "taskset_manual_test_2",
        "wcet_list": [2, 4],
        "deadline_list": [6, 8],
        "period_list": [6, 8],
        "interference_list": [[0, 2], [2, 0]],
        "utilization_list": [0.25, 0.4]
    }


def expected_taskset_set_structure2():
    """Prepare and return a second expected TasksetSet structure for the test."""
    return {
        'taskset_id': 'taskset_manual_test_2',
        'wcet': np.array([2, 4]),
        'deadline': np.array([6, 8]),
        'period': np.array([6, 8]),
        'interference': np.array([[0, 2], [2, 0]]),
        'utilization': np.array([0.25, 0.4])
    }


def expected_taskset_structure2():
    """Prepare and return a second expected Taskset structure for the test."""
    return [{
        'taskset_number': 0,
        'wcet': np.array([2, 4]),
        'deadline': np.array([6, 8]),
        'period': np.array([6, 8]),
        'interference': np.array([[0, 2], [2, 0]]),
        'utilization': np.array([0.25, 0.4]),
        'hyperperiod': 24,
        'N': np.array([4, 3]),
        'activation': [np.array([1, 2, 3, 4]), np.array([1, 2, 3])],
        'absolute_deadline': [{1: 7, 2: 13, 3: 19, 4: 25}, {1: 9, 2: 17, 3: 25}]
    }]


def expected_task_structure2():
    """Prepare and return a second set of expected Task structures for the test."""
    return [
        {'task_number': 0, 'wcet': 2, 'deadline': 6, 'period': 6, 'interference': [
            0, 2], 'utilization': 0.25, 'absolute_deadline': {1: 7, 2: 13, 3: 19, 4: 25}},
        {'task_number': 1, 'wcet': 4, 'deadline': 8, 'period': 8, 'interference': [
            2, 0], 'utilization': 0.4, 'absolute_deadline': {1: 9, 2: 17, 3: 25}}
    ]


# Test creation
def create_taskset(data):
    """Create and return a Taskset object using provided data."""
    taskset_manual = TasksetSetManual(
        data['taskset_id'], data['wcet_list'], data['deadline_list'],
        data['period_list'], data['interference_list'], data['utilization_list']
    )
    taskset_set = taskset_manual.create_taskset_set()
    return taskset_set


def verify_taskset_set_attributes(taskset_set, expected_taskset_set):
    """Verify all expected attributes of the TasksetSet object."""
    assert taskset_set.taskset_id == expected_taskset_set['taskset_id']
    assert np.array_equal(taskset_set.wcet, expected_taskset_set['wcet'])
    assert np.array_equal(taskset_set.deadline,
                          expected_taskset_set['deadline'])
    assert np.array_equal(taskset_set.period, expected_taskset_set['period'])
    assert np.array_equal(taskset_set.interference,
                          expected_taskset_set['interference'])
    assert np.allclose(taskset_set.utilization,
                       expected_taskset_set['utilization'], rtol=1e-04)


def verify_taskset_attributes(taskset_set, expected_taskset):
    """Verify all expected attributes of the Taskset object."""
    for taskset, exp_taskset in zip(taskset_set.taskset_list, expected_taskset):
        assert taskset.taskset_number == exp_taskset['taskset_number']
        assert np.array_equal(taskset.wcet, exp_taskset['wcet'])
        assert np.array_equal(taskset.deadline, exp_taskset['deadline'])
        assert np.array_equal(taskset.period, exp_taskset['period'])
        assert np.array_equal(taskset.interference,
                              exp_taskset['interference'])
        assert np.allclose(taskset.utilization,
                           exp_taskset['utilization'], rtol=1e-04)
        assert taskset.hyperperiod == exp_taskset['hyperperiod']
        assert np.array_equal(taskset.N, exp_taskset['N'])
        assert all(np.array_equal(a, b)
                   for a, b in zip(taskset.activation, exp_taskset['activation']))
        assert all(np.array_equal(a, b)
                   for a, b in zip(taskset.absolute_deadline, exp_taskset['absolute_deadline']))


def verify_task_attributes(taskset_set, expected_tasks):
    """Verify all expected attributes for each Task in the Taskset."""
    for taskset in taskset_set.taskset_list:
        for task, exp_task in zip(taskset.task_list, expected_tasks):
            assert task.task_number == exp_task['task_number']
            assert np.array_equal(task.wcet, exp_task['wcet'])
            assert np.array_equal(task.deadline, exp_task['deadline'])
            assert np.array_equal(task.period, exp_task['period'])
            assert np.array_equal(task.interference, exp_task['interference'])
            assert np.isclose(task.utilization,
                              exp_task['utilization'], rtol=1e-04)
            assert task.absolute_deadline == exp_task['absolute_deadline']


@pytest.mark.parametrize("input_data, expected_taskset_set, expected_taskset, expected_tasks", [
    (prepare_input_data(), expected_taskset_set_structure(),
     expected_taskset_structure(), expected_task_structure()),
    (prepare_input_data2(), expected_taskset_set_structure2(),
     expected_taskset_structure2(), expected_task_structure2())
])
def test_taskset_creation(input_data, expected_taskset_set, expected_taskset, expected_tasks):
    """Main test function to test taskset creation and attribute validation."""
    taskset_set = create_taskset(input_data)
    verify_taskset_set_attributes(taskset_set, expected_taskset_set)
    verify_taskset_attributes(taskset_set, expected_taskset)
    verify_task_attributes(taskset_set, expected_tasks)
