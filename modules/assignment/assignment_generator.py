import numpy
from modules.assignment.assignment import Assignment
from modules.assignment.assignment_set import AssignmentSet
from modules.assignment.assignment_algorithms.citta import Citta
from modules.assignment.assignment_algorithms.worst_fit_assigner import WorstFitAssigner
from modules.assignment.assignment_algorithms.first_fit_assigner import FirstFitAssigner
from modules.assignment.assignment_algorithms.best_fit_assigner import BestFitAssigner
from modules.assignment.assignment_algorithms.w_min import Wmin

from time import perf_counter


class AssignmentGenerator:
    def __init__(self, taskset_set_obj, taskset_id, assignment_id, assignment_method, sorting_criterion, number_of_cores, assignment_options):
        print("Initializing AssignmentGenerator")
        self.taskset_set_obj = taskset_set_obj
        self.taskset_id = taskset_id
        self.assignment_id = assignment_id
        self.assignment_method = assignment_method
        self.sorting_criterion = sorting_criterion
        self.number_of_cores = number_of_cores
        self.assignment_options = assignment_options
        self.assignment_algorithms_with_sorting = [
            "Citta",
            "WorstFitAssigner",
            "FirstFitAssigner",
            "BestFitAssigner"
        ]

        self.assignment_algorithms_without_sorting = [
            "Wmin"
        ]
        print(
            f"AssignmentGenerator initialized with method: {self.assignment_method}")

    def generate_assignment_set(self):
        """Generates assignments for each Taskset within the TasksetSet."""
        print("Generating assignment set")
        assignment_list = []  # Store assignments for each taskset

        # Determine the assignment method once
        if self.assignment_method not in self.assignment_algorithms_with_sorting and self.assignment_method not in self.assignment_algorithms_without_sorting:
            print(
                f"Invalid assignment method: {self.assignment_method}. Returning None.")
            return None

        assignment_class = globals()[self.assignment_method]

        if self.assignment_method in self.assignment_algorithms_with_sorting:
            assignment_function = self.generate_assignment_with_sorting
        else:
            assignment_function = self.generate_assignment_without_sorting

        # Apply the selected assignment function to all tasksets
        for taskset in self.taskset_set_obj.taskset_list:
            print(f"Generating assignment for taskset: {taskset.taskset_id}")
            assignment = assignment_function(taskset, assignment_class)
            assignment_list.append(assignment)
            print(f"Assignment generated for taskset: {taskset.taskset_id}")

        assignment_set = AssignmentSet(assignment_id=self.assignment_id, taskset_id=self.taskset_id, assignment_method=self.assignment_method,
                                       sorting_criterion=self.sorting_criterion, number_of_cores=self.number_of_cores, assignment_list=assignment_list)
        print("Assignment set generation completed")
        return assignment_set

    def generate_assignment_with_sorting(self, taskset, assignment_class):
        print(
            f"Generating assignment with sorting using {assignment_class.__name__}")
        start_time_compute = perf_counter()
        assigner = assignment_class(
            taskset=taskset,
            number_of_cores=self.number_of_cores,
            sorting_criterion=self.sorting_criterion,
            assignment_options=self.assignment_options
        )
        assigned_cores, successfully_assigned = assigner.assign()
        end_time_compute = perf_counter()
        computation_time = end_time_compute - start_time_compute
        if not successfully_assigned:
            computation_time = numpy.nan
            print(
                f"Assignment with sorting failed for taskset: {taskset.taskset_id}")
        else:
            print(
                f"Assignment with sorting succeeded for taskset: {taskset.taskset_id}")

        assignment = Assignment(assignment=assigned_cores,
                                success=successfully_assigned)
        assignment.add_performances(computation_time=computation_time)
        return assignment

    def generate_assignment_without_sorting(self, taskset, assignment_class):
        print(
            f"Generating assignment without sorting using {assignment_class.__name__}")
        start_time_compute = perf_counter()
        assigner = assignment_class(
            taskset=taskset,
            number_of_cores=self.number_of_cores,
            assignment_options=self.assignment_options
        )
        assigned_cores, successfully_assigned = assigner.assign()
        end_time_compute = perf_counter()
        computation_time = end_time_compute - start_time_compute
        if not successfully_assigned:
            computation_time = numpy.nan
            print(
                f"Assignment without sorting failed for taskset: {taskset.taskset_id}")
        else:
            print(
                f"Assignment without sorting succeeded for taskset: {taskset.taskset_id}")

        assignment = Assignment(assignment=assigned_cores,
                                success=successfully_assigned)
        assignment.add_performances(computation_time=computation_time)
        return assignment
