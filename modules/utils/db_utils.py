import sqlite3
import time


class DBUtils:
    def __init__(self, db_path, assignment_algorithm_priority=[
            "WorstFitAssigner", "FirstFitAssigner", "BestFitAssigner", "Wmin", "Citta"], scheduling_algorithm_priority=["EarliestDeadlineFirst", "EarliestDeadlineFirstVariant1", "EarliestDeadlineFirstVariant2",
                                                                                                                        "DeadlineMonotonic", "DeadlineMonotonicVariant1", "DeadlineMonotonicVariant2", "CombinedScheduler", "Rhma"]):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # Store algorithm priority lists as attributes
        self.assignment_algorithm_priority = assignment_algorithm_priority
        self.scheduling_algorithm_priority = scheduling_algorithm_priority

    def execute_with_retry(self, query, params=None, max_retries=100, delay=1):
        """
        Execute a SQL query with retry logic in case of a database lock.

        :param query: The SQL query to execute.
        :param params: Optional tuple or dictionary of parameters to use with the query.
        :param max_retries: Maximum number of retry attempts (default: 100).
        :param delay: Delay in seconds between retries (default: 1 second).
        :return: Result of the query execution or raises an exception after max retries.
        """
        retries = 0
        success = False

        while retries < max_retries and not success:
            try:
                if params:
                    self.cursor.execute(query, params)
                else:
                    self.cursor.execute(query)
                return self.cursor.fetchall()  # Return the result of the query
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    retries += 1
                    print(
                        f"Database is locked. Retrying {retries}/{max_retries} in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise  # Re-raise the exception if it's not a locking issue

        if retries >= max_retries:
            raise sqlite3.OperationalError(
                "Max retries reached. Database is still locked.")

    def get_result_file_path(self, config_id, config_type):
        """Récupère le chemin du fichier de résultat pour une configuration donnée dans la base de données."""
        query = f"""
            SELECT result_file_path
            FROM {config_type.capitalize()}s
            WHERE {config_type}_id = ?
            """
        result = self.execute_with_retry(query, (config_id,))
        return result[0][0] if result else None

    def update_result_file_path(self, config_id, config_type, file_path):
        """Met à jour le chemin du fichier de résultat pour une configuration donnée."""
        query = f"""
            UPDATE {config_type.capitalize()}s
            SET result_file_path = ?
            WHERE {config_type}_id = ?
        """
        self.execute_with_retry(query, (file_path, config_id))
        self.conn.commit()

    def add_column(self, table_name, column_name, column_type):
        """Adds a column to a table if it doesn't exist."""
        print(f"Adding column '{column_name}' to table '{table_name}'...")
        query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        try:
            self.execute_with_retry(query)
            self.conn.commit()
            print(f"Column '{column_name}' added successfully!")
        except sqlite3.OperationalError:
            print(
                f"Column '{column_name}' already exists in table '{table_name}'. Skipping.")

    def close_connection(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def check_result_exists(self, table_name, id_column, config_key):
        """Checks if a result file path exists for a given config ID."""
        query = f"""
            SELECT result_file_path
            FROM {table_name}
            WHERE {id_column} = ?
        """
        result = self.execute_with_retry(query, (config_key,))
        return result[0][0] is not None if result else False

    def get_config_ids_with_no_results(self, table_name, id_column, experience_id):
        """Retrieves config IDs from a table where result_file_path is NULL,
        grouped and sorted by algorithm (respecting priority), then numerically within each algorithm.
        """
        query = f"""
            SELECT {id_column}
            FROM {table_name}
            WHERE result_file_path IS NULL
            AND {id_column} IN (
                SELECT {id_column}
                FROM Experience{table_name}
                WHERE experience_id = ?
            )
        """
        result = self.execute_with_retry(query, (experience_id,))
        config_ids = [row[0] for row in result]

        # Group and sort config_ids by algorithm
        grouped_config_ids = {}
        if table_name == 'Assignments':
            algorithm_data = self.get_all_assignment_algorithms(config_ids)
            priority_list = self.assignment_algorithm_priority
        elif table_name == 'Schedulings':
            algorithm_data = self.get_all_scheduling_algorithms(config_ids)
            priority_list = self.scheduling_algorithm_priority
        else:  # Taskset
            algorithm_data = {config_id: 'taskset' for config_id in config_ids}
            priority_list = ["taskset"]  # Only one algorithm for taskset

        for config_id in config_ids:
            algorithm = algorithm_data.get(config_id)
            if algorithm not in grouped_config_ids:
                grouped_config_ids[algorithm] = []
            grouped_config_ids[algorithm].append(config_id)

        # Sort algorithms based on priority list
        sorted_algorithms = sorted(grouped_config_ids.keys(), key=lambda x: priority_list.index(
            x) if x in priority_list else len(priority_list))

        # Sort IDs numerically within each algorithm
        sorted_grouped_config_ids = {}
        for algorithm in sorted_algorithms:
            sorted_grouped_config_ids[algorithm] = sorted(
                grouped_config_ids[algorithm], key=lambda x: int(x.split('_')[1]))

        return sorted_grouped_config_ids

    def get_assignment_algorithm(self, assignment_id):
        """Retrieves the assignment_method for the given assignment_id."""
        query = """
            SELECT assignment_method
            FROM Assignments
            WHERE assignment_id = ?
        """
        result = self.execute_with_retry(query, (assignment_id,))
        return result[0][0] if result else None

    def get_scheduling_algorithm(self, scheduling_id):
        """Retrieves the scheduling_algorithm for the given scheduling_id."""
        query = """
            SELECT scheduling_algorithm
            FROM Schedulings
            WHERE scheduling_id = ?
        """
        result = self.execute_with_retry(query, (scheduling_id,))
        return result[0][0] if result else None

    def get_all_assignment_algorithms(self, assignment_ids):
        """Retrieves assignment_method for multiple assignment_ids in chunks."""
        chunk_size = 999  # SQLite often has a limit around 1000
        algorithm_data = {}
        for i in range(0, len(assignment_ids), chunk_size):
            chunk = assignment_ids[i:i + chunk_size]
            placeholders = ",".join("?" * len(chunk))
            query = f"""
                SELECT assignment_id, assignment_method
                FROM Assignments
                WHERE assignment_id IN ({placeholders})
            """
            result = self.execute_with_retry(query, chunk)
            algorithm_data.update(dict(result))
        return algorithm_data

    def get_all_scheduling_algorithms(self, scheduling_ids):
        """Retrieves scheduling_algorithm for multiple scheduling_ids in chunks."""
        chunk_size = 999  # SQLite often has a limit around 1000
        algorithm_data = {}
        for i in range(0, len(scheduling_ids), chunk_size):
            chunk = scheduling_ids[i:i + chunk_size]
            placeholders = ",".join("?" * len(chunk))
            query = f"""
                SELECT scheduling_id, scheduling_algorithm
                FROM Schedulings
                WHERE scheduling_id IN ({placeholders})
            """
            result = self.execute_with_retry(query, chunk)
            algorithm_data.update(dict(result))
        return algorithm_data
