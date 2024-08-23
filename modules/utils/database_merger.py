import sqlite3
from pathlib import Path
import shutil
import time

from modules.utils.db_utils import DBUtils


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

        self.db_utils_v2 = DBUtils(self.db_path_v2)
        self.db_utils_merged = DBUtils(self.merged_db_path)
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

        self.db_utils_merged._commit_with_retry()
        print("All tables merged")

    def _merge_table(self, table_name):
        """Merges data from v2 into the merged database, prioritizing non-empty 'result_file_path' values."""

        # Get column names from the merged database
        self.db_utils_merged.cursor.execute(
            f"SELECT * FROM {table_name} LIMIT 1")
        columns = [description[0]
                   for description in self.db_utils_merged.cursor.description]

        print(f"Merging table {table_name} with columns: {columns}")

        # Process rows from v2
        for row in self.db_utils_v2._execute_with_retry(f"SELECT * FROM {table_name}"):
            primary_key_column = columns[0]
            primary_key_value = row[0]

            # Get the index of the 'result_file_path' in the v2 row
            result_file_path_index = columns.index('result_file_path')

            existing_row = self.db_utils_merged._execute_with_retry(
                f"SELECT * FROM {table_name} WHERE {primary_key_column} = ?",
                (primary_key_value,),
            )

            if existing_row:
                # Existing row in merged database
                existing_row = existing_row[0]
                existing_result_file_path = existing_row[result_file_path_index]

                # Check if the 'result_file_path' in v2 is non-empty
                if row[result_file_path_index]:
                    # 'result_file_path' in v2 is non-empty, replace the entire row in the merged database
                    update_query = (
                        f"UPDATE {table_name} SET "
                        + ", ".join([f"{col} = ?" for col in columns])
                        + f" WHERE {primary_key_column} = ?"
                    )
                    self.db_utils_merged._execute_with_retry(
                        update_query, (*row, primary_key_value))
                elif not existing_result_file_path:
                    # 'result_file_path' in v2 is empty, but only merge other columns if 'result_file_path' in merged DB is empty
                    for idx, column in enumerate(columns):
                        if idx != result_file_path_index and row[idx] is not None:
                            self.db_utils_merged._execute_with_retry(
                                f"UPDATE {table_name} SET {column} = ? WHERE {primary_key_column} = ?",
                                (row[idx], primary_key_value)
                            )
            else:
                # Row doesn't exist, insert the new row from v2
                insert_query = (
                    f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ("
                    + ", ".join(["?"] * len(row))
                    + ")"
                )
                self.db_utils_merged._execute_with_retry(insert_query, row)
