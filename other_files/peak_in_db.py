import sqlite3
from pathlib import Path


def get_table_info(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Obtenir la liste de toutes les tables dans la base de données
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        print(f"Table: {table_name}")

        # Obtenir le nombre de lignes dans la table
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        row_count = cursor.fetchone()[0]
        print(f"Nombre de lignes: {row_count}")

        # Obtenir la première ligne de la table
        cursor.execute(
            f"SELECT * FROM {table_name} ORDER BY ROWID ASC LIMIT 1;")
        first_row = cursor.fetchone()
        print(f"Première ligne: {first_row}")

        # Obtenir la dernière ligne de la table
        cursor.execute(
            f"SELECT * FROM {table_name} ORDER BY ROWID DESC LIMIT 1;")
        last_row = cursor.fetchone()
        print(f"Dernière ligne: {last_row}")

        print("-" * 50)

    conn.close()


if __name__ == "__main__":
    script_path = Path(__file__).parent
    db_path = script_path / "../generation/experience.db"
    print(db_path)
    get_table_info(db_path)
