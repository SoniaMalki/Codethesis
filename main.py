import sys
import datetime
import pickle
import os 
import json
from pathlib import Path
import time

# Corrected imports based on your directory structure
from modules.experience_generation.experience_generator import ExperienceGenerator
from modules.experience_generation.experience import Experience
#from modules.experience_generation.task_model.matrix_m import MatrixM
from modules.experience_generation.taskset_set_generator import TasksetSetGenerator
from modules.taskset import Taskset
from modules.assignment_generation.citta import Citta
from modules.assignment_generation.taskset_assignment import TasksetAssignment
from modules.scheduling_generation.scheduler import Scheduler
from modules.assignment_generation.assignment_result import AssignmentResult
from modules.scheduling_generation.scheduling_result import SchedulingResult

current_path = Path(__file__).parent


def format_assignment_results(assignment_results):
    formatted_results = []

    for core_index, tasks in enumerate(assignment_results):
        core_summary = f"Core {core_index + 1}:\n"
        total_utilization = 0.0

        for task in tasks:
            task_description = f"    Task {task.task_number} - WCET: {task.wcet}, Deadline: {task.deadline}, Period: {task.period}, Utilization: {task.utilization}\n"
            core_summary += task_description
            total_utilization += task.utilization

        core_summary += f"Total Utilization: {total_utilization:.2f}\n"
        formatted_results.append(core_summary)

    return "\n".join(formatted_results)


def main(experience_parameter_index="0"):
    experience_parameter = load_parameter("experience", experience_parameter_index)

    taskset_option = experience_parameter["taskset_option"]
    assignment_option = experience_parameter["assignment_option"]
    schedule_option = experience_parameter["schedule_option"]

    if taskset_option != "none":
        taskset_name = experience_parameter["taskset_name"]

        if taskset_option == "generate":
            print("*****")
            print(f"Generating taskset")
            generation_parameter_index = experience_parameter["generation_parameter_index"]
            generation_parameter = load_parameter("generation", generation_parameter_index)
            experience = experience_generation(generation_parameter)
            print(experience)
            write_result(experience, "taskset", taskset_name)
        elif taskset_option == "open":
            print("*****")
            print(f"Opening taskset")
            experience = open_generated("taskset", taskset_name)

    if assignment_option != "none":
        assignment_name = experience_parameter["assignment_name"]

        if assignment_option == "generate":
            list_of_assignment_algorithm = experience_parameter["list_of_assignment_algorithm"]
            assignment_result = AssignmentResult()
            for assignment_algorithm in list_of_assignment_algorithm:
                print("*****")
                print(f"Launching assignment with method {assignment_algorithm}")
                assignment_result = launch_assignment_experience(assignment_algorithm, experience, assignment_result)
                print(format_assignment_results(assignment_result[0]['taskset_assignment']))
                write_result(assignment_result, "assignment", assignment_name)
        elif assignment_option == "open":
            print("*****")
            print(f"Opening assignment")
            assignment_result = open_generated("assignment", assignment_name)

    if schedule_option != "none":
        schedule_name = experience_parameter["schedule_name"]

        if schedule_option == "generate":
            list_of_scheduling_algorithm = experience_parameter["list_of_scheduling_algorithm"]
            print("--------------------------------------------")
            scheduling_result = SchedulingResult()
            for scheduling_algorithm in list_of_scheduling_algorithm:
                print("*****")
                print(f"Launching scheduling with method {scheduling_algorithm}")
                scheduling_result = launch_scheduling_experience(scheduling_algorithm, experience, assignment_result, scheduling_result)
            print("--------------------------------------------")
        elif schedule_option == "open":
            print("*****")
            print(f"Opening schedule")
            scheduling_result = open_generated("schedule", schedule_name)


def load_parameter(parameter_name, parameter_index):
    with open(f'{current_path}/{parameter_name}_parameter.json', 'r') as json_file:
        parameter = json.load(json_file)
    assert len(parameter) != 0
    if int(parameter_index) >= 0 and int(parameter_index) < len(parameter):
        return parameter[parameter_index]
    else:
        print("Parameter not specified or not in the range; defaulting to option 0")
        return parameter["0"]

def experience_generation(generation_parameter):
    experience_generation = ExperienceGenerator(**generation_parameter)
    experience = experience_generation.generate_experience()
    return experience

def matrix_generation(matrix_parameter):
    matrix_generation = MatrixGeneration(**matrix_parameter)
    matrix = matrix_generation.generate_matrix()
    return matrix

def launch_assignment_experience(assignment_algorithm, experience, assignment_result):
    list_of_sorting_criterion = experience.list_of_sorting_criterion
    number_of_cores = experience.number_of_cores
    assignment_running_length = len(experience) * len(experience.taskset_set_list[0]) * len(list_of_sorting_criterion)
    taskset_assignment = TasksetAssignment(assignment_algorithm, number_of_cores)
    experience_assignment = []
    i = 0
    for taskset_set in experience:
        for taskset in taskset_set:
            for sorting_criterion in list_of_sorting_criterion:
                print(f"Launching taskset assignment {i+1} of {assignment_running_length}")
                task_assignment_list, successfully_assigned = taskset_assignment.assign(taskset=taskset, sorting_criterion=sorting_criterion)
                assignment_result.add_result(successfully_assigned, task_assignment_list, taskset)
                i += 1
    return assignment_result

def launch_scheduling_experience(scheduling_algorithm, experience, assignment_result, scheduling_result):
    number_of_cores = experience.number_of_cores
    scheduling_running_length = len(assignment_result)
    for i, assignment in enumerate(assignment_result):
        print(f"Launching taskset scheduling {i+1} of {scheduling_running_length}")
        taskset_scheduling = Scheduler(assignment, scheduling_algorithm, number_of_cores)
        schedule, successfully_scheduled = taskset_scheduling.schedule()
        print(schedule)
        schedule.draw_task_schedule()
        scheduling_result.add_result(successfully_scheduled, schedule, assignment)
    return scheduling_result

def open_generated(dir_name, filename):
    with open(f"{current_path}/results/{dir_name}/{filename}.obj", 'rb') as filepy:
        res = pickle.load(filepy)
    return res

def write_result(experiment_assignment_result, dir_name, filename):
    parent_dir_name = f"{current_path}/results"
    if not os.path.isdir(parent_dir_name):
        os.mkdir(parent_dir_name)
    if not os.path.isdir(parent_dir_name + "/" + dir_name):
        os.mkdir(parent_dir_name + "/" + dir_name)
    
    with open(f"{parent_dir_name}/{dir_name}/{filename}.obj", 'wb') as filepy:
        pickle.dump(experiment_assignment_result, filepy)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        experience_parameter_index = sys.argv[1]
        main(experience_parameter_index)
    elif len(sys.argv) >= 3:
        experience_parameter_index = sys.argv[1]
        generation_parameter_index = sys.argv[2]
        main(experience_parameter_index, generation_parameter_index)
    else:
        main()
