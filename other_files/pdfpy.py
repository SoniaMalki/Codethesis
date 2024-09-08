import subprocess
import os
from PyPDF2 import PdfMerger


def convert_to_pdf_with_paps(input_file, output_file):
    """
    Convertit un fichier texte (ex: Python) en PDF avec UTF-8 supporté à l'aide de paps.
    """
    try:
        # Commande paps pour convertir en PDF avec prise en charge de l'UTF-8
        command = f"paps --font='Courier 10' {input_file} | ps2pdf - {output_file}"

        # Exécution de la commande
        subprocess.run(command, shell=True, check=True)
        print(
            f"Le fichier {input_file} a été converti en {output_file} avec paps (UTF-8).")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la conversion de {input_file}: {e}")


def convert_all_py_files_in_directory(input_dir, output_dir):
    """
    Convertit tous les fichiers Python (.py) dans un dossier en PDF et les enregistre dans un dossier de sortie.
    """
    # Créer le dossier de sortie s'il n'existe pas
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Parcourir tous les fichiers du dossier d'entrée
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".py"):
            input_file = os.path.join(input_dir, file_name)
            output_file = os.path.join(
                output_dir, f"{os.path.splitext(file_name)[0]}.pdf")

            # Appel de la fonction pour convertir en PDF
            convert_to_pdf_with_paps(input_file, output_file)

    print(
        f"Toutes les conversions en PDF sont terminées. Les fichiers sont dans le dossier {output_dir}.")


def merge_pdfs_in_directory(output_dir, combined_pdf):
    """
    Fusionne tous les fichiers PDF dans le dossier output_dir en un seul fichier PDF nommé combined_pdf.
    """
    pdf_merger = PdfMerger()
    pdf_files = [os.path.join(output_dir, f)
                 for f in os.listdir(output_dir) if f.endswith(".pdf")]

    if not pdf_files:
        print("Aucun fichier PDF trouvé pour fusionner.")
        return

    pdf_files.sort()

    for pdf in pdf_files:
        pdf_merger.append(pdf)

    pdf_merger.write(combined_pdf)
    pdf_merger.close()
    print(f"Tous les fichiers PDF ont été fusionnés dans {combined_pdf}.")


# Dossier contenant les fichiers Python
input_dir = "Code"

# Dossier de sortie pour les PDF générés
output_dir = "pdf_files"

# Nom du fichier PDF combiné
combined_pdf = "combined_output.pdf"

# Étape 1: Convertir tous les fichiers Python en PDF
convert_all_py_files_in_directory(input_dir, output_dir)

# Étape 2: Fusionner tous les fichiers PDF en un seul fichier
merge_pdfs_in_directory(output_dir, combined_pdf)
