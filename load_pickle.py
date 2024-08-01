import pickle

def load_pickle_file(filename):
    """Charge et affiche le contenu d'un fichier pickle."""
    try:
        with open(filename, 'rb') as file:
            data = pickle.load(file)
            print("Contenu du fichier pickle :")
            print(data)
    except FileNotFoundError:
        print(f"Erreur : Le fichier {filename} n'a pas été trouvé.")
    except EOFError:
        print("Erreur : Le fichier est corrompu ou vide.")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")

if __name__ == "__main__":
    # Nom du fichier pickle à charger
    filename = "prime_matrix_10000_23_10000000000000000000000000000.pkl"
    load_pickle_file(filename)
