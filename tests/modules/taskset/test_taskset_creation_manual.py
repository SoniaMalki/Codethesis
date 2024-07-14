import numpy as np
import pytest
from modules.taskset.taskset_set_manual import TasksetSetManual

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


def expected_taskset_structure():
    """Prepare and return expected Taskset structure for the test."""
    return {
        'taskset_number': 0,
        'wcet': np.array([1, 3]),
        'deadline': np.array([4, 5]),
        'period': np.array([4, 5]),
        'interference': np.array([[0, 1], [1, 0]]),
        'utilization': np.array([0.3333, 0.3]),
        'hyperperiod': 20,
        'N': np.array([5, 4]),
        'activation': [np.array([1, 2, 3, 4, 5]), np.array([1, 2, 3, 4])]
    }


def expected_task_structure():
    """Prepare and return expected Task structures for the test."""
    return [
        {'task_number': 0, 'wcet': 1, 'deadline': 4, 'period': 4, 'interference': [
            0, 1], 'utilization': 0.3333, 'absolute_deadline': {1: 5, 2: 9, 3: 13, 4: 17, 5: 21}},
        {'task_number': 1, 'wcet': 3, 'deadline': 5, 'period': 5,
            'interference': [1, 0], 'utilization': 0.3, 'absolute_deadline': {1: 6, 2: 11, 3: 16, 4: 21}}
    ]


def create_taskset(data):
    """Create and return a Taskset object using provided data."""
    taskset_manual = TasksetSetManual(
        data['taskset_id'], data['wcet_list'], data['deadline_list'],
        data['period_list'], data['interference_list'], data['utilization_list']
    )
    taskset_set = taskset_manual.create_taskset_set()
    return taskset_set.taskset_list[0]  # Assuming only one taskset is created


def verify_taskset_attributes(taskset, expected):
    """Verify all expected attributes of the Taskset object."""
    assert taskset.taskset_number == expected['taskset_number']
    assert np.array_equal(taskset.wcet, expected['wcet'])
    assert np.array_equal(taskset.deadline, expected['deadline'])
    assert np.array_equal(taskset.period, expected['period'])
    assert np.array_equal(taskset.interference, expected['interference'])
    assert np.allclose(taskset.utilization,
                       expected['utilization'], rtol=1e-04)
    assert taskset.hyperperiod == expected['hyperperiod']
    assert np.array_equal(taskset.N, expected['N'])
    assert all(np.array_equal(a, b)
               for a, b in zip(taskset.activation, expected['activation']))


def verify_task_attributes(taskset, expected_tasks):
    """Verify all expected attributes for each Task in the Taskset."""
    for task, exp_task in zip(taskset.task_list, expected_tasks):

        assert task.task_number == exp_task['task_number']
        assert task.wcet == exp_task['wcet']
        assert task.deadline == exp_task['deadline']
        assert task.period == exp_task['period']
        assert task.interference == exp_task['interference']
        assert np.isclose(task.utilization,
                          exp_task['utilization'], rtol=1e-04)
        assert task.absolute_deadline == exp_task['absolute_deadline']


@pytest.mark.parametrize("input_data, expected_ts, expected_tasks", [
    (prepare_input_data(), expected_taskset_structure(), expected_task_structure())
])
def test_taskset_creation(input_data, expected_ts, expected_tasks):
    """Main test function to test taskset creation and attribute validation."""
    taskset = create_taskset(input_data)
    verify_taskset_attributes(taskset, expected_ts)
    verify_task_attributes(taskset, expected_tasks)


