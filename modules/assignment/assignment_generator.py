from modules.assignment.assignment import Assignment
from modules.assignment.assignment_set import AssignmentSet
from modules.assignment.assignment_algorithms.citta import Citta
from modules.assignment.assignment_algorithms.citta_old import Cittaold
from modules.assignment.assignment_algorithms.wfdu import Wfdu
from modules.assignment.assignment_algorithms.ffdu import Ffdu
from modules.assignment.assignment_algorithms.w_min import Wmin

import time

class AssignmentGenerator:
    def __init__(self, taskset_set_obj, taskset_id, assignment_id, assignment_method, citta_criteria, number_of_cores):
        self.taskset_set_obj = taskset_set_obj
        self.taskset_id = taskset_id
        self.assignment_id = assignment_id
        self.assignment_method = assignment_method[0].lower()  # Store in lowercase for case-insensitive comparison
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
        elif self.assignment_method == "wmin":
            assignment_function = self._wmin_assignment
        else:
            print(f"Invalid assignment method: {self.assignment_method}. Returning None.")
            return None

        # Apply the selected assignment function to all tasksets
        for taskset in self.taskset_set_obj.taskset_list:
            assignment, success = assignment_function(taskset)
            assignment_list.append(Assignment(assignment=assignment, success=success))

        assignment = AssignmentSet(assignment_id=self.assignment_id, taskset_id=self.taskset_id, assignment_method=self.assignment_method,
                                   citta_criteria=self.citta_criteria, number_of_cores=self.number_of_cores, assignment_list=assignment_list)  # Store assignments for each taskset
        return assignment  # Return a list of assignments, one for each taskset

    # Private methods now take a single taskset as input
    def _citta_assignment(self, taskset):
        """Performs the Citta assignment algorithm."""
        citta_instance= Citta(
            taskset,  # Pass a list containing only the current taskset
            self.number_of_cores,
            self.citta_criteria
        )

        assigned_cores, successfully_assigned = citta_instance.assign()
        print(assigned_cores, "citta mine")

        citta_instance= Cittaold(
            taskset,  # Pass a list containing only the current taskset
            self.number_of_cores,
            self.citta_criteria
        )

        assigned_cores,_ ,successfully_assigned = citta_instance.assign()
        print(assigned_cores, "citta old")


        task_assignment_list = [[] for _ in range(self.number_of_cores)]
        if successfully_assigned:
            for core_index, core in enumerate(assigned_cores):
                for task_index in core:
                    task_assignment_list[core_index].append(taskset.task_list[task_index])

        return task_assignment_list, successfully_assigned

    def _wfdu_assignment(self, taskset):
        """Performs the WFDU assignment algorithm."""
        wfdu_instance = Wfdu(
            taskset,  # Pass a list containing only the current taskset
            self.number_of_cores
        )
        assigned_cores, successfully_assigned = wfdu_instance.assign()
        print(assigned_cores)
        task_assignment_list = [[] for _ in range(self.number_of_cores)]
        if successfully_assigned:
            for core_index, core in enumerate(assigned_cores):
                for task_index in core:
                    task_assignment_list[core_index].append(taskset.task_list[task_index])

        return task_assignment_list, successfully_assigned

    def _ffdu_assignment(self, taskset):
        """Performs the FFDU assignment algorithm."""
        ffdu_instance = Ffdu(
            taskset,  # Pass a list containing only the current taskset
            self.number_of_cores
        )
        assigned_cores, successfully_assigned = ffdu_instance.assign()
        print(assigned_cores)
        task_assignment_list = [[] for _ in range(self.number_of_cores)]
        if successfully_assigned:
            for core_index, core in enumerate(assigned_cores):
                for task_index in core:
                    task_assignment_list[core_index].append(taskset.task_list[task_index])

        return task_assignment_list, successfully_assigned

    def _wmin_assignment(self, taskset):
        """Performs the Wmin assignment algorithm."""
        wmin_instance = Wmin(
            taskset,  # Pass a list containing only the current taskset
            self.number_of_cores
        )
        assigned_cores, successfully_assigned = wmin_instance.assign()
        
        task_assignment_list = [[] for _ in range(self.number_of_cores)]
        if successfully_assigned:
            for core_index, core in enumerate(assigned_cores):
                for task_index in core:
                    task_assignment_list[core_index].append(taskset.task_list[task_index])

        return task_assignment_list, successfully_assigned