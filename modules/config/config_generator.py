import itertools
from pathlib import Path
import sqlite3
import time


class ConfigGenerator:
    def __init__(self, db_path, experience_data):
        print("Initializing ConfigGenerator")
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

        # Vérifier si config_parameters est présent
        if "config_parameters" not in experience_data:
            raise ValueError(
                "config_parameters dictionary is missing in experience data."
            )

        self.config_parameters = experience_data["config_parameters"]

        # Récupérer tous les paramètres depuis experience_data
        for param_section in ["taskset_parameters", "assignment_parameters", "scheduling_parameters"]:
            for param_name, param_value in self.config_parameters[param_section].items():
                setattr(self, param_name, param_value)

        # Vérification de tous les paramètres obligatoires
        required_params = [
            "taskset_repetitions",
            "tasks_per_taskset",
            "interference_factors",
            "probability_factors",
            "max_utilization_factors",
            "deadline_options",
            "prime_exponent_hyperperiod_combinations",
            "number_of_cores_list",
            "assignment_methods",
            "sorting_criteria",
            "scheduling_algorithms",
            "non_preemption_time_variant2_options",
            "solving_time_limit_milp_assignment",
            "solving_time_limit_milp_scheduling"
        ]
        for param_name in required_params:
            if getattr(self, param_name) is None:
                raise ValueError(
                    f"Paramètre obligatoire manquant dans experience.json: {param_name}")

        # Dictionnaire pour les paramètres optionnels
        self.optional_params = {
            "sorting_criteria": {
                method: self.sorting_criteria if method != "Wmin" else [""]
                for method in self.assignment_methods
            },
            "solving_time_limit_milp_assignment": {
                method: self.solving_time_limit_milp_assignment
                if method in ["Wmin", "Citta"]
                else [""]
                for method in self.assignment_methods
            },
            "solver_name_assignment": {
                method: self.solver_name_assignment
                if method in ["Wmin", "Citta"]
                else [""]
                for method in self.assignment_methods
            },
            "non_preemption_time_variant2_options": {
                algorithm: self.non_preemption_time_variant2_options
                if algorithm
                in [
                    "EarliestDeadlineFirstVariant2",
                    "DeadlineMonotonicVariant2",
                    "CombinedScheduler",
                    "Rhma",
                ]
                else [""]
                for algorithm in self.scheduling_algorithms
            },
            "solving_time_limit_milp_scheduling": {
                algorithm: self.solving_time_limit_milp_scheduling
                if algorithm == "Rhma"
                else [""]
                for algorithm in self.scheduling_algorithms
            },
            "solver_name_scheduling": {
                algorithm: self.solver_name_scheduling
                if algorithm == "Rhma"
                else [""]
                for algorithm in self.scheduling_algorithms
            },
        }
        # Initialiser les index globalement
        self.taskset_index = self.get_last_index("Tasksets", "taskset_id") + 1
        self.assignment_index = self.get_last_index(
            "Assignments", "assignment_id") + 1
        self.scheduling_index = self.get_last_index(
            "Schedulings", "scheduling_id") + 1
        print("ConfigGenerator initialized successfully")

    def create_tables(self):
        print("Creating tables if not exist")
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
                number_of_cores INT,
                result_file_path TEXT
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
                result_file_path TEXT,
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
                result_file_path TEXT,
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
        print("Tables created or verified successfully")

    def add_experience(self, experience_id):
        """
        Ajoute une nouvelle experience à la base de données s'il n'existe pas.
        """
        print(f"Adding experience: {experience_id}")
        try:
            self.cursor.execute(
                "INSERT INTO Experiences (experience_id) VALUES (?)",
                (experience_id,)
            )
            self.conn.commit()
            print(f"Experience {experience_id} added successfully")
            return experience_id
        except sqlite3.IntegrityError:
            print(f"L'expérience '{experience_id}' existe déjà.")
            return None

    def get_last_index(self, table_name, id_column):
        """Récupère le dernier index utilisé dans une table pour une colonne d'ID donnée."""
        print(f"Getting last index from table {table_name}")
        self.cursor.execute(f"""
            SELECT MAX(CAST(SUBSTR({id_column}, LENGTH('{id_column.split('_')[0]}_') + 1) AS INT)) 
            FROM {table_name}
        """)
        result = self.cursor.fetchone()
        print(
            f"Last index for {table_name} is {result[0] if result[0] is not None else 0}")
        return result[0] if result[0] is not None else 0

    def taskset_exists(self, taskset_repetition, tasks_per_taskset, interference_factor, probability_factor, max_utilization, deadline_option, max_hyperperiod, max_prime, gen_limit_exponent, number_of_cores):
        """Vérifie si un taskset avec les mêmes paramètres existe déjà."""
        print("Checking if taskset exists")
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
        result = self.cursor.fetchone()
        print(f"Taskset exists: {result is not None}")
        return result

    def generate_tasksets(self, experience_id):
        print(f"Generating taskset config for experience {experience_id}")
        for repetition, tasks, interference, probability, util_factor, deadline, (
            hyperperiod,
            prime,
            exponent,
        ) in itertools.product(
            self.taskset_repetitions,
            self.tasks_per_taskset,
            self.interference_factors,
            self.probability_factors,
            self.max_utilization_factors,
            self.deadline_options,
            self.prime_exponent_hyperperiod_combinations,
        ):
            for cores in self.number_of_cores_list:
                # Vérifier si un taskset avec les mêmes paramètres existe déjà
                existing_taskset = self.taskset_exists(
                    repetition, tasks, interference,
                    probability, util_factor * cores, deadline,
                    hyperperiod, prime, exponent, cores
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
                            max_prime, gen_limit_exponent, number_of_cores, result_file_path
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            taskset_id,
                            "generate",
                            repetition,
                            tasks,
                            interference,
                            probability,
                            util_factor * cores,
                            deadline,
                            hyperperiod,
                            prime,
                            exponent,
                            cores,
                            "",
                        ),
                    )
                    self.taskset_index += 1
                    print(f"New taskset generated with id: {taskset_id}")

                # Lier le taskset à l'expérience
                self.cursor.execute(
                    """
                    INSERT OR IGNORE INTO ExperienceTasksets (experience_id, taskset_id) 
                    VALUES (?, ?)
                    """,
                    (experience_id, taskset_id)
                )
        self.conn.commit()
        print(
            f"Taskset config generation for experience {experience_id} completed")

    def assignment_exists(self, taskset_id, sorting_criterion, assignment_method, number_of_cores, solving_time_limit_MILP, solver_name):
        """Vérifie si un assignment avec les mêmes paramètres existe déjà."""
        print(f"Checking if assignment exists for taskset_id: {taskset_id}")
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
        result = self.cursor.fetchone()
        print(f"Assignment exists: {result is not None}")
        return result

    def generate_assignments(self, experience_id):
        print(f"Generating assignment config for experience {experience_id}")
        for taskset_id in self.get_taskset_ids_for_experience(experience_id):
            cores = self.get_number_of_cores_from_taskset(taskset_id)
            for method in self.assignment_methods:
                for sorting, solving_time, solver_name in itertools.product(
                    self.optional_params["sorting_criteria"][method],
                    self.optional_params["solving_time_limit_milp_assignment"][method],
                    self.optional_params["solver_name_assignment"][method]
                ):
                    # Vérifier si un assignment avec les mêmes paramètres existe déjà
                    existing_assignment = self.assignment_exists(
                        taskset_id, sorting, method, cores, solving_time, solver_name
                    )

                    if existing_assignment:
                        # Réutiliser l'ID de l'assignment existant
                        assignment_id = existing_assignment[0]
                        print(
                            f"Assignment existant réutilisé : {assignment_id}")
                    else:
                        # Générer un nouvel ID d'assignment
                        assignment_id = f"assignment_{self.assignment_index}"
                        self.cursor.execute(
                            """
                            INSERT INTO Assignments (
                                assignment_id, taskset_id, action, sorting_criterion,
                                assignment_method, number_of_cores, solving_time_limit_MILP, solver_name, result_file_path
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                assignment_id,
                                taskset_id,
                                "generate",
                                sorting,
                                method,
                                cores,
                                solving_time,
                                solver_name,
                                "",
                            )
                        )
                        self.assignment_index += 1  # Incrémenter l'index global
                        print(
                            f"New assignment generated with id: {assignment_id}")

                    # Lier l'assignment à l'expérience
                    self.cursor.execute(
                        """
                        INSERT OR IGNORE INTO ExperienceAssignments (experience_id, assignment_id) 
                        VALUES (?, ?)
                        """,
                        (experience_id, assignment_id)
                    )
        self.conn.commit()
        print(
            f"Assignment config generation for experience {experience_id} completed")

    def scheduling_exists(self, assignment_id, taskset_id, scheduling_algorithm, non_preemption_time_variant2, solving_time_limit_MILP, solver_name):
        """Vérifie si un scheduling avec les mêmes paramètres existe déjà."""
        print(
            f"Checking if scheduling exists for assignment_id: {assignment_id}")
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
        result = self.cursor.fetchone()
        print(f"Scheduling exists: {result is not None}")
        return result

    def generate_schedulings(self, experience_id):
        print(f"Generating scheduling config for experience {experience_id}")
        for assignment_id in self.get_assignment_ids_for_experience(experience_id):
            taskset_id = self.get_taskset_id_from_assignment(assignment_id)
            for algorithm in self.scheduling_algorithms:
                for non_preemption, solving_time, solver_name in itertools.product(
                    self.optional_params["non_preemption_time_variant2_options"][algorithm],
                    self.optional_params["solving_time_limit_milp_scheduling"][algorithm],
                    self.optional_params["solver_name_scheduling"][algorithm],
                ):
                    # Vérifier si un scheduling avec les mêmes paramètres existe déjà
                    existing_scheduling = self.scheduling_exists(
                        assignment_id, taskset_id, algorithm, non_preemption, solving_time, solver_name
                    )

                    if existing_scheduling:
                        # Réutiliser l'ID du scheduling existant
                        scheduling_id = existing_scheduling[0]
                        print(
                            f"Scheduling existant réutilisé : {scheduling_id}")
                    else:
                        # Générer un nouvel ID de scheduling
                        scheduling_id = f"scheduling_{self.scheduling_index}"
                        self.cursor.execute(
                            """
                            INSERT INTO Schedulings (
                                scheduling_id, assignment_id, taskset_id, action, scheduling_algorithm,
                                non_preemption_time_variant2, solving_time_limit_MILP, solver_name, result_file_path
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                scheduling_id,
                                assignment_id,
                                taskset_id,
                                "generate",
                                algorithm,
                                non_preemption,
                                solving_time,
                                solver_name,
                                "",
                            )
                        )
                        self.scheduling_index += 1  # Incrémenter l'index global
                        print(
                            f"New scheduling generated with id: {scheduling_id}")

                    # Lier le scheduling à l'expérience
                    self.cursor.execute(
                        """
                        INSERT OR IGNORE INTO ExperienceSchedulings (experience_id, scheduling_id) 
                        VALUES (?, ?)
                        """,
                        (experience_id, scheduling_id)
                    )
        self.conn.commit()
        print(
            f"Scheduling config generation for experience {experience_id} completed")

    def get_taskset_ids_for_experience(self, experience_id):
        print(f"Fetching taskset ids for experience {experience_id}")
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

        print(f"Taskset ids for experience {experience_id}: {taskset_ids}")
        return taskset_ids

    def get_assignment_ids_for_experience(self, experience_id):
        print(f"Fetching assignment ids for experience {experience_id}")
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

        print(
            f"Assignment ids for experience {experience_id}: {assignment_ids}")
        return assignment_ids

    def get_number_of_cores_from_taskset(self, taskset_id):
        print(f"Fetching number of cores for taskset {taskset_id}")
        self.cursor.execute(
            "SELECT number_of_cores FROM Tasksets WHERE taskset_id = ?",
            (taskset_id,)
        )
        result = self.cursor.fetchone()
        cores = result[0] if result else None
        print(f"Number of cores for taskset {taskset_id}: {cores}")
        return cores

    def get_taskset_id_from_assignment(self, assignment_id):
        print(f"Fetching taskset id for assignment {assignment_id}")
        self.cursor.execute(
            "SELECT taskset_id FROM Assignments WHERE assignment_id = ?",
            (assignment_id,)
        )
        result = self.cursor.fetchone()
        taskset_id = result[0] if result else None
        print(f"Taskset id for assignment {assignment_id}: {taskset_id}")
        return taskset_id

    def generate_configs_from_json(self, json_data, experience_id=None):
        """
        Génère les configurations à partir d'un dictionnaire JSON.

        Args:
            json_data (dict): Le dictionnaire JSON contenant les données de configuration.
            experience_id (str, optional): La clé de l'expérience spécifique à générer.
                                             Si None, toutes les expériences du JSON seront générées.
        """
        print("Generating configs from JSON")
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
            print(f"Processing experience {experience_id}")
            # experience_id est maintenant la clé du dictionnaire
            self.add_experience(experience_id)
            config_params = experience_data["config_parameters"]
            self.generate_tasksets(experience_id)
            self.generate_assignments(experience_id)
            self.generate_schedulings(experience_id)
            print(f"Experience {experience_id} processed successfully")

    def close_connection(self):
        print("Closing database connection")
        self.conn.close()
        print("Database connection closed")
