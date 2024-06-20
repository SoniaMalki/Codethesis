import json
import os
from pathlib import Path

from modules.taskset.taskset_set_generator import TasksetSetGenerator

class Experience:
    def __init__(self, taskset_parameters, assignment_parameters, scheduling_parameters):
        """
        Initializes an Experience object.

        Args:
            taskset_parameters (dict): A dictionary containing taskset configuration.
            assignment_parameters (dict): A dictionary containing assignment configuration.
            scheduling_parameters (dict): A dictionary containing scheduling configuration.
        """
        self.taskset_parameters = taskset_parameters
        self.assignment_parameters = assignment_parameters
        self.scheduling_parameters = scheduling_parameters
        
        self.taskset_set_obj = None
        self.assignment_obj = None  # Use assignment_obj to avoid confusion with assignment (dict)
        self.scheduling_obj = None  # Use scheduling_obj to avoid confusion with scheduling (dict)

    def process(self):
        """Processes the experience, generating tasksets, assignments, and schedulings as needed."""
        print("Processing Experience")
        self._process_taskset()
        #self._process_assignment()
        #self._process_scheduling()

    def _process_taskset(self):
        """Handles the generation or opening of the taskset."""
        if self.taskset_parameters["action"] == 'generate':
            print("*****")
            print(f"Generating taskset")
            print(self.taskset_parameters["parameters"])
            taskset_generator = TasksetSetGenerator(**self.taskset_parameters["parameters"])
            self.taskset_set = taskset_generator.generate_taskset_set()
            self.taskset["taskset_id"] = self.taskset_set.taskset_set_number

        #TODO todo test this after generate is corrected
        elif self.taskset_parameters["action"] == 'open':
            print("*****")
            print(f"Opening taskset")
            taskset_loader = TasksetSetLoader()
            self.taskset_set = taskset_loader.load(self.taskset_parameters["taskset_id"])
        else:
            print(f"Invalid taskset action: {self.taskset_parameters['action']}")
            return

    def _process_assignment(self):
        """Handles the generation or opening of the assignment."""
        if self.assignment["action"] == 'generate':
            print("*****")
            print(f"Launching assignment with method {self.assignment['parameters']['assignment_method']}")
            if self.taskset_set is None:
                print("Cannot generate assignment without a valid taskset.")
                return

            assignment_generator = AssignmentGenerator()
            self.assignment_obj = assignment_generator.generate_assignment(
                self.taskset_set,
                self.assignment['parameters']['assignment_method'],
                self.assignment['parameters']['citta_criteria']
            )
            self.assignment["assignment_id"] = self.assignment_obj.assignment_id

        elif self.assignment["action"] == 'open':
            print("*****")
            print(f"Opening assignment")
            assignment_loader = AssignmentLoader()
            self.assignment_obj = assignment_loader.load(self.assignment["assignment_id"])
        else:
            self.assignment_obj = None  # No assignment needed

    def _process_scheduling(self):
        """Handles the generation or opening of the scheduling."""
        if self.scheduling["action"] == 'generate':
            print("*****")
            print(f"Launching scheduling with method {self.scheduling['parameters']['scheduling_algorithms']}")
            if self.taskset_set is None or self.assignment_obj is None:
                print("Cannot generate scheduling without a valid taskset and assignment.")
                return

            self.scheduling_obj = SchedulingGenerator(
                self.taskset_set,
                self.assignment_obj,
                self.scheduling['parameters']['scheduling_algorithms']
            ).generate_scheduling()
            self.scheduling["scheduling_id"] = self.scheduling_obj.scheduling_id
            print(f"Scheduling completed. Schedule ID: {self.scheduling_obj.scheduling_id}")

        elif self.scheduling["action"] == 'open':
            print("*****")
            print(f"Opening schedule")
            scheduling_loader = SchedulingLoader()
            self.scheduling_obj = scheduling_loader.load(self.scheduling["scheduling_id"])
        else:
            self.scheduling_obj = None  # No scheduling needed

    def save(self, filename):
        """Saves the experience data to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.parameters, f, indent=4)  # Save parameters to JSON