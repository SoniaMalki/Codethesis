import json
import os
from pathlib import Path
import numpy as np

from modules.taskset.taskset_set_generator import TasksetSetGenerator
from modules.taskset.taskset_set_loader_saver import TasksetSetLoaderSaver
from modules.assignment.assignment_generator import AssignmentGenerator
from modules.assignment.assignment_loader_saver import AssignmentLoaderSaver
from modules.scheduling.scheduling_generator import SchedulingGenerator
from modules.scheduling.scheduling_loader_saver import SchedulingLoaderSaver


class Experience:
    def __init__(self, taskset_parameters, assignment_parameters, scheduling_parameters, main_path):
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

        self.main_path = main_path
        
        self.taskset_set_obj = None
        self.assignment_set_obj = None 
        self.scheduling_set_obj = None  

    def process(self):
        """Processes the experience, generating tasksets, assignments, and schedulings as needed."""
        print("Processing Experience")
        self.process_taskset()
        self.process_assignment()
        self.process_scheduling()

    def process_taskset(self):
        """Handles the generation or opening of the taskset."""
        taskset_loader_saver = TasksetSetLoaderSaver(self.main_path)

        if self.taskset_parameters["action"] == 'generate':
            print("*****")
            print(f"Generating taskset")
            taskset_generator = TasksetSetGenerator(self.taskset_parameters["taskset_id"], **self.taskset_parameters["parameters"])
            self.taskset_set_obj = taskset_generator.generate_taskset_set()
            taskset_loader_saver.save(self.taskset_set_obj)

        elif self.taskset_parameters["action"] == 'open':
            print("*****")
            print(f"Opening taskset")
            self.taskset_set_obj = taskset_loader_saver.load(self.taskset_parameters["taskset_id"])
        else:
            print(f"Invalid taskset action: {self.taskset_parameters['action']}")
            return

    def process_assignment(self):
        """Handles the generation or opening of the assignment."""
        assignment_loader_saver = AssignmentLoaderSaver(self.main_path)

        if self.assignment_parameters["action"] == 'generate':
            print("*****")
            print(f"Generating assignment")
            assignment_generator = AssignmentGenerator(
                self.taskset_set_obj,
                self.assignment_parameters["taskset_id"],
                self.assignment_parameters["assignment_id"],
                **self.assignment_parameters["parameters"]
            )
            self.assignment_set_obj = assignment_generator.generate_assignment_set()
            assignment_loader_saver.save(self.assignment_set_obj, self.assignment_parameters["assignment_id"])

        elif self.assignment_parameters["action"] == 'open':
            print("*****")
            print(f"Opening assignment")
            self.assignment_set_obj = assignment_loader_saver.load(self.assignment_parameters["assignment_id"])
        
        elif self.assignment_parameters["action"] == 'none':
            print(f"None received. Pass")
        
        else:
            print(f"Invalid assignment action: {self.assignment_parameters['action']}")
            return

    def process_scheduling(self):
        """Handles the generation or opening of the scheduling."""
        scheduling_loader_saver = SchedulingLoaderSaver(self.main_path)

        if self.scheduling_parameters["action"] == 'generate':
            print("*****")
            print(f"Generating scheduling")
            scheduling_generator = SchedulingGenerator(
                self.taskset_set_obj,
                self.assignment_set_obj,
                self.scheduling_parameters["taskset_id"],
                self.scheduling_parameters["assignment_id"],
                self.scheduling_parameters["scheduling_id"],
                **self.scheduling_parameters["parameters"]
            )
            self.scheduling_set_obj = scheduling_generator.generate_scheduling_set()
            scheduling_loader_saver.save(self.scheduling_set_obj, self.scheduling_parameters["scheduling_id"])

        elif self.scheduling_parameters["action"] == 'open':
            print("*****")
            print(f"Opening scheduling")
            self.scheduling_set_obj = scheduling_loader_saver.load(self.scheduling_parameters["scheduling_id"])
        
        elif self.scheduling_parameters["action"] == 'none':
            print(f"None received. Pass")
        
        else:
            print(f"Invalid scheduling action: {self.scheduling_parameters['action']}")
            return