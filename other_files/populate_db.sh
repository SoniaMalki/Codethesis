#!/bin/bash

# Définir le chemin de base pour les scripts et les données
base_dir="$CODETHESIS"

# Vérifier que l'argument index est fourni et qu'il s'agit d'un chiffre
if [ -z "$1" ] || ! [[ "$1" =~ ^[0-9]+$ ]]; then
    echo "Erreur: L'argument 'index' est obligatoire et doit être un chiffre."
    echo "Utilisation: $0 <index>"
    exit 1
fi

# Affecter l'argument à la variable index
index="$1"

# Lire toutes les clés dans le fichier experience_${index}.json en conservant l'ordre d'apparition
keys=$(jq -r 'to_entries|map(.key)|.[]' "$base_dir/experience_${index}.json")

# Boucler sur chaque clé et exécuter la commande
for key in $keys
do
    python3 "$base_dir/main.py" generate_configs "$index" "$key"
done
