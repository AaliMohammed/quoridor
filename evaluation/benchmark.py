import time
import csv
from engine.board import QuoridorBoard
from minimax import QuoridorAI

def run_experiment(depth, h_type):
    board = QuoridorBoard()
    ai = QuoridorAI(board, player_id=2, depth=depth, heuristic_type=h_type)
    
    start_time = time.time()
    # On simule un coup au milieu du jeu pour tester la performance
    ai.get_best_move() 
    end_time = time.time()
    
    return {
        "depth": depth,
        "heuristic": h_type,
        "nodes": ai.nodes_explored,
        "time": end_time - start_time
    }

# Génération des données pour le tableau
results = []
for d in [1, 2, 3]: # Test de différentes profondeurs
    for h in ['H1', 'H2', 'H3']: # Test des 3 heuristiques
        print(f"Test en cours : Profondeur {d}, Heuristique {h}...")
        res = run_experiment(d, h)
        results.append(res)

# Sauvegarde en CSV pour le rapport
keys = results[0].keys()
with open('analyse_ia.csv', 'w', newline='') as f:
    dict_writer = csv.DictWriter(f, keys)
    dict_writer.writeheader()
    dict_writer.writerows(results)