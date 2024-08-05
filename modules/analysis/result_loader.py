import os
from pathlib import Path
import pickle
import json
import sqlite3
import time

from modules.scheduling.composite_scheduling import CompositeScheduling
from modules.scheduling.scheduling import Scheduling


class ResultLoader:
    def __init__(self, db_path, experience_id):
        self.db_path = db_path
        self.experience_id = experience_id
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def load_data(self, file_path):
        with open(file_path, "rb") as f:
            return pickle.load(f)

    def get_config_ids(self, config_type):
        if config_type == "taskset":
            self.cursor.execute(
                "SELECT taskset_id FROM ExperienceTasksets WHERE experience_id = ?",
                (self.experience_id,)
            )
        elif config_type == "assignment":
            self.cursor.execute(
                "SELECT assignment_id FROM ExperienceAssignments WHERE experience_id = ?",
                (self.experience_id,)
            )
        elif config_type == "scheduling":
            self.cursor.execute(
                "SELECT scheduling_id FROM ExperienceSchedulings WHERE experience_id = ?",
                (self.experience_id,)
            )
        else:
            print(f"Erreur : Type de configuration invalide '{config_type}'.")
            return []

        return [row[0] for row in self.cursor.fetchall()]

    def load_results(self):
        taskset_sets = []
        assignment_sets = []
        scheduling_sets = []

        taskset_ids = self.get_config_ids("taskset")
        assignment_ids = self.get_config_ids("assignment")
        scheduling_ids = self.get_config_ids("scheduling")

        result_directory = Path(self.db_path).parent / "results"

        for taskset_id in taskset_ids:

            file_path = result_directory / "tasksets" / f"{taskset_id}.pkl"
            if file_path.exists():
                data_obj = self.load_data(file_path)
                taskset_sets.append(data_obj)

        for assignment_id in assignment_ids:
            file_path = result_directory / \
                "assignments" / f"{assignment_id}.pkl"
            if file_path.exists():
                data_obj = self.load_data(file_path)
                assignment_sets.append(data_obj)

        for scheduling_id in scheduling_ids:
            file_path = result_directory / \
                "schedulings" / f"{scheduling_id}.pkl"
            if file_path.exists():
                data_obj = self.load_data(file_path)
                scheduling_sets.append(data_obj)

        return taskset_sets, assignment_sets, scheduling_sets

    def close_connection(self):
        self.conn.close()
