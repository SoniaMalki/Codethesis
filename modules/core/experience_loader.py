import sqlite3
from pathlib import Path
from modules.core.experience import Experience


class ExperienceLoader:
    def __init__(self, db_path, experience_id=None):
        self.db_path = db_path
        self.experience_id = experience_id
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def load(self, config_id):
        """Charge les données de configuration à partir de la base de données.

        Args:
            config_id (str): ID de la configuration à charger (ex: "taskset_1").

        Returns:
            Experience: Un objet Experience contenant les données chargées, ou None si aucune donnée n'est trouvée.
        """
        taskset_params, assignment_params, scheduling_params = None, None, None

        # Déterminer le type de configuration à partir de config_id
        config_type = config_id.split('_')[0]

        if config_type == "taskset":
            # Charger uniquement les paramètres du taskset
            self.cursor.execute(
                """
                SELECT T.taskset_id, T.action, T.taskset_repetition, T.tasks_per_taskset, T.interference_factor, 
                       T.probability_factor, T.max_utilization, T.deadline_option, T.max_hyperperiod, 
                       T.max_prime, T.gen_limit_exponent, T.result_file_path
                FROM Tasksets T
                JOIN ExperienceTasksets ET ON T.taskset_id = ET.taskset_id
                WHERE ET.experience_id = ? AND T.taskset_id = ?
                """,
                (self.experience_id, config_id)
            )
            taskset_data = self.cursor.fetchone()

            if taskset_data:
                taskset_params = {
                    "action": taskset_data[1],
                    "taskset_id": taskset_data[0],
                    "parameters": {
                        "taskset_repetition": taskset_data[2],
                        "tasks_per_taskset": taskset_data[3],
                        "interference_factor": taskset_data[4],
                        "probability_factor": taskset_data[5],
                        "max_utilization": taskset_data[6],
                        "taskset_options": {
                            "deadline_option": taskset_data[7],
                            "max_hyperperiod": taskset_data[8],
                            "max_prime": taskset_data[9],
                            "gen_limit_exponent": taskset_data[10]
                        }
                    },
                    "result_file_path": taskset_data[11]
                }
                # Ajouter assignment et scheduling avec action "none"
                assignment_params = {"action": "none"}
                scheduling_params = {"action": "none"}

        elif config_type == "assignment":
            # Charger uniquement les paramètres d'assignation
            self.cursor.execute(
                """
                SELECT A.assignment_id, A.action, A.sorting_criterion, A.assignment_method,
                       A.number_of_cores, A.solving_time_limit_MILP, A.solver_name, A.result_file_path, A.taskset_id
                FROM Assignments A
                JOIN ExperienceAssignments EA ON A.assignment_id = EA.assignment_id
                WHERE EA.experience_id = ? AND A.assignment_id = ?
                """,
                (self.experience_id, config_id)
            )
            assignment_data = self.cursor.fetchone()

            if assignment_data:
                assignment_params = {
                    "action": assignment_data[1],
                    "assignment_id": assignment_data[0],
                    "taskset_id": self.get_taskset_id_from_assignment(config_id),
                    "parameters": {
                        "sorting_criterion": assignment_data[2],
                        "assignment_method": assignment_data[3],
                        "number_of_cores": assignment_data[4],
                        "assignment_options": {
                            "solving_time_limit_MILP": assignment_data[5],
                            "solver_name": assignment_data[6]
                        }
                    },
                    "result_file_path": assignment_data[7]
                }
                # Ajouter taskset avec action "open" et scheduling avec action "none"
                taskset_params = {"action": "open",
                                  "taskset_id": assignment_data[8]}
                scheduling_params = {"action": "none"}

        elif config_type == "scheduling":
            # Charger uniquement les paramètres de planification
            self.cursor.execute(
                """
                SELECT S.scheduling_id, S.action, S.scheduling_algorithm, S.non_preemption_time_variant2,
                       S.solving_time_limit_MILP, S.solver_name, S.result_file_path, S.taskset_id, S.assignment_id
                FROM Schedulings S
                JOIN ExperienceSchedulings ES ON S.scheduling_id = ES.scheduling_id
                WHERE ES.experience_id = ? AND S.scheduling_id = ?
                """,
                (self.experience_id, config_id)
            )
            scheduling_data = self.cursor.fetchone()

            if scheduling_data:
                scheduling_params = {
                    "action": scheduling_data[1],
                    "scheduling_id": scheduling_data[0],
                    "taskset_id": self.get_taskset_id_from_scheduling(config_id),
                    "assignment_id": self.get_assignment_id_from_scheduling(config_id),
                    "parameters": {
                        "scheduling_algorithm": scheduling_data[2],
                        "scheduling_options": {
                            "non_preemption_time_variant2": scheduling_data[3],
                            "solving_time_limit_MILP": scheduling_data[4],
                            "solver_name": scheduling_data[5]
                        }
                    },
                    "result_file_path": scheduling_data[6]
                }
                # Ajouter taskset et assignment avec action "open"
                taskset_params = {"action": "open",
                                  "taskset_id": scheduling_data[7]}
                assignment_params = {"action": "open",
                                     "assignment_id": scheduling_data[8]}

        # Retourner None si aucun paramètre n'a été chargé
        if taskset_params is None and assignment_params is None and scheduling_params is None:
            return None

        return Experience(
            taskset_parameters=taskset_params,
            assignment_parameters=assignment_params,
            scheduling_parameters=scheduling_params,
            main_path=Path(self.db_path).parent,
            db_path=self.db_path
        )

    def get_experience_ids(self):
        """Récupère la liste des IDs d'expérience disponibles dans la base de données."""
        self.cursor.execute("SELECT experience_id FROM Experiences")
        return [row[0] for row in self.cursor.fetchall()]

    def get_taskset_id_from_assignment(self, assignment_id):
        self.cursor.execute(
            "SELECT taskset_id FROM Assignments WHERE assignment_id = ?",
            (assignment_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_taskset_id_from_scheduling(self, scheduling_id):
        self.cursor.execute(
            "SELECT T.taskset_id FROM Tasksets T JOIN Assignments A ON T.taskset_id = A.taskset_id JOIN Schedulings S ON A.assignment_id = S.assignment_id WHERE S.scheduling_id = ?",
            (scheduling_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_assignment_id_from_scheduling(self, scheduling_id):
        self.cursor.execute(
            "SELECT assignment_id FROM Schedulings WHERE scheduling_id = ?",
            (scheduling_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_config_ids(self, config_type="taskset"):
        """Récupère les IDs de configuration pour un type donné et une expérience donnée.

        Args:
            config_type (str, optional): Le type de configuration ('taskset', 'assignment', 'scheduling'). 
                                         Par défaut à 'taskset'.

        Returns:
            list: Une liste d'IDs de configuration.
        """
        if not self.experience_id:
            return []

        if config_type == "taskset":
            return self.get_taskset_ids_for_experience(self.experience_id)
        elif config_type == "assignment":
            return self.get_assignment_ids_for_experience(self.experience_id)
        elif config_type == "scheduling":
            return self.get_scheduling_ids_for_experience(self.experience_id)
        else:
            print(f"Erreur : Type de configuration invalide '{config_type}'.")
            return []

    def get_taskset_ids_for_experience(self, experience_id):
        self.cursor.execute(
            """
            SELECT T.taskset_id 
            FROM Tasksets T 
            JOIN ExperienceTasksets ET ON T.taskset_id = ET.taskset_id 
            WHERE ET.experience_id = ?
            """,
            (experience_id,)
        )
        taskset_ids = [row[0] for row in self.cursor.fetchall()]

        # Trier numériquement les taskset_id
        taskset_ids.sort(key=lambda x: int(x.split('_')[1]))

        return taskset_ids

    def get_assignment_ids_for_experience(self, experience_id):
        self.cursor.execute(
            """
            SELECT A.assignment_id
            FROM Assignments A
            JOIN ExperienceAssignments EA ON A.assignment_id = EA.assignment_id
            WHERE EA.experience_id = ?
            """,
            (experience_id,)
        )
        assignment_ids = [row[0] for row in self.cursor.fetchall()]

        # Trier numériquement les assignment_id
        assignment_ids.sort(key=lambda x: int(x.split('_')[1]))

        return assignment_ids

    def get_scheduling_ids_for_experience(self, experience_id):
        self.cursor.execute(
            """
            SELECT S.scheduling_id
            FROM Schedulings S
            JOIN ExperienceSchedulings ES ON S.scheduling_id = ES.scheduling_id
            WHERE ES.experience_id = ?
            """,
            (experience_id,)
        )
        scheduling_ids = [row[0] for row in self.cursor.fetchall()]

        # Trier numériquement les scheduling_id
        scheduling_ids.sort(key=lambda x: int(x.split('_')[1]))

        return scheduling_ids

    def close_connection(self):
        self.conn.close()
