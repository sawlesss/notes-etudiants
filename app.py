import logging
from flask import jsonify
from auth import utilisateur_connecte
import os
import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)

# Fichier où sont conservées les notes de l'école
DB = "notes.db"


# Prépare le registre des notes au démarrage de l'application
def init_db():
    with sqlite3.connect(DB) as con:
        # Chaque note concerne un étudiant, dans un module
        con.execute(
            "CREATE TABLE IF NOT EXISTS notes "
            "(id INTEGER PRIMARY KEY, etudiant TEXT, module TEXT, note REAL)"
        )

        # Si le registre est vide, on y inscrit deux notes d'exemple
        if con.execute("SELECT COUNT(*) FROM notes").fetchone()[0] == 0:
            con.executemany(
                "INSERT INTO notes (etudiant, module, note) VALUES (?, ?, ?)",
                [
                    ("Amina", "DevSecOps", 15.5),
                    ("Youssef", "DevSecOps", 12.0),
                ],
            )


init_db()


# Page d'accueil : l'étudiant y trouve le lien vers les notes
@app.route("/")
def accueil():
    return (
        "<!DOCTYPE html><html lang='fr'><head><meta charset='utf-8'>"
        "<title>Notes des etudiants</title></head><body>"
        "<h1>Consultation des notes</h1>"
        "<p><a href='/notes'>Voir les notes</a></p></body></html>"
    )


# Indique que le service des notes est disponible
@app.route("/health")
def health():
    return jsonify(status="ok", version = 1.0)

@app.route("/version")
def test_version():
    return jsonify(version = 1.0)


# Consultation des notes : toutes les notes,
# ou seulement celles d'un étudiant si on donne son nom
# Exemple : /notes?etudiant=Amina
@app.route("/notes")
def lister_notes():
    # Nom de l'étudiant recherché (facultatif)
    etudiant = request.args.get("etudiant", "")

    with sqlite3.connect(DB) as con:
        rows = con.execute(
            "SELECT id, etudiant, module, note FROM notes WHERE etudiant LIKE ?",
            (f"%{etudiant}%",),
        ).fetchall()

    # Pour chaque note : l'étudiant, le module et la note obtenue
    return jsonify(
        [
            {
                "id": r[0],
                "etudiant": r[1],
                "module": r[2],
                "note": r[3],
            }
            for r in rows
        ]
    )

@app.route("/notes/<int:note_id>", methods=["PUT"])
def modifier_note(note_id):
    user = utilisateur_connecte()
    if user is None:
        return jsonify(erreur="Authentification requise"), 401
    if user["role"] != "enseignant":
        return jsonify(erreur="Accès refusé"), 403

    note = (request.get_json(silent=True) or {}).get("note")
    if isinstance(note, bool) or not isinstance(note, (int, float)) \
            or not 0 <= note <= 20:
        return jsonify(erreur="Note invalide (0 à 20)"), 400

    try:
        con = sqlite3.connect(DB)
        try:
            row = con.execute("SELECT module FROM notes WHERE id = ?",
                              (note_id,)).fetchone()
            if row is None:
                return jsonify(erreur="Note introuvable"), 404
            if row[0] != user["module"]:
                return jsonify(erreur="Accès refusé"), 403
            con.execute("UPDATE notes SET note = ? WHERE id = ?",
                        (note, note_id))
            con.commit()
        finally:
            con.close()
        logging.info("Note %s -> %s par %s", note_id, note, user["nom"])
        return jsonify(statut="OK")
    except sqlite3.Error:
        logging.exception("Erreur lors de la modification")
        return jsonify(erreur="Erreur interne"), 500

# Démarrage du service des notes, sur ce poste uniquement
if __name__ == "__main__":
    app.run(host=os.environ.get("APP_HOST", "127.0.0.1"), port=5000)
