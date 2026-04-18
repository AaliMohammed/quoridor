# Quoridor IA — Projet Intelligence Artificielle

Implémentation du jeu **Quoridor** en Python avec une IA basée sur l'algorithme **Minimax avec élagage Alpha-Bêta** et trois niveaux de difficulté.

---

## Prérequis

- Python 3.8 ou supérieur
- Aucune dépendance externe requise (bibliothèque standard uniquement)

Pour les tests unitaires :
```bash
pip install pytest
```

---

## Lancer le jeu

Depuis le répertoire `quoridor/` :

```bash
python main.py
```

Le programme vous demandera :
1. **Mode** : Humain vs Humain (`H`) ou Humain vs IA (`I`)
2. **Difficulté** (si mode IA) :
   - `1` — Facile (H1 : heuristique linéaire, profondeur 2)
   - `2` — Moyen (H2 : BFS chemin court, profondeur 2)
   - `3` — Expert (H3 : BFS + urgence + bonus murs, profondeur 2)

### Commandes en jeu

| Action | Saisie |
|--------|--------|
| Déplacer le pion | `M` puis `ligne colonne` (ex: `3 4`) |
| Poser un mur | `W` puis ligne (0-7), colonne (0-7), orientation (`H` ou `V`) |
| Quitter | `Q` |

Les coordonnées affichées vont de 0 à 8. Un mur horizontal `H` en `(r, c)` bloque le passage entre les lignes `r` et `r+1` au niveau des colonnes `c` et `c+1`.

---

## Lancer le benchmark (analyse expérimentale)

```bash
python -m evaluation.benchmark
```

Teste les 3 heuristiques aux profondeurs 1, 2 et 3. Génère `evaluation/analyse_ia.csv`.

---

## Lancer le tournoi entre IAs

```bash
python -m evaluation.tournament
```

Organise 50 parties pour chaque paire d'IA (H1 vs H2, H1 vs H3, H2 vs H3). Génère `evaluation/tournament_results.csv`.

> **Note :** le tournoi peut prendre plusieurs minutes selon la machine. La progression est affichée en temps réel.

---

## Lancer les tests unitaires

```bash
python -m pytest tests/ -v
```

---

## Structure du projet

```
quoridor/
├── engine/
│   ├── board.py        # Plateau 17×17, règles, BFS, placement de murs
│   └── validator.py
├── ia/
│   ├── minimax.py      # Algorithme Minimax + élagage Alpha-Bêta
│   └── heuristics.py   # H1 (linéaire), H2 (BFS), H3 (BFS + murs)
├── evaluation/
│   ├── benchmark.py    # Mesure nœuds et temps par heuristique/profondeur
│   └── tournament.py   # Tournoi round-robin 50 parties/paire
├── tests/
│   └── test_board.py   # Tests unitaires du moteur de jeu
├── main.py             # Point d'entrée — interface terminal
└── README.md
```

---

## Règles du jeu Quoridor (rappel)

- Plateau 9×9, 2 joueurs, 10 murs chacun.
- **P1** part du milieu de la ligne 0 et doit atteindre la ligne 8 (affiché comme ligne 8 à l'écran).
- **P2** part du milieu de la ligne 8 et doit atteindre la ligne 0.
- À chaque tour : **déplacer son pion** ou **poser un mur** (2 cases de long).
- Un mur ne peut pas isoler complètement un joueur (vérification par BFS).
- Si deux pions sont adjacents, on peut **sauter par-dessus** l'adversaire.
  Si le saut droit est bloqué (mur ou bord), un **saut diagonal** est possible.
