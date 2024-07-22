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

scheduling_options_non_preemption_time_variant2 = [
    "number_of_tasks",
    "wcet_of_tasks",
    "system_utilization"
]

scheduling_algorithms = scheduling_algorithms_with_combination + \
    scheduling_algorithms_without_combination
experiences = ["manual_1", "manual_2", "generate_1"]


def prepare_input_data_taskset_manual_1():
    taskset_id = "taskset_manual_1"
    taskset_action = "manual"
    wcet = [2, 3, 2, 3]
    deadline = [6, 10, 7, 9]
    period = [6, 10, 7, 9]
    interference = [
        [0, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 0]
    ]

    utilization = [w / p for w, p in zip(wcet, period)]

    return taskset_id, taskset_action, wcet, deadline, period, interference, utilization


def prepare_input_data_taskset_manual_2():
    taskset_id = "taskset_manual_2"
    taskset_action = "manual"
    wcet = [3, 3, 21, 14, 8]
    deadline = [12, 15, 75, 24, 25]
    period = [12, 15, 75, 24, 25]
    interference = [
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ]
    utilization = [w / p for w, p in zip(wcet, period)]

    return taskset_id, taskset_action, wcet, deadline, period, interference, utilization


def prepare_input_data_taskset_generate_1():
    taskset_id = "taskset_generate_1"
    taskset_action = "generate"
    taskset_repetition = 1
    probability_factor = 0.1
    max_utilization = 1
    tasks_per_taskset = 5
    interference_factor = 0.2
    taskset_options = {
        "deadline_option": "eq_period",
        "max_hyperperiod": 10000,
        "max_prime": 20,
        "gen_limit_exponent": 2
    }

    return taskset_id, taskset_action, taskset_repetition, probability_factor, max_utilization, tasks_per_taskset, interference_factor, taskset_options


def prepare_input_data_dic_taskset_manual(wcet, deadline, period, interference, utilization):
    taskset_parameters = {
        "wcet_list": wcet,
        "deadline_list": deadline,
        "period_list": period,
        "interference_list": interference,
        "utilization_list": utilization
    }
    return taskset_parameters


def prepare_input_data_dic_taskset_generate(taskset_repetition, probability_factor, max_utilization, tasks_per_taskset, interference_factor, taskset_options):
    taskset_parameters = {
        "taskset_repetition": taskset_repetition,
        "probability_factor": probability_factor,
        "max_utilization": max_utilization,
        "tasks_per_taskset": tasks_per_taskset,
        "interference_factor": interference_factor,
        "taskset_options": taskset_options
    }
    return taskset_parameters


def prepare_input_data_dic(scheduling_algorithm, non_preemption_time_variant_2):
    assignment_parameters = {
        "assignment_id": "assignment",
        "taskset_id": "taskset",
        "sorting_criterion": "utilization_descending",
        "assignment_method": "WFDU",
        "number_of_cores": 2,
        "assignment_options": {

        },
    }
    scheduling_parameters = {
        "assignment_id": "assignment",
        "taskset_id": "taskset",
        "scheduling_id": "scheduling",
        "scheduling_algorithm": scheduling_algorithm,
        "scheduling_options": {
            "non_preemption_time_variant2": non_preemption_time_variant_2,
            "solving_time_limit_MILP": 10,
        }
    }
    return assignment_parameters, scheduling_parameters


def prepare_input_data(experience, scheduling_algorithm, non_preemption_time_variant_2):
    if experience == "manual_1":
        taskset_id, taskset_action, wcet, deadline, period, interference, utilization = prepare_input_data_taskset_manual_1()
    elif experience == "manual_2":
        taskset_id, taskset_action, wcet, deadline, period, interference, utilization = prepare_input_data_taskset_manual_2()
    elif experience == "generate_1":
        taskset_id, taskset_action, taskset_repetition, probability_factor, max_utilization, tasks_per_taskset, interference_factor, taskset_options = prepare_input_data_taskset_generate_1()

    if taskset_action == "manual":
        taskset_parameters = prepare_input_data_dic_taskset_manual(
            wcet, deadline, period, interference, utilization)
    elif taskset_action == "generate":
        taskset_parameters = prepare_input_data_dic_taskset_generate(
            taskset_repetition, probability_factor, max_utilization, tasks_per_taskset, interference_factor, taskset_options)
    assignment_parameters, scheduling_parameters = prepare_input_data_dic(
        scheduling_algorithm, non_preemption_time_variant_2)
    return taskset_action, taskset_id, taskset_parameters, assignment_parameters, scheduling_parameters


def prepare_output_data(scheduling_loader_saver, experience, scheduling, scheduling_parameters, scheduling_algorithm, non_preemption_time_variant_2):
    save_test_results(scheduling_loader_saver, scheduling,
                      scheduling_parameters, experience, scheduling_algorithm, non_preemption_time_variant_2)
    expected_scheduling = scheduling_loader_saver.load_test_expected_result(
        scheduling_parameters["scheduling_id"],
        experience,
        scheduling_algorithm,
        non_preemption_time_variant_2
    )
    return expected_scheduling


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


def create_scheduling(taskset, assignment, scheduling_parameters):
    generator = SchedulingGenerator(
        taskset_set_obj=taskset,
        assignment_set_obj=assignment,
        taskset_id=scheduling_parameters["taskset_id"],
        assignment_id=scheduling_parameters["assignment_id"],
        scheduling_id=scheduling_parameters["scheduling_id"],
        scheduling_algorithm=scheduling_parameters["scheduling_algorithm"],
        scheduling_options=scheduling_parameters["scheduling_options"]
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


def verify_assignment(assignment):
    for result in assignment:
        assert result.success == 1


def verify_scheduling(scheduling, expected_scheduling):
    assert scheduling == expected_scheduling
    for result, exp_s in zip(scheduling, expected_scheduling):
        assert result == exp_s


@ pytest.fixture(autouse=True)
def reset_random_seed():
    np.random.seed(42)
    random.seed(42)


def generate_param_combinations():
    combinations = []
    for non_preemp_t_variant_2 in scheduling_options_non_preemption_time_variant2:
        for algorithm in scheduling_algorithms:
            for experience in experiences:
                combinations.append(
                    (algorithm, experience, non_preemp_t_variant_2))
    return combinations


def save_test_results(scheduling_loader_saver, scheduling, scheduling_parameters, experience, scheduling_algorithm, non_preemption_time_variant_2):
    if save_results:
        # Sauvegarder les résultats pour la première exécution du test
        scheduling_loader_saver.save_test_expected_result(
            scheduling,
            scheduling_parameters["scheduling_id"],
            experience,
            scheduling_algorithm,
            non_preemption_time_variant_2,
        )


@ pytest.mark.parametrize("scheduling_algorithm,experience, non_preemption_time_variant2", generate_param_combinations(), ids=lambda val: f"{val}")
def test_scheduling(scheduling_algorithm, experience, non_preemption_time_variant2):
    input_data = prepare_input_data(
        experience, scheduling_algorithm, non_preemption_time_variant2)
    taskset_action, taskset_id, taskset_parameters, assignment_parameters, scheduling_parameters = input_data
    scheduling_loader_saver = SchedulingLoaderSaver(Path(os.getcwd()))

    if taskset_action == "manual":
        taskset = create_taskset_manual(taskset_id, taskset_parameters)
    elif taskset_action == "generate":
        taskset = create_taskset_generate(taskset_id, taskset_parameters)
    else:
        raise ValueError("Invalid parameter")
    assignment = create_assignment(
        taskset, assignment_parameters)

    # if assignment_parameters["assignment_method"].lower() != "wmin":
    #     shape_interference(taskset)
    verify_assignment(assignment)
    scheduling = create_scheduling(taskset, assignment, scheduling_parameters)

    expected_scheduling = prepare_output_data(
        scheduling_loader_saver, experience, scheduling, scheduling_parameters, scheduling_algorithm, non_preemption_time_variant2)

    if expected_scheduling is not None:
        verify_scheduling(scheduling, expected_scheduling)
    else:
        assert False, "Résultats de scheduling attendus non trouvés, veuillez les créer."
