import sqlite3
import os
import shutil


class DatabaseConcatenator:
    def __init__(self, db_paths, structure_db_path, result_folder):
        self.db_paths = db_paths
        self.structure_db_path = structure_db_path
        self.result_folder = result_folder

        self.result_columns = {
            'result_file_path', 'cluster', 'threads', 'slurm_time', 'slurm_memory'}

        self.conn_structure = sqlite3.connect(self.structure_db_path)
        self.conn_structure.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn_structure.cursor()

    def load_data(self, conn):
        print("Loading data from database...")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Tasksets")
        tasksets = cursor.fetchall()
        print(f"Loaded {len(tasksets)} tasksets.")
        cursor.execute("SELECT * FROM Assignments")
        assignments = cursor.fetchall()
        print(f"Loaded {len(assignments)} assignments.")
        cursor.execute("SELECT * FROM Schedulings")
        schedulings = cursor.fetchall()
        print(f"Loaded {len(schedulings)} schedulings.")
        return tasksets, assignments, schedulings

    def find_matching_taskset_id(self, taskset):
        """Recherche un taskset correspondant dans big.db."""
        print(f"Searching for matching Taskset: {taskset[2:]}")
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

    def find_matching_assignment_id(self, assignment, taskset_map):
        """Recherche un assignment correspondant dans big.db en utilisant le nouveau taskset_id."""

        # Traduire l'ancien taskset_id en nouveau taskset_id
        old_taskset_id = assignment[1]
        new_taskset_id = taskset_map.get(old_taskset_id)

        if new_taskset_id is None:
            print(
                f"Error: No matching taskset found for assignment {assignment[0]}. This should not happen!")
            return None

        print(
            f"Searching for matching Assignment: {(new_taskset_id,) + assignment[2:7]}")
        self.cursor.execute("""
            SELECT assignment_id FROM Assignments WHERE
                taskset_id = ? AND
                action = ? AND
                sorting_criterion = ? AND
                assignment_method = ? AND
                number_of_cores = ? AND
                solving_time_limit_MILP = ? 
            """, (new_taskset_id,) + assignment[2:7])  # Utiliser le nouveau taskset_id
        result = self.cursor.fetchone()
        if result:
            print(f"Found matching Assignment ID in big.db: {result[0]}")
            return result[0]
        else:
            print(
                "Error: No matching Assignment found. This should not happen!")
            return None

    def find_matching_scheduling_id(self, scheduling, taskset_map, assignment_map):
        """Recherche un scheduling correspondant dans big.db en utilisant les nouveaux IDs."""

        # Traduire les anciens IDs en nouveaux IDs
        old_assignment_id = scheduling[1]
        old_taskset_id = scheduling[2]
        new_assignment_id = assignment_map.get(old_assignment_id)
        new_taskset_id = taskset_map.get(old_taskset_id)

        if new_assignment_id is None or new_taskset_id is None:
            print(
                f"Error: No matching assignment or taskset found for scheduling {scheduling[0]}. This should not happen!")
            return None

        print(
            f"Searching for matching Scheduling: {(new_assignment_id, new_taskset_id) + scheduling[3:7]}")

        self.cursor.execute("""
            SELECT scheduling_id FROM Schedulings WHERE
                assignment_id = ? AND
                taskset_id = ? AND
                action = ? AND
                scheduling_algorithm = ? AND
                non_preemption_time_variant2 = ? AND
                solving_time_limit_MILP = ? 
            """, (new_assignment_id, new_taskset_id) + scheduling[3:7])  # Utiliser les nouveaux IDs
        result = self.cursor.fetchone()
        if result:
            print(f"Found matching Scheduling ID in big.db: {result[0]}")
            return result[0]
        else:
            print(
                "Error: No matching Scheduling found. This should not happen!")
            return None

    def update_result_columns(self, table_name, record, new_id):
        """Met à jour les colonnes de résultats pour l'enregistrement donné."""
        print(f"Updating result columns for {table_name[:-1]} {new_id}...")
        self.cursor.execute(f"SELECT * FROM {table_name} LIMIT 0")
        columns = [description[0]
                   for description in self.cursor.description]
        record = dict(zip(columns, record))

        update_values = []
        set_clause = []
        for col in self.result_columns:
            if col in record:
                set_clause.append(f"{col} = ?")
                update_values.append(record[col])

        set_clause.append(f"result_file_path = ?")
        update_values.append(f"{new_id}.pkl")

        if set_clause:
            query = f"UPDATE {table_name} SET {', '.join(set_clause)} WHERE {table_name[:-1]}_id = ?"
            update_values.append(new_id)

            self.cursor.execute(query, tuple(update_values))
            self.conn_structure.commit()
            print(f"Result columns updated successfully.")

    def process_database(self, db_index, db_path):
        print(f"Processing database: {db_path} (index: {db_index})")
        with sqlite3.connect(db_path) as conn:
            tasksets, assignments, schedulings = self.load_data(conn)

        taskset_map = {}
        for taskset in tasksets:
            new_taskset_id = self.find_matching_taskset_id(taskset)
            if new_taskset_id is not None:
                taskset_map[taskset[0]] = new_taskset_id
                self.update_result_columns(
                    "Tasksets", taskset, new_taskset_id)

        assignment_map = {}
        for assignment in assignments:
            new_assignment_id = self.find_matching_assignment_id(
                assignment, taskset_map)
            if new_assignment_id is not None:
                assignment_map[assignment[0]] = new_assignment_id
                self.update_result_columns(
                    "Assignments", assignment, new_assignment_id)

        scheduling_map = {}
        for scheduling in schedulings:
            new_scheduling_id = self.find_matching_scheduling_id(
                scheduling, taskset_map, assignment_map)
            if new_scheduling_id is not None:
                scheduling_map[scheduling[0]] = new_scheduling_id
                self.update_result_columns(
                    "Schedulings", scheduling, new_scheduling_id)

        return taskset_map, assignment_map, scheduling_map

    def move_and_rename_files(self, table_name, id_map, db_index):
        """Copie et renomme les fichiers de résultats pour la table donnée."""
        print(f"Moving and renaming result files for {table_name}...")
        os.makedirs(os.path.join(self.result_folder,
                    table_name.lower()), exist_ok=True)

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
        for db_index, db_path in self.db_paths.items():
            taskset_map, assignment_map, scheduling_map = {}, {}, {}
            tm, am, sm = self.process_database(db_index, db_path)
            taskset_map.update(tm)
            assignment_map.update(am)
            scheduling_map.update(sm)
            self.move_and_rename_files("Tasksets", taskset_map, db_index)
            self.move_and_rename_files("Assignments", assignment_map, db_index)
            self.move_and_rename_files(
                "Schedulings", scheduling_map, db_index)
            print("Database integration completed.")
        self.conn_structure.close()
