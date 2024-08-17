#!/bin/bash

# Définir le chemin de base pour les scripts et les données
base_dir="$CODETHESIS"

# Lire toutes les clés dans experience.json en conservant l'ordre d'apparition
keys=$(jq -r 'to_entries|map(.key)|.[]' "$base_dir/experience.json")

# Boucler sur chaque clé et exécuter la commande
for key in $keys
do
    echo "Lancement de la commande pour la clé: $key"
    python3 "$base_dir/main.py" generate_configs "$key"
done
