import sqlite3
from pathlib import Path
import shutil 


class DatabaseMerger:
    def __init__(self, db_path_v1, db_path_v2, merged_db_path):
        print("------------------------------")
        print("Initializing DatabaseMerger")
        self.db_path_v1 = Path(db_path_v1)
        self.db_path_v2 = Path(db_path_v2)
        self.merged_db_path = Path(merged_db_path)

        # Debugging: Print database paths
        print(f"Database v1 path: {self.db_path_v1}")
        print(f"Database v2 path: {self.db_path_v2}")
        print(f"Merged database path: {self.merged_db_path}")

        # Copy v1 to merged.db
        shutil.copy(self.db_path_v1, self.merged_db_path)

        self.conn_v2 = sqlite3.connect(self.db_path_v2)
        self.conn_merged = sqlite3.connect(self.merged_db_path)
        self.cursor_merged = self.conn_merged.cursor()
        print("DatabaseMerger initialized successfully")

    def merge_tables(self):
        """Merges data from v2 database into the merged database (originally copied from v1)."""
        print("------------------------------")
        print("Merging tables")

        tables_to_merge = [
            "Tasksets",
            "Assignments",
            "Schedulings",
        ]  # Only tables with potential 'result_file_path' conflicts

        for table in tables_to_merge:
            print(f"Merging table: {table}")
            self._merge_table(table)
            print(f"Table {table} merged")

        self.conn_merged.commit()
        print("All tables merged")

    def _merge_table(self, table_name):
        """Merges data from v2 into the merged database, prioritizing non-empty 'result_file_path' values."""

        # Get column names from the merged database
        self.cursor_merged.execute(f"SELECT * FROM {table_name} LIMIT 1")
        columns = [description[0]
                   for description in self.cursor_merged.description]

        print(f"Merging table {table_name} with columns: {columns}")

        # Process rows from v2
        for row in self.conn_v2.cursor().execute(f"SELECT * FROM {table_name}"):
            primary_key_column = columns[0]
            primary_key_value = row[0]

            self.cursor_merged.execute(
                f"SELECT result_file_path FROM {table_name} WHERE {primary_key_column} = ?",
                (primary_key_value,),
            )
            existing_result_file_path = self.cursor_merged.fetchone()

            if existing_result_file_path:
                # Update only if v2 has a non-empty result_file_path and v1 (merged) is empty
                if row[-1] and not existing_result_file_path[0]:
                    self.cursor_merged.execute(
                        f"UPDATE {table_name} SET result_file_path = ? WHERE {primary_key_column} = ?",
                        (row[-1], primary_key_value),
                    )
            else:
                # Insert the new row from v2 if it doesn't exist in the merged database
                insert_query = (
                    f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ("
                    + ", ".join(["?"] * len(row))
                    + ")"
                )
                self.cursor_merged.execute(insert_query, row)

    def close_connections(self):
        """Closes all database connections."""
        print("------------------------------")
        print("Closing database connections")
        self.conn_v2.close()
        self.conn_merged.close()ddd 
        print("Database connections closed")
