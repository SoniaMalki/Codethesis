#!/bin/bash

# Vérifier que l'argument index est fourni et qu'il s'agit d'un chiffre
if [ -z "$1" ] || ! [[ "$1" =~ ^[0-9]+$ ]]; then
    echo "Erreur: L'argument 'index' est obligatoire et doit être un chiffre."
    echo "Utilisation: $0 <index>"
    exit 1
fi

# Affecter l'argument à la variable index
index="$1"

# Définir le chemin de base pour les scripts et les données
dir="$GLOBALSCRATCH/generation"

# Utiliser l'index pour définir les fichiers de base de données
db_file="$dir/experience_${index}.db"
db_save="$dir/experience_old_${index}.db"

# Renommer l'ancien fichier de base de données
mv "$db_file" "$db_save"

# Créer un nouveau fichier de base de données à partir de l'ancien
cat <( sqlite3 "$db_save" .dump | grep "^ROLLBACK" -v ) <( echo "COMMIT;" ) | sqlite3 "$db_file"
