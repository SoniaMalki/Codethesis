import tempfile
from pathlib import Path
import numpy as np
import pytest
import random
from modules.taskset.task_parameters_generator.prime_matrix_generator import PrimeMatrixGenerator
from modules.taskset.taskset_set_generator import TasksetSetGenerator
np.random.seed(42)
random.seed(42)


@pytest.fixture(scope="function", autouse=True)
def use_temporary_prime_matrix_path():
    global prime_path
    global result_path
    with tempfile.TemporaryDirectory() as temp_dir:
        prime_path = Path(temp_dir)
        result_path = prime_path / "results"
        yield


def prepare_input_data():
    """Prepare and return input data for the test."""
    return {
        "taskset_id": "taskset_generate_test",
        "taskset_repetition": 1,
        "probability_factor": 0.1,
        "max_utilization": 0.2,
        "tasks_per_taskset": 2,
        "interference_factor": 0.2,
        "taskset_options": {
            "deadline_option": "leq_period",
            "max_hyperperiod": 100000,
            "max_prime": 20,
            "gen_limit_exponent": 2
        }
    }


def expected_taskset_set_structure():
    """Prepare and return expected TasksetSet structure for the test."""
    return {
        'taskset_id': "taskset_generate_test",
        'wcet': np.array([[263.,  53.]]),
        'deadline': np.array([[681, 6551]]),
        'period': np.array([[1350, 10800]]),
        'interference': np.array([[[0., 0.],
                                   [0., 0.]]]),
        'utilization': np.array([[0.19507143, 0.00492857]])
    }


def expected_taskset_structure():
    """Prepare and return expected Taskset structure for the test."""
    return [{
        'taskset_number': 0,
        'wcet': np.array([263.,  53.]),
        'deadline': np.array([681, 6551]),
        'period': np.array([1350, 10800]),
        'interference': np.array([[0., 0.],
                                  [0., 0.]]),
        'utilization': np.array([0.19507143, 0.00492857]),
        'hyperperiod': np.int64(10800),
        'N': np.array([8., 1.]),
        'activation': [[1, 2, 3, 4, 5, 6, 7, 8], [1]],
        'absolute_deadline': [{1: np.int64(682), 2: np.int64(2032), 3: np.int64(3382), 4: np.int64(4732), 5: np.int64(6082), 6: np.int64(7432), 7: np.int64(8782), 8: np.int64(10132)}, {1: np.int64(6552)}],

    }]


def expected_task_structure():
    """Prepare and return expected Task structures for the test."""
    return [
        {'task_number': 0, 'wcet': np.float64(263.0), 'deadline': np.int64(681), 'period': np.int64(
            1350), 'interference': np.array([0., 0.]), 'utilization': np.float64(0.1950714306409916), 'absolute_deadline': {1: np.int64(682), 2: np.int64(2032), 3: np.int64(3382), 4: np.int64(4732), 5: np.int64(6082), 6: np.int64(7432), 7: np.int64(8782), 8: np.int64(10132)}},
        {'task_number': 1, 'wcet': np.float64(53.0), 'deadline': np.int64(6551), 'period': np.int64(10800),
            'interference': np.array([0., 0.]), 'utilization': np.float64(0.004928569359008384), 'absolute_deadline': {1: np.int64(6552)}}
    ]

# Test creation


def create_taskset(data):
    """Create and return a Taskset object using provided data."""
    max_hyperperiod = data["taskset_options"]["max_hyperperiod"]
    max_prime = data["taskset_options"]["max_prime"]
    gen_limit_exponent = data["taskset_options"]["gen_limit_exponent"]
    PrimeMatrixGenerator(
        main_path=prime_path, result_path=result_path, max_hyperperiod=max_hyperperiod, max_prime=max_prime, gen_limit_exponent=gen_limit_exponent)
    generator = TasksetSetGenerator(
        main_path=prime_path,
        result_path=result_path,
        taskset_id=data['taskset_id'],
        taskset_repetition=data['taskset_repetition'],
        probability_factor=data['probability_factor'],
        max_utilization=data['max_utilization'],
        tasks_per_taskset=data['tasks_per_taskset'],
        interference_factor=data['interference_factor'],
        taskset_options=data["taskset_options"]
    )
    taskset_set = generator.generate_taskset_set()
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
            assert task.wcet == exp_task['wcet']
            assert task.deadline == exp_task['deadline']
            assert task.period == exp_task['period']
            assert np.array_equal(task.interference,
                                  exp_task['interference'])
            assert np.isclose(task.utilization,
                              exp_task['utilization'], rtol=1e-04)
            assert task.absolute_deadline == exp_task['absolute_deadline']


@pytest.fixture(autouse=True)
def reset_random_seed():
    np.random.seed(42)
    random.seed(42)


@pytest.mark.parametrize("input_data, expected_taskset_set, expected_taskset, expected_tasks", [
    (prepare_input_data(), expected_taskset_set_structure(),
     expected_taskset_structure(), expected_task_structure())
])
def test_taskset_creation(input_data, expected_taskset_set, expected_taskset, expected_tasks):
    """Main test function to test taskset creation and attribute validation."""
    taskset_set = create_taskset(input_data)
    verify_taskset_set_attributes(taskset_set, expected_taskset_set)
    verify_taskset_attributes(taskset_set, expected_taskset)
    verify_task_attributes(taskset_set, expected_tasks)
