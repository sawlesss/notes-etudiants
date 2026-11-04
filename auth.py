import json
import os
from flask import request

# Les jetons des utilisateurs sont conservés hors du code,
# dans un fichier qui n'est pas partagé sur GitHub
FICHIER_JETONS = os.environ.get("FICHIER_JETONS", "jetons.json")

# Retrouve l'utilisateur (nom, rôle, module) à partir du jeton
# présenté avec la demande ; personne si le jeton est absent ou inconnu
def utilisateur_connecte():
    entete = request.headers.get("Authorization", "")
    if not entete.startswith("Bearer "):
        return None
    try:
        with open(FICHIER_JETONS, encoding="utf-8") as fichier:
            jetons = json.load(fichier)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return jetons.get(entete.removeprefix("Bearer "))
