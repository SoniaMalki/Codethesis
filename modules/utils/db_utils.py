import sqlite3
from pathlib import Path


class DBUtils:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

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
        """Enter the runtime context related to this object."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context related to this object."""
        # Close the database connection
        self.conn.close()

    def get_config_ids_with_no_results(self, table_name, id_column, experience_id):
        """Retrieves config IDs from a table where result_file_path is NULL."""
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
            return [row[0] for row in results]
        except Exception as e:
            print(f"Error retrieving config IDs from {table_name}: {e}")
            return []

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
