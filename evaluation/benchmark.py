import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import csv
from engine.board import QuoridorBoard
from ia.minimax import QuoridorAI


def run_experiment(depth, h_type, n_runs=3):
    """
    Mesure les performances d'une IA a une profondeur et heuristique donnees.
    Effectue n_runs mesures et retourne la moyenne pour plus de fiabilite.
    """
    times = []
    nodes_list = []

    scores = []

    for _ in range(n_runs):
        board = QuoridorBoard(verbose=False)
        ai = QuoridorAI(board, player_id=2, depth=depth,
                        heuristic_type=h_type, verbose=False)

        start_time = time.time()
        ai.get_best_move()
        end_time = time.time()

        times.append(end_time - start_time)
        nodes_list.append(ai.nodes_explored)
        scores.append(ai.best_score)

    return {
        "depth": depth,
        "heuristic": h_type,
        "nodes_mean": round(sum(nodes_list) / n_runs),
        "nodes_min": min(nodes_list),
        "nodes_max": max(nodes_list),
        "time_mean": round(sum(times) / n_runs, 4),
        "time_min": round(min(times), 4),
        "time_max": round(max(times), 4),
        "score_mean": round(sum(scores) / n_runs, 3),
        "score_min": round(min(scores), 3),
        "score_max": round(max(scores), 3),
    }


if __name__ == '__main__':
    results = []

    print("=== ANALYSE EXPERIMENTALE DES HEURISTIQUES ===\n")
    print(f"{'Profondeur':<12} {'Heuristique':<14} {'Noeuds (moy)':<14} {'Temps moy (s)':<16} {'Score moy'}")
    print("-" * 75)

    for d in [1, 2, 3]:
        for h in ['H1', 'H2', 'H3']:
            print(f"  Test en cours : Profondeur {d}, Heuristique {h}...", end=" ", flush=True)
            res = run_experiment(d, h)
            results.append(res)
            print(f"=> {res['nodes_mean']} noeuds, {res['time_mean']}s, score={res['score_mean']}")

    print("\n=== TABLEAU RECAPITULATIF ===\n")
    print(f"{'Profondeur':<12} {'Heuristique':<14} {'Noeuds (moy)':<14} {'Temps moy (s)':<16} {'Temps min':<12} {'Temps max':<12} {'Score moy':<12} {'Score min':<12} {'Score max'}")
    print("-" * 110)
    for res in results:
        print(f"{res['depth']:<12} {res['heuristic']:<14} {res['nodes_mean']:<14} "
              f"{res['time_mean']:<16} {res['time_min']:<12} {res['time_max']:<12} "
              f"{res['score_mean']:<12} {res['score_min']:<12} {res['score_max']}")

    # Sauvegarde CSV pour le rapport
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'analyse_ia.csv')
    keys = results[0].keys()
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(results)

    print(f"\nResultats sauvegardes dans : {csv_path}")
