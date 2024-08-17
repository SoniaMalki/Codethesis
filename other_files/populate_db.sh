#!/bin/bash

# Lire toutes les clés dans experience.json en conservant l'ordre d'apparition
keys=$(jq -r 'to_entries|map(.key)|.[]' ../experience.json)

# Boucler sur chaque clé et exécuter la commande
for key in $keys
do
    echo "Lancement de la commande pour la clé: $key"
    python3 ../main.py generate_configs "$key"
done
