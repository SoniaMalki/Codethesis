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
            print(f"Column '{column_name}' already exists in table '{table_name}'. Skipping.")

    def close_connection(self):
        self.conn.close()
