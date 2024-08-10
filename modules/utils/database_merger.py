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

            # Get the indices of the relevant columns in the v2 row
            result_file_path_index = columns.index('result_file_path')
            cluster_index = columns.index('cluster')
            threads_index = columns.index('threads')
            slurm_time_index = columns.index('slurm_time')
            slurm_memory_index = columns.index('slurm_memory')

            self.cursor_merged.execute(
                f"SELECT result_file_path, cluster, threads, slurm_time, slurm_memory FROM {table_name} WHERE {primary_key_column} = ?",
                (primary_key_value,),
            )
            existing_row = self.cursor_merged.fetchone()

            if existing_row:
                # Row exists, update columns with non-empty values from v2
                merged_result_file_path, merged_cluster, merged_threads, merged_slurm_time, merged_slurm_memory = existing_row

                # Choose the non-empty 'result_file_path', prioritizing v2 if both are non-empty
                if row[result_file_path_index] and not merged_result_file_path:
                    self.cursor_merged.execute(
                        f"UPDATE {table_name} SET result_file_path = ? WHERE {primary_key_column} = ?",
                        (row[result_file_path_index], primary_key_value),
                    )

                # Update cluster if v2 value is not empty
                if row[cluster_index]:
                    self.cursor_merged.execute(
                        f"UPDATE {table_name} SET cluster = ? WHERE {primary_key_column} = ?",
                        (row[cluster_index], primary_key_value),
                    )

                # Update threads if v2 value is not empty
                if row[threads_index] is not None:  # Use 'is not None' for threads as it can be 0
                    self.cursor_merged.execute(
                        f"UPDATE {table_name} SET threads = ? WHERE {primary_key_column} = ?",
                        (row[threads_index], primary_key_value),
                    )

                # Update slurm_time if v2 value is not empty
                if row[slurm_time_index]:
                    self.cursor_merged.execute(
                        f"UPDATE {table_name} SET slurm_time = ? WHERE {primary_key_column} = ?",
                        (row[slurm_time_index], primary_key_value),
                    )

                # Update slurm_memory if v2 value is not empty
                if row[slurm_memory_index]:
                    self.cursor_merged.execute(
                        f"UPDATE {table_name} SET slurm_memory = ? WHERE {primary_key_column} = ?",
                        (row[slurm_memory_index], primary_key_value),
                    )

            else:
                # Row doesn't exist, insert the new row from v2
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
        self.conn_merged.close()
        print("Database connections closed")
