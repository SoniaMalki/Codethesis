import itertools
from pathlib import Path
import sqlite3


class ConfigGeneratorDB:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()
        # Initialiser les index globalement
        self.taskset_index = self.get_last_index("Tasksets", "taskset_id") + 1
        self.assignment_index = self.get_last_index(
            "Assignments", "assignment_id") + 1
        self.scheduling_index = self.get_last_index(
            "Schedulings", "scheduling_id") + 1

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Experiences (
                experience_id TEXT PRIMARY KEY
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Tasksets (
                taskset_id TEXT PRIMARY KEY,
                action TEXT,
                taskset_repetition INT,
                tasks_per_taskset INT,
                interference_factor FLOAT,
                probability_factor FLOAT,
                max_utilization FLOAT,
                deadline_option VARCHAR,
                max_hyperperiod INT,
                max_prime INT,
                gen_limit_exponent INT,
                number_of_cores INT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ExperienceTasksets (
                experience_id TEXT,
                taskset_id TEXT,
                PRIMARY KEY (experience_id, taskset_id),
                FOREIGN KEY (experience_id) REFERENCES Experiences(experience_id),
                FOREIGN KEY (taskset_id) REFERENCES Tasksets(taskset_id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Assignments (
                assignment_id TEXT PRIMARY KEY,
                taskset_id TEXT,
                action TEXT,
                sorting_criterion VARCHAR,
                assignment_method VARCHAR,
                number_of_cores INT,
                solving_time_limit_MILP INT,
                solver_name VARCHAR,
                FOREIGN KEY (taskset_id) REFERENCES Tasksets(taskset_id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ExperienceAssignments (
                experience_id TEXT,
                assignment_id TEXT,
                PRIMARY KEY (experience_id, assignment_id),
                FOREIGN KEY (experience_id) REFERENCES Experiences(experience_id),
                FOREIGN KEY (assignment_id) REFERENCES Assignments(assignment_id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Schedulings (
                scheduling_id TEXT PRIMARY KEY,
                assignment_id TEXT,
                taskset_id TEXT,
                action TEXT,  
                scheduling_algorithm VARCHAR,
                non_preemption_time_variant2 VARCHAR,
                solving_time_limit_MILP INT,
                solver_name VARCHAR,
                FOREIGN KEY (assignment_id) REFERENCES Assignments(assignment_id),
                FOREIGN KEY (taskset_id) REFERENCES Tasksets(taskset_id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ExperienceSchedulings (
                experience_id TEXT,
                scheduling_id TEXT,
                PRIMARY KEY (experience_id, scheduling_id),
                FOREIGN KEY (experience_id) REFERENCES Experiences(experience_id),
                FOREIGN KEY (scheduling_id) REFERENCES Schedulings(scheduling_id)
            )
        """)

    def add_experience(self, experience_id):
        """
        Ajoute une nouvelle experience à la base de données s'il n'existe pas.
        """
        try:
            self.cursor.execute(
                "INSERT INTO Experiences (experience_id) VALUES (?)",
                (experience_id,)
            )
            self.conn.commit()
            return experience_id
        except sqlite3.IntegrityError:
            print(f"L'expérience '{experience_id}' existe déjà.")
            return None

    def get_last_index(self, table_name, id_column):
        """Récupère le dernier index utilisé dans une table pour une colonne d'ID donnée."""
        self.cursor.execute(f"""
            SELECT MAX(CAST(SUBSTR({id_column}, LENGTH('{id_column.split('_')[0]}_') + 1) AS INT)) 
            FROM {table_name}
        """)
        result = self.cursor.fetchone()
        return result[0] if result[0] is not None else 0

    def taskset_exists(self, taskset_repetition, tasks_per_taskset, interference_factor, probability_factor, max_utilization, deadline_option, max_hyperperiod, max_prime, gen_limit_exponent, number_of_cores):
        """Vérifie si un taskset avec les mêmes paramètres existe déjà."""
        self.cursor.execute(
            """
            SELECT taskset_id
            FROM Tasksets
            WHERE taskset_repetition = ?
              AND tasks_per_taskset = ?
              AND interference_factor = ?
              AND probability_factor = ?
              AND max_utilization = ?
              AND deadline_option = ?
              AND max_hyperperiod = ?
              AND max_prime = ?
              AND gen_limit_exponent = ?
              AND number_of_cores = ?
            """,
            (taskset_repetition, tasks_per_taskset, interference_factor, probability_factor, max_utilization,
             deadline_option, max_hyperperiod, max_prime, gen_limit_exponent, number_of_cores)
        )
        return self.cursor.fetchone()

    def generate_tasksets(self, experience_id, taskset_params):
        for taskset_repetition, tasks_per_taskset, interference_factor, probability_factor, max_utilization_factor, deadline_option, (
            max_hyperperiod,
            max_prime,
            gen_limit_exponent,
        ) in itertools.product(
            taskset_params["taskset_repetitions"],
            taskset_params["tasks_per_taskset"],
            taskset_params["interference_factors"],
            taskset_params["probability_factors"],
            taskset_params["max_utilization_factors"],
            taskset_params["deadline_options"],
            taskset_params["prime_exponent_hyperperiod_combinations"],
        ):
            for number_of_cores in taskset_params["number_of_cores_list"]:
                # Vérifier si un taskset avec les mêmes paramètres existe déjà
                existing_taskset = self.taskset_exists(
                    taskset_repetition, tasks_per_taskset, interference_factor,
                    probability_factor, max_utilization_factor * number_of_cores, deadline_option,
                    max_hyperperiod, max_prime, gen_limit_exponent, number_of_cores
                )

                if existing_taskset:
                    # Réutiliser l'ID du taskset existant
                    taskset_id = existing_taskset[0]
                    print(f"Taskset existant réutilisé : {taskset_id}")
                else:
                    # Générer un nouvel ID de taskset
                    taskset_id = f"taskset_{self.taskset_index}"
                    self.cursor.execute(
                        """
                        INSERT INTO Tasksets (
                            taskset_id, action, taskset_repetition, tasks_per_taskset, interference_factor,
                            probability_factor, max_utilization, deadline_option, max_hyperperiod,
                            max_prime, gen_limit_exponent, number_of_cores
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            taskset_id,
                            "generate",
                            taskset_repetition,
                            tasks_per_taskset,
                            interference_factor,
                            probability_factor,
                            max_utilization_factor * number_of_cores,
                            deadline_option,
                            max_hyperperiod,
                            max_prime,
                            gen_limit_exponent,
                            number_of_cores
                        ),
                    )
                    self.taskset_index += 1  # Incrémenter l'index global

                # Lier le taskset à l'expérience
                self.cursor.execute(
                    """
                    INSERT OR IGNORE INTO ExperienceTasksets (experience_id, taskset_id) 
                    VALUES (?, ?)
                    """,
                    (experience_id, taskset_id)
                )
        self.conn.commit()

    def assignment_exists(self, taskset_id, sorting_criterion, assignment_method, number_of_cores, solving_time_limit_MILP, solver_name):
        """Vérifie si un assignment avec les mêmes paramètres existe déjà."""
        self.cursor.execute(
            """
            SELECT assignment_id
            FROM Assignments
            WHERE taskset_id = ?
              AND sorting_criterion = ?
              AND assignment_method = ?
              AND number_of_cores = ?
              AND solving_time_limit_MILP = ?
              AND solver_name = ?
            """,
            (taskset_id, sorting_criterion, assignment_method,
             number_of_cores, solving_time_limit_MILP, solver_name)
        )
        return self.cursor.fetchone()

    def generate_assignments(self, experience_id, assignment_params):
        for taskset_id in self.get_taskset_ids_for_experience(experience_id):
            for assignment_method, sorting_criterion, solving_time_limit_milp_assignment, solver_name in itertools.product(
                assignment_params["assignment_methods"],
                assignment_params["sorting_criteria"],
                assignment_params["solving_time_limit_milp_assignment"],
                assignment_params["solver_name_assignment"]
            ):
                # Vérifier si un assignment avec les mêmes paramètres existe déjà
                existing_assignment = self.assignment_exists(
                    taskset_id, sorting_criterion, assignment_method,
                    self.get_number_of_cores_from_taskset(taskset_id),
                    solving_time_limit_milp_assignment, solver_name
                )

                if existing_assignment:
                    # Réutiliser l'ID de l'assignment existant
                    assignment_id = existing_assignment[0]
                    print(f"Assignment existant réutilisé : {assignment_id}")
                else:
                    # Générer un nouvel ID d'assignment
                    assignment_id = f"assignment_{self.assignment_index}"
                    self.cursor.execute(
                        """
                        INSERT INTO Assignments (
                            assignment_id, taskset_id, action, sorting_criterion,
                            assignment_method, number_of_cores, solving_time_limit_MILP, solver_name
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            assignment_id,
                            taskset_id,
                            "generate",
                            sorting_criterion,
                            assignment_method,
                            self.get_number_of_cores_from_taskset(taskset_id),
                            solving_time_limit_milp_assignment,
                            solver_name,
                        )
                    )
                    self.assignment_index += 1  # Incrémenter l'index global

                # Lier l'assignment à l'expérience
                self.cursor.execute(
                    """
                    INSERT OR IGNORE INTO ExperienceAssignments (experience_id, assignment_id) 
                    VALUES (?, ?)
                    """,
                    (experience_id, assignment_id)
                )
        self.conn.commit()

    def scheduling_exists(self, assignment_id, taskset_id, scheduling_algorithm, non_preemption_time_variant2, solving_time_limit_MILP, solver_name):
        """Vérifie si un scheduling avec les mêmes paramètres existe déjà."""
        self.cursor.execute(
            """
            SELECT scheduling_id
            FROM Schedulings
            WHERE assignment_id = ?
              AND taskset_id = ?
              AND scheduling_algorithm = ?
              AND non_preemption_time_variant2 = ?
              AND solving_time_limit_MILP = ?
              AND solver_name = ?
            """,
            (assignment_id, taskset_id, scheduling_algorithm,
             non_preemption_time_variant2, solving_time_limit_MILP, solver_name)
        )
        return self.cursor.fetchone()

    def generate_schedulings(self, experience_id, scheduling_params):
        for assignment_id in self.get_assignment_ids_for_experience(experience_id):
            # Obtenir le taskset_id correspondant à l'assignment_id
            taskset_id = self.get_taskset_id_from_assignment(assignment_id)

            for scheduling_algorithm, non_preemption_time_variant2_options, solving_time_limit_milp_scheduling, solver_name in itertools.product(
                scheduling_params["scheduling_algorithms"],
                scheduling_params["non_preemption_time_variant2_options"],
                scheduling_params["solving_time_limit_milp_scheduling"],
                scheduling_params["solver_name_scheduling"]
            ):
                # Vérifier si un scheduling avec les mêmes paramètres existe déjà
                existing_scheduling = self.scheduling_exists(
                    assignment_id, taskset_id, scheduling_algorithm,
                    non_preemption_time_variant2_options, solving_time_limit_milp_scheduling,
                    solver_name
                )

                if existing_scheduling:
                    # Réutiliser l'ID du scheduling existant
                    scheduling_id = existing_scheduling[0]
                    print(f"Scheduling existant réutilisé : {scheduling_id}")
                else:
                    # Générer un nouvel ID de scheduling
                    scheduling_id = f"scheduling_{self.scheduling_index}"
                    self.cursor.execute(
                        """
                        INSERT INTO Schedulings (
                            scheduling_id, assignment_id, taskset_id, action, scheduling_algorithm,
                            non_preemption_time_variant2, solving_time_limit_MILP, solver_name
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            scheduling_id,
                            assignment_id,
                            taskset_id,
                            "generate",
                            scheduling_algorithm,
                            non_preemption_time_variant2_options,
                            solving_time_limit_milp_scheduling,
                            solver_name,
                        )
                    )
                    self.scheduling_index += 1  # Incrémenter l'index global

                # Lier le scheduling à l'expérience
                self.cursor.execute(
                    """
                    INSERT OR IGNORE INTO ExperienceSchedulings (experience_id, scheduling_id) 
                    VALUES (?, ?)
                    """,
                    (experience_id, scheduling_id)
                )
        self.conn.commit()

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
        return [row[0] for row in self.cursor.fetchall()]

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
        return [row[0] for row in self.cursor.fetchall()]

    def get_number_of_cores_from_taskset(self, taskset_id):
        self.cursor.execute(
            "SELECT number_of_cores FROM Tasksets WHERE taskset_id = ?",
            (taskset_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_taskset_id_from_assignment(self, assignment_id):
        self.cursor.execute(
            "SELECT taskset_id FROM Assignments WHERE assignment_id = ?",
            (assignment_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def generate_configs_from_json(self, json_data, experience_id=None):
        """
        Génère les configurations à partir d'un dictionnaire JSON.

        Args:
            json_data (dict): Le dictionnaire JSON contenant les données de configuration.
            experience_id (str, optional): La clé de l'expérience spécifique à générer.
                                             Si None, toutes les expériences du JSON seront générées.
        """
        if experience_id:
            # Générer uniquement l'expérience spécifiée
            if experience_id in json_data:
                experience_data = {experience_id: json_data[experience_id]}
            else:
                print(
                    f"Erreur: La clé d'expérience '{experience_id}' est introuvable dans les données JSON.")
                return
        else:
            # Générer toutes les expériences du JSON
            experience_data = json_data

        for experience_id, experience_data in experience_data.items():
            # experience_id est maintenant la clé du dictionnaire
            self.add_experience(experience_id)
            config_params = experience_data["config_parameters"]
            self.generate_tasksets(
                experience_id, config_params["taskset_parameters"])
            self.generate_assignments(
                experience_id, config_params["assignment_parameters"])
            self.generate_schedulings(
                experience_id, config_params["scheduling_parameters"])

    def close_connection(self):
        self.conn.close()
