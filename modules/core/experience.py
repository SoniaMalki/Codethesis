import json
import os
from pathlib import Path

class Experience:
    def __init__(self, **kwargs):
        """
        Initializes an Experience object.

        Args:
            **kwargs: A dictionary containing parameters to generate tasksets, assignments, and schedulings.
        """
        self.taskset_set = None
        self.assignment = None
        self.scheduling = None
        self.parameters = kwargs

    def process(self):
        """Processes the experience, generating tasksets, assignments, and schedulings as needed."""
        print("Processing Experience")
        print(self.parameters.keys())

        taskset_parameters = self.parameters.get('taskset')
        print(taskset_parameters)
        # Taskset handling
        if taskset_parameters.get('action') == 'generate':
            print("*****")
            print(f"Generating taskset")
            taskset_generator = TasksetSetGenerator(**self.parameters['taskset_parameters'])
            self.taskset_set = taskset_generator.generate_taskset_set()
            self.parameters['taskset_id'] = self.taskset_set.taskset_set_number

        elif taskset_parameters.get('action') == 'open':
            print("*****")
            print(f"Opening taskset")
            taskset_loader = TasksetSetLoader()
            self.taskset_set = taskset_loader.load(self.parameters['taskset_id'])
        else:
            print(f"Invalid taskset action: {taskset_parameters.get('action')}")
            return

        # Assignment handling
        if self.parameters.get('assignment_action') == 'generate':
            print("*****")
            print(f"Launching assignment with method {self.parameters['assignment_parameters']['assignment_method']}")
            if self.taskset_set is None:
                print("Cannot generate assignment without a valid taskset.")
                return

            assignment_generator = AssignmentGenerator()
            self.assignment = assignment_generator.generate_assignment(
                self.taskset_set,
                self.parameters['assignment_parameters']['assignment_method'],
                self.parameters['assignment_parameters']['citta_criteria']
            )
            self.parameters['assignment_id'] = self.assignment.assignment_id

        elif self.parameters.get('assignment_action') == 'open':
            print("*****")
            print(f"Opening assignment")
            assignment_loader = AssignmentLoader()
            self.assignment = assignment_loader.load(self.parameters['assignment_id'])
        else:
            self.assignment = None  # No assignment needed

        # Scheduling handling
        if self.parameters.get('scheduling_action') == 'generate':
            print("*****")
            print(f"Launching scheduling with method {self.parameters['scheduling_parameters']['scheduling_algorithms']}")
            if self.taskset_set is None or self.assignment is None:
                print("Cannot generate scheduling without a valid taskset and assignment.")
                return

            self.scheduling = SchedulingGenerator(
                self.taskset_set,
                self.assignment,
                self.parameters['scheduling_parameters']['scheduling_algorithms']
            ).generate_scheduling()
            self.parameters['scheduling_id'] = self.scheduling.scheduling_id
            print(f"Scheduling completed. Schedule ID: {self.scheduling.scheduling_id}")

        elif self.parameters.get('scheduling_action') == 'open':
            print("*****")
            print(f"Opening schedule")
            scheduling_loader = SchedulingLoader()
            self.scheduling = scheduling_loader.load(self.parameters['scheduling_id'])
        else:
            self.scheduling = None  # No scheduling needed

    def save(self, filename):
        """Saves the experience data to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.parameters, f, indent=4)  # Save parameters to JSON