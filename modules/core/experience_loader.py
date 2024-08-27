from pathlib import Path
from modules.core.experience import Experience
from modules.utils.db_utils import DBUtils


class ExperienceLoader:
    def __init__(self, db_path, result_path, experience_id=None):
        print(
            f"Initializing ExperienceLoader for experience ID: {experience_id}")
        self.db_utils = DBUtils(db_path)
        self.result_path = result_path
        self.experience_id = experience_id
        print("ExperienceLoader initialized successfully")

    def load(self, config_id):
        """Charge les données de configuration à partir de la base de données.

        Args:
            config_id (str): ID de la configuration à charger (ex: "taskset_1").

        Returns:
            Experience: Un objet Experience contenant les données chargées, ou None si aucune donnée n'est trouvée.
        """
        print(f"Loading configuration for ID: {config_id}")
        taskset_params, assignment_params, scheduling_params = None, None, None

        # Déterminer le type de configuration à partir de config_id
        config_type = config_id.split('_')[0]

        if config_type == "taskset":
            print("Loading taskset configuration")
            taskset_data = self.db_utils.get_taskset_data(config_id)

            if taskset_data:
                taskset_data = taskset_data[0]  # Extract the single row
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
            print("Loading assignment configuration")
            assignment_data = self.db_utils.get_assignment_data(config_id)

            if assignment_data:
                assignment_data = assignment_data[0]
                assignment_params = {
                    "action": assignment_data[1],
                    "assignment_id": assignment_data[0],
                    "taskset_id": self.db_utils.get_taskset_id_from_assignment(config_id),
                    "parameters": {
                        "sorting_criterion": assignment_data[2],
                        "assignment_method": assignment_data[3],
                        "number_of_cores": assignment_data[4],
                        "assignment_options": {
                            "threads": assignment_data[5],
                            "solving_time_limit_MILP": assignment_data[6],
                            "solver_name": assignment_data[7]
                        }
                    },
                    "result_file_path": assignment_data[8]
                }
                # Ajouter taskset avec action "open" et scheduling avec action "none"
                taskset_params = {"action": "open",
                                  "taskset_id": assignment_data[9]}
                scheduling_params = {"action": "none"}

        elif config_type == "scheduling":
            print("Loading scheduling configuration")
            scheduling_data = self.db_utils.get_scheduling_data(config_id)

            if scheduling_data:
                scheduling_data = scheduling_data[0]
                scheduling_params = {
                    "action": scheduling_data[1],
                    "scheduling_id": scheduling_data[0],
                    "taskset_id": self.db_utils.get_taskset_and_assignment_ids_from_scheduling(config_id)[0],
                    "assignment_id": self.db_utils.get_taskset_and_assignment_ids_from_scheduling(config_id)[1],
                    "parameters": {
                        "scheduling_algorithm": scheduling_data[2],
                        "scheduling_options": {
                            "non_preemption_time_variant2": scheduling_data[3],
                            "threads": scheduling_data[4],
                            "solving_time_limit_MILP": scheduling_data[5],
                            "solver_name": scheduling_data[6]
                        }
                    },
                    "result_file_path": scheduling_data[7]
                }
                # Ajouter taskset et assignment avec action "open"
                taskset_params = {"action": "open",
                                  "taskset_id": scheduling_data[8]}
                assignment_params = {"action": "open",
                                     "assignment_id": scheduling_data[9]}

        # Retourner None si aucun paramètre n'a été chargé
        if taskset_params is None and assignment_params is None and scheduling_params is None:
            print(f"No configuration found for ID: {config_id}")
            return None

        print(f"Configuration for ID: {config_id} loaded successfully")
        return Experience(
            taskset_parameters=taskset_params,
            assignment_parameters=assignment_params,
            scheduling_parameters=scheduling_params,
            main_path=Path(self.db_utils.db_path).parent,
            db_path=self.db_utils.db_path,
            result_path=self.result_path
        )

    def get_experience_ids(self):
        """Récupère la liste des IDs d'expérience disponibles dans la base de données."""
        return self.db_utils.get_experience_ids()

    def get_config_ids(self, config_type="taskset"):
        """Récupère les IDs de configuration pour un type donné et une expérience donnée.

        Args:
            config_type (str, optional): Le type de configuration ('taskset', 'assignment', 'scheduling').
                                         Par défaut à 'taskset'.

        Returns:
            list: Une liste d'IDs de configuration.
        """
        print(f"Fetching configuration IDs for type: {config_type}")
        if not self.experience_id:
            return []

        return self.db_utils.get_config_ids_for_experience(self.experience_id, config_type)
