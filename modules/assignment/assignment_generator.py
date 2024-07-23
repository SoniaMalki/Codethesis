from modules.assignment.assignment import Assignment
from modules.assignment.assignment_set import AssignmentSet
from modules.assignment.assignment_algorithms.citta import Citta
from modules.assignment.assignment_algorithms.worst_fit_assigner import WorstFitAssigner
from modules.assignment.assignment_algorithms.first_fit_assigner import FirstFitAssigner
from modules.assignment.assignment_algorithms.best_fit_assigner import BestFitAssigner
from modules.assignment.assignment_algorithms.w_min import Wmin

import time


class AssignmentGenerator:
    def __init__(self, taskset_set_obj, taskset_id, assignment_id, assignment_method, sorting_criterion, number_of_cores, assignment_options):
        self.taskset_set_obj = taskset_set_obj
        self.taskset_id = taskset_id
        self.assignment_id = assignment_id
        # Store in lowercase for case-insensitive comparison
        self.assignment_method = assignment_method
        self.sorting_criterion = sorting_criterion
        self.number_of_cores = number_of_cores
        self.assignment_options = assignment_options

    def generate_assignment_set(self):
        """Generates assignments for each Taskset within the TasksetSet."""
        assignment_list = []

        # Determine the assignment method once
        if self.assignment_method == "CITTA":
            assignment_function = self._citta_assignment
        elif self.assignment_method == "WorstFitAssigner":
            assignment_function = self._WorstFitAssigner_assignment
        elif self.assignment_method == "FirstFitAssigner":
            assignment_function = self._FirstFitAssigner_assignment
        elif self.assignment_method == "BestFitAssigner":
            assignment_function = self._BestFitAssigner_assignment
        elif self.assignment_method == "Wmin":
            assignment_function = self._wmin_assignment
        else:
            print(
                f"Invalid assignment method: {self.assignment_method}. Returning None.")
            return None

        # Apply the selected assignment function to all tasksets
        for taskset in self.taskset_set_obj.taskset_list:
            assignment, success = assignment_function(taskset)
            assignment_list.append(Assignment(
                assignment=assignment, success=success))
            print(assignment, success)

        assignment = AssignmentSet(assignment_id=self.assignment_id, taskset_id=self.taskset_id, assignment_method=self.assignment_method,
                                   sorting_criterion=self.sorting_criterion, number_of_cores=self.number_of_cores, assignment_list=assignment_list)  # Store assignments for each taskset
        return assignment  # Return a list of assignments, one for each taskset

    # Private methods now take a single taskset as input
    def _citta_assignment(self, taskset):
        """Performs the Citta assignment algorithm."""
        citta_instance = Citta(
            taskset,  # Pass a list containing only the current taskset
            self.number_of_cores,
            self.sorting_criterion,
            self.assignment_options
        )

        assigned_cores, successfully_assigned = citta_instance.assign()

        return assigned_cores, successfully_assigned

    def _WorstFitAssigner_assignment(self, taskset):
        """Performs the WorstFitAssigner assignment algorithm."""
        WorstFitAssigner_instance = WorstFitAssigner(
            taskset,  # Pass a list containing only the current taskset
            self.number_of_cores,
            self.sorting_criterion,
            self.assignment_options
        )
        assigned_cores, successfully_assigned = WorstFitAssigner_instance.assign()

        return assigned_cores, successfully_assigned

    def _FirstFitAssigner_assignment(self, taskset):
        """Performs the FirstFitAssigner assignment algorithm."""
        FirstFitAssigner_instance = FirstFitAssigner(
            taskset,  # Pass a list containing only the current taskset
            self.number_of_cores,
            self.sorting_criterion,
            self.assignment_options
        )
        assigned_cores, successfully_assigned = FirstFitAssigner_instance.assign()

        return assigned_cores, successfully_assigned

    def _BestFitAssigner_assignment(self, taskset):
        """Performs the BestFitAssigner assignment algorithm."""
        BestFitAssigner_instance = BestFitAssigner(
            taskset,  # Pass a list containing only the current taskset
            self.number_of_cores,
            self.sorting_criterion,
            self.assignment_options
        )
        assigned_cores, successfully_assigned = BestFitAssigner_instance.assign()

        return assigned_cores, successfully_assigned

    def _wmin_assignment(self, taskset):
        """Performs the Wmin assignment algorithm."""
        wmin_instance = Wmin(
            taskset,  # Pass a list containing only the current taskset
            self.number_of_cores,
            self.assignment_options
        )
        assigned_cores, successfully_assigned = wmin_instance.assign()

        return assigned_cores, successfully_assigned
