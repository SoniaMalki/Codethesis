import json
import os
from pathlib import Path
import time
import numpy as np

from modules.taskset.taskset_set_manual import TasksetSetManual
from modules.taskset.taskset_set_generator import TasksetSetGenerator
from modules.taskset.taskset_set_loader_saver import TasksetSetLoaderSaver
from modules.assignment.assignment_generator import AssignmentGenerator
from modules.assignment.assignment_loader_saver import AssignmentLoaderSaver
from modules.scheduling.scheduling_generator import SchedulingGenerator
from modules.scheduling.scheduling_loader_saver import SchedulingLoaderSaver
from modules.utils.db_utils import DBUtils


class Experience:
    def __init__(self, taskset_parameters, assignment_parameters, scheduling_parameters, main_path, db_path):
        """
        Initializes an Experience object.

        Args:
            taskset_parameters (dict): A dictionary containing taskset configuration.
            assignment_parameters (dict): A dictionary containing assignment configuration.
            scheduling_parameters (dict): A dictionary containing scheduling configuration.
            db_path (Path): Chemin vers la base de données.
        """
        self.taskset_parameters = taskset_parameters
        self.assignment_parameters = assignment_parameters
        self.scheduling_parameters = scheduling_parameters

        self.main_path = main_path
        self.db_path = db_path

        self.taskset_set_obj = None
        self.assignment_set_obj = None
        self.scheduling_set_obj = None

        self.db_utils = DBUtils(self.db_path)

    def process(self):
        """Processes the experience, generating tasksets, assignments, and schedulings as needed."""
        print("Processing Experience")
        self.process_taskset()
        self.process_assignment()
        self.process_scheduling()

    def process_taskset(self):
        """Handles the generation or opening of the taskset."""
        if self.taskset_parameters["action"] == 'none':
            print(f"Taskset Action : None received. Pass")

        elif self.taskset_parameters["action"] == 'open' or self.taskset_parameters["action"] == 'generate':
            taskset_loader_saver = TasksetSetLoaderSaver(
                self.main_path, self.db_path)

            # Vérifier si un chemin de résultat est enregistré dans la base de données
            result_file_path = self.db_utils.get_result_file_path(
                self.taskset_parameters["taskset_id"], "taskset"
            )

            if result_file_path:
                if self.taskset_parameters["action"] != "open":
                    print("*****")
                    print(
                        f"Existing taskset from {result_file_path} changing action to open")
                    self.taskset_parameters["action"] = "open"

            if self.taskset_parameters["action"] == 'generate':
                print("*****")
                print(f"Generating taskset")
                taskset_generator = TasksetSetGenerator(
                    self.main_path,
                    self.taskset_parameters["taskset_id"], **self.taskset_parameters["parameters"])
                self.taskset_set_obj = taskset_generator.generate_taskset_set()
                taskset_loader_saver.save(self.taskset_set_obj)

            elif self.taskset_parameters["action"] == 'open':
                print("*****")
                print(f"Opening taskset")
                self.taskset_set_obj = taskset_loader_saver.load(
                    self.taskset_parameters["taskset_id"])

            elif self.taskset_parameters["action"] == 'manual':
                print("*****")
                print(f"Creating taskset manually")
                taskset_manual = TasksetSetManual(
                    taskset_id=self.taskset_parameters["taskset_id"],
                    wcet_list=self.taskset_parameters["parameters"]["wcet"],
                    deadline_list=self.taskset_parameters["parameters"]["deadline"],
                    period_list=self.taskset_parameters["parameters"]["period"],
                    interference_list=self.taskset_parameters["parameters"]["interference"],
                    utilization_list=self.taskset_parameters["parameters"]["utilization"],
                )
                self.taskset_set_obj = taskset_manual.create_taskset_set()
                taskset_loader_saver.save(self.taskset_set_obj)

        else:
            print(
                f"Invalid taskset action: {self.taskset_parameters['action']}")
            return

    def process_assignment(self):
        """Handles the generation or opening of the assignment."""
        if self.assignment_parameters["action"] == 'none':
            print(f"Assignment Action : None received. Pass")

        elif self.assignment_parameters["action"] == 'open' or self.assignment_parameters["action"] == 'generate':
            assignment_loader_saver = AssignmentLoaderSaver(
                self.main_path, self.db_path)

            # Vérifier si un chemin de résultat est enregistré dans la base de données
            result_file_path = self.db_utils.get_result_file_path(
                self.assignment_parameters["assignment_id"], "assignment"
            )

            if result_file_path:
                if self.assignment_parameters["action"] != "open":
                    print("*****")
                    print(
                        f"Existing assignment from {result_file_path} changing action to open")
                    self.assignment_parameters["action"] = "open"

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
                assignment_loader_saver.save(
                    self.assignment_set_obj, self.assignment_parameters["assignment_id"])

            elif self.assignment_parameters["action"] == 'open':
                print("*****")
                print(f"Opening assignment")
                self.assignment_set_obj = assignment_loader_saver.load(
                    self.assignment_parameters["assignment_id"])

        else:
            print(
                f"Invalid assignment action: {self.assignment_parameters['action']}")
            return

    def process_scheduling(self):
        """Handles the generation or opening of the scheduling."""
        if self.scheduling_parameters["action"] == 'none':
            print(f"Scheduling Action : None received. Pass")

        elif self.scheduling_parameters["action"] == 'open' or self.scheduling_parameters["action"] == 'generate':
            scheduling_loader_saver = SchedulingLoaderSaver(
                self.main_path, self.db_path)

            # Vérifier si un chemin de résultat est enregistré dans la base de données
            result_file_path = self.db_utils.get_result_file_path(
                self.scheduling_parameters["scheduling_id"], "scheduling"
            )

            if result_file_path:
                if self.scheduling_parameters["action"] != "open":
                    print("*****")
                    print(
                        f"Existing scheduling from {result_file_path} changing action to open")
                    self.scheduling_parameters["action"] = "open"
            else:
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
                    scheduling_loader_saver.save(
                        self.scheduling_set_obj, self.scheduling_parameters["scheduling_id"])

                elif self.scheduling_parameters["action"] == 'open':
                    print("*****")
                    print(f"Opening scheduling")
                    self.scheduling_set_obj = scheduling_loader_saver.load(
                        self.scheduling_parameters["scheduling_id"])
        else:
            print(
                f"Invalid scheduling action: {self.scheduling_parameters['action']}")
            return
