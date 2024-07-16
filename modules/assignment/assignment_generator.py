from modules.assignment.assignment import Assignment
from modules.assignment.assignment_set import AssignmentSet
from modules.assignment.assignment_algorithms.citta import Citta
from modules.assignment.assignment_algorithms.wfdu import Wfdu
from modules.assignment.assignment_algorithms.ffdu import Ffdu
from modules.assignment.assignment_algorithms.bfdu import Bfdu
from modules.assignment.assignment_algorithms.w_min import Wmin

import time


class AssignmentGenerator:
    def __init__(self, taskset_set_obj, taskset_id, assignment_id, assignment_method, citta_criteria, number_of_cores):
        self.taskset_set_obj = taskset_set_obj
        self.taskset_id = taskset_id
        self.assignment_id = assignment_id
        # Store in lowercase for case-insensitive comparison
        self.assignment_method = assignment_method[0].lower()
        self.citta_criteria = citta_criteria[0].lower()
        self.number_of_cores = number_of_cores

    def generate_assignment_set(self):
        """Generates assignments for each Taskset within the TasksetSet."""
        assignment_list = []

        # Determine the assignment method once
        if self.assignment_method == "citta":
            assignment_function = self._citta_assignment
        elif self.assignment_method == "wfdu":
            assignment_function = self._wfdu_assignment
        elif self.assignment_method == "ffdu":
            assignment_function = self._ffdu_assignment
        elif self.assignment_method == "bfdu":
            assignment_function = self._bfdu_assignment
        elif self.assignment_method == "wmin":
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

        assignment = AssignmentSet(assignment_id=self.assignment_id, taskset_id=self.taskset_id, assignment_method=self.assignment_method,
                                   citta_criteria=self.citta_criteria, number_of_cores=self.number_of_cores, assignment_list=assignment_list)  # Store assignments for each taskset
        return assignment  # Return a list of assignments, one for each taskset

    # Private methods now take a single taskset as input
    def _citta_assignment(self, taskset):
        """Performs the Citta assignment algorithm."""
        citta_instance = Citta(
            taskset,  # Pass a list containing only the current taskset
            self.number_of_cores,
            self.citta_criteria
        )

        assigned_cores, successfully_assigned = citta_instance.assign()

        return assigned_cores, successfully_assigned

    def _wfdu_assignment(self, taskset):
        """Performs the WFDU assignment algorithm."""
        wfdu_instance = Wfdu(
            taskset,  # Pass a list containing only the current taskset
            self.number_of_cores
        )
        assigned_cores, successfully_assigned = wfdu_instance.assign()

        return assigned_cores, successfully_assigned

    def _ffdu_assignment(self, taskset):
        """Performs the FFDU assignment algorithm."""
        ffdu_instance = Ffdu(
            taskset,  # Pass a list containing only the current taskset
            self.number_of_cores
        )
        assigned_cores, successfully_assigned = ffdu_instance.assign()

        return assigned_cores, successfully_assigned

    def _bfdu_assignment(self, taskset):
        """Performs the BFDU assignment algorithm."""
        bfdu_instance = Bfdu(
            taskset,  # Pass a list containing only the current taskset
            self.number_of_cores
        )
        assigned_cores, successfully_assigned = bfdu_instance.assign()

        return assigned_cores, successfully_assigned

    def _wmin_assignment(self, taskset):
        """Performs the Wmin assignment algorithm."""
        wmin_instance = Wmin(
            taskset,  # Pass a list containing only the current taskset
            self.number_of_cores
        )
        assigned_cores, successfully_assigned = wmin_instance.assign()

        return assigned_cores, successfully_assigned
