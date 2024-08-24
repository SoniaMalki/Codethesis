import sqlite3
import os
import shutil


class DatabaseConcatenator:
    def __init__(self, db_paths, structure_db_path, result_folder):
        self.db_paths = db_paths
        self.structure_db_path = structure_db_path
        self.result_folder = result_folder

        self.result_columns = {'result_file_path',
                               'cluster', 'threads', 'slurm_time', 'slurm_memory'}

        self.conn_structure = sqlite3.connect(self.structure_db_path)
        self.conn_structure.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn_structure.cursor()

    def load_data(self, conn):
        print("Loading data from database...")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Tasksets")
        tasksets = cursor.fetchall()
        print(f"Loaded {len(tasksets)} tasksets.")
        return tasksets

    def find_matching_taskset_id(self, taskset):
        """Recherche un taskset correspondant dans big.db."""
        print(
            f"Searching for matching Taskset: {taskset[2:]}")
        self.cursor.execute("""
            SELECT taskset_id FROM Tasksets WHERE
                taskset_repetition = ? AND
                tasks_per_taskset = ? AND
                interference_factor = ? AND
                probability_factor = ? AND
                max_utilization = ? AND
                deadline_option = ? AND
                max_hyperperiod = ? AND
                max_prime = ? AND
                gen_limit_exponent = ? AND
                number_of_cores = ?
            """, taskset[2:12])
        result = self.cursor.fetchone()
        if result:
            print(f"Found matching Taskset ID in big.db: {result[0]}")
            return result[0]
        else:
            print("Error: No matching Taskset found. This should not happen!")
            return None

    def process_database(self, db_index, db_path):
        print(f"Processing database: {db_path} (index: {db_index})")
        with sqlite3.connect(db_path) as conn:
            tasksets = self.load_data(conn)

        taskset_map = {}

        for taskset in tasksets:
            new_taskset_id = self.find_matching_taskset_id(taskset)
            if new_taskset_id is not None:
                taskset_map[taskset[0]] = new_taskset_id

                self.cursor.execute(
                    "UPDATE Tasksets SET result_file_path = ? WHERE taskset_id = ?",
                    (f"{new_taskset_id}.pkl", new_taskset_id)
                )
                self.conn_structure.commit()

        return taskset_map, {}, {}

    def move_and_rename_files(self, table_name, id_map):
        """Copie et renomme les fichiers de résultats pour la table donnée."""
        print(f"Moving and renaming result files for {table_name}...")
        os.makedirs(os.path.join(self.result_folder,
                    table_name.lower()), exist_ok=True)

        for db_index in self.db_paths:
            source_folder = os.path.join(
                self.result_folder.parent, f"results_{db_index}", table_name.lower())
            if os.path.exists(source_folder):
                for filename in os.listdir(source_folder):
                    if filename.endswith(".pkl"):
                        file_id = filename.split('_')[1].split('.')[0]
                        new_file_id = id_map.get(
                            f"{table_name.lower()[:-1]}_{file_id}")
                        if new_file_id:
                            old_path = os.path.join(source_folder, filename)
                            new_filename = f"{new_file_id}.pkl"
                            new_path = os.path.join(
                                self.result_folder, table_name.lower(), new_filename)
                            shutil.copy2(old_path, new_path)
                            print(f"Copied: {old_path} -> {new_path}")
            else:
                print(f"Directory not found: {source_folder}")
        print(
            f"Result files copied and renamed successfully for {table_name}.")

    def integrate_databases(self):
        print("Integrating databases...")
        taskset_map, _, _ = {}, {}, {}
        for db_index, db_path in self.db_paths.items():
            tm, _, _ = self.process_database(db_index, db_path)
            taskset_map.update(tm)

        self.move_and_rename_files("Tasksets", taskset_map)
        print("Database integration completed.")
        self.conn_structure.close()
