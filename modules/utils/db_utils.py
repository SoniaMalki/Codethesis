import json
import sqlite3
from pathlib import Path


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

    def get_result_file_path(self, config_id, config_type):
        """Récupère le chemin du fichier de résultat pour une configuration donnée dans la base de données."""
        self.cursor.execute(
            f"""
            SELECT result_file_path
            FROM {config_type.capitalize()}s
            WHERE {config_type}_id = ?
            """,
            (config_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def update_result_file_path(self, config_id, config_type, file_path):
        """Met à jour le chemin du fichier de résultat pour une configuration donnée."""
        self.cursor.execute(f"""
            UPDATE {config_type.capitalize()}s
            SET result_file_path = ?
            WHERE {config_type}_id = ?
        """, (file_path, config_id))
        self.conn.commit()

    def add_column(self, table_name, column_name, column_type):
        """Adds a column to a table if it doesn't exist."""
        print(f"Adding column '{column_name}' to table '{table_name}'...")
        try:
            self.cursor.execute(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            )
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
        try:
            self.cursor.execute(f"""
                SELECT result_file_path
                FROM {table_name}
                WHERE {id_column} = ?
            """, (config_key,))
            result = self.cursor.fetchone()
            return result[0] is not None if result else False
        except Exception as e:
            print(f"Error checking result existence in {table_name}: {e}")
            return False

    def get_config_ids_with_no_results(self, table_name, id_column, experience_id):
        """Retrieves config IDs from a table where result_file_path is NULL,
        grouped and sorted by algorithm (respecting priority), then numerically within each algorithm.
        """
        try:
            self.cursor.execute(f"""
                SELECT {id_column}
                FROM {table_name}
                WHERE result_file_path IS NULL
                AND {id_column} IN (
                    SELECT {id_column}
                    FROM Experience{table_name}
                    WHERE experience_id = ?
                )
            """, (experience_id,))
            results = self.cursor.fetchall()
            config_ids = [row[0] for row in results]

            # Group and sort config_ids by algorithm
            grouped_config_ids = {}
            if table_name == 'Assignments':
                algorithm_data = self.get_all_assignment_algorithms(config_ids)
                priority_list = self.assignment_algorithm_priority
            elif table_name == 'Schedulings':
                algorithm_data = self.get_all_scheduling_algorithms(config_ids)
                priority_list = self.scheduling_algorithm_priority
            else:  # Taskset
                algorithm_data = {
                    config_id: 'taskset' for config_id in config_ids}
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

        except Exception as e:
            print(f"Error retrieving config IDs from {table_name}: {e}")
            return {}

    def get_assignment_algorithm(self, assignment_id):
        """Retrieves the assignment_method for the given assignment_id."""
        try:
            self.cursor.execute("""
                SELECT assignment_method
                FROM Assignments
                WHERE assignment_id = ?
            """, (assignment_id,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error retrieving assignment algorithm: {e}")
            return None

    def get_scheduling_algorithm(self, scheduling_id):
        """Retrieves the scheduling_algorithm for the given scheduling_id."""
        try:
            self.cursor.execute("""
                SELECT scheduling_algorithm
                FROM Schedulings
                WHERE scheduling_id = ?
            """, (scheduling_id,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error retrieving scheduling algorithm: {e}")
            return None

    def get_all_assignment_algorithms(self, assignment_ids):
        """Retrieves assignment_method for multiple assignment_ids in chunks."""
        try:
            chunk_size = 999  # SQLite often has a limit around 1000
            algorithm_data = {}
            for i in range(0, len(assignment_ids), chunk_size):
                chunk = assignment_ids[i:i + chunk_size]
                placeholders = ",".join("?" * len(chunk))
                self.cursor.execute(f"""
                    SELECT assignment_id, assignment_method
                    FROM Assignments
                    WHERE assignment_id IN ({placeholders})
                """, chunk)
                algorithm_data.update(dict(self.cursor.fetchall()))
            return algorithm_data
        except Exception as e:
            print(f"Error retrieving assignment algorithms: {e}")
            return {}

    def get_all_scheduling_algorithms(self, scheduling_ids):
        """Retrieves scheduling_algorithm for multiple scheduling_ids in chunks."""
        try:
            chunk_size = 999  # SQLite often has a limit around 1000
            algorithm_data = {}
            for i in range(0, len(scheduling_ids), chunk_size):
                chunk = scheduling_ids[i:i + chunk_size]
                placeholders = ",".join("?" * len(chunk))
                self.cursor.execute(f"""
                    SELECT scheduling_id, scheduling_algorithm
                    FROM Schedulings
                    WHERE scheduling_id IN ({placeholders})
                """, chunk)
                algorithm_data.update(dict(self.cursor.fetchall()))
            return algorithm_data
        except Exception as e:
            print(f"Error retrieving scheduling algorithms: {e}")
            return {}
