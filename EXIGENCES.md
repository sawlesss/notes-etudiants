# Exigences de sécurité de l'application des notes

| # | Exigence : « Le système doit… » | Vérification | Étape du SDLC | Test |
|---|---|---|---|---|
| 1 | Empêcher l'injection SQL dans la recherche par nom | Test automatique + Bandit | Développement | S1 |
| 2 | Identifier l'utilisateur (jeton) avant toute modification | Test automatique | Conception / Développement | S2 |
| 3 | Réserver la modification des notes aux enseignants | Test automatique | Conception / Développement | S3 |
| 4 | Limiter un enseignant aux notes de son propre module | Test automatique | Conception / Développement | S4 |
| 5 | Refuser toute note qui n'est pas un nombre entre 0 et 20 | Test automatique | Développement | S5 |
| 6 | Ne montrer aucun détail technique en cas d'erreur | Test automatique + revue de code | Développement / Revue | S7 |
| 7 | Permettre à l'enseignant du module de modifier la note de son étudiant | Test automatique | Test | S6 |