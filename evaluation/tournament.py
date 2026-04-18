import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import time
from engine.board import QuoridorBoard
from ia.minimax import QuoridorAI

# Limite de sécurité : une partie ne peut dépasser ce nombre de coups
MAX_MOVES_PER_GAME = 300


def play_game(config1, config2, first_player=1):
    """
    Simule une partie complète entre deux IAs sans intervention humaine.

    config = {'name': str, 'h': 'H1'/'H2'/'H3', 'depth': int}
    first_player : 1 ou 2 (qui joue en premier)

    Retourne l'id du joueur gagnant (1 ou 2), ou 0 si limite de coups atteinte.
    """
    board = QuoridorBoard(verbose=False)
    current_player = first_player

    for move_num in range(MAX_MOVES_PER_GAME):
        winner = board.is_win()
        if winner:
            return winner

        config = config1 if current_player == 1 else config2
        ai = QuoridorAI(
            board,
            player_id=current_player,
            depth=config['depth'],
            heuristic_type=config['h'],
            verbose=False
        )

        move = ai.get_best_move()

        if move is None:
            # L'IA n'a plus de coups valides : l'adversaire gagne
            return 3 - current_player

        m_type, data = move
        if m_type == 'M':
            board.move_player(current_player, data[0], data[1])
        else:
            board.place_wall(current_player, data[0], data[1], data[2])

        current_player = 3 - current_player

    # Limite atteinte : le joueur le plus proche de son arrivée gagne
    path1 = board.get_shortest_path_length(1)
    path2 = board.get_shortest_path_length(2)
    if path1 < path2:
        return 1
    elif path2 < path1:
        return 2
    return 0  # Égalité parfaite


def run_tournament(configs, n_games=50):
    """
    Organise un tournoi round-robin entre toutes les IAs.
    Chaque paire s'affronte n_games fois en alternant le joueur qui commence.

    Retourne un dictionnaire de résultats par paire.
    """
    all_results = []
    pairs = [(i, j) for i in range(len(configs)) for j in range(i + 1, len(configs))]

    total_pairs = len(pairs)
    print(f"\n{'='*60}")
    print(f"  TOURNOI : {len(configs)} IAs — {total_pairs} paires — {n_games} parties/paire")
    print(f"{'='*60}")

    for pair_idx, (idx1, idx2) in enumerate(pairs):
        c1 = configs[idx1]
        c2 = configs[idx2]
        name1, name2 = c1['name'], c2['name']

        wins = {name1: 0, name2: 0, 'draw': 0}
        wins_as_first = {name1: 0, name2: 0}  # analyse de l'avantage du premier joueur

        print(f"\n[{pair_idx+1}/{total_pairs}] {name1} vs {name2} ({n_games} parties)")
        pair_start = time.time()

        for game_num in range(n_games):
            # Alterner qui commence pour équilibrer l'avantage du premier joueur
            first = 1 if game_num % 2 == 0 else 2
            winner = play_game(c1, c2, first_player=first)

            if winner == 1:
                wins[name1] += 1
                if first == 1:
                    wins_as_first[name1] += 1
            elif winner == 2:
                wins[name2] += 1
                if first == 2:
                    wins_as_first[name2] += 1
            else:
                wins['draw'] += 1

            # Affichage de la progression
            total_played = game_num + 1
            bar_len = 30
            filled = int(bar_len * total_played / n_games)
            bar = '#' * filled + '-' * (bar_len - filled)
            print(f"  [{bar}] {total_played}/{n_games}  "
                  f"{name1}: {wins[name1]}  {name2}: {wins[name2]}  Nuls: {wins['draw']}",
                  end='\r')

        pair_time = time.time() - pair_start
        print()  # nouvelle ligne après la barre de progression

        total = n_games - wins['draw']
        rate1 = (wins[name1] / n_games * 100) if n_games > 0 else 0
        rate2 = (wins[name2] / n_games * 100) if n_games > 0 else 0

        print(f"  Résultat : {name1} {wins[name1]} ({rate1:.1f}%)  |  "
              f"{name2} {wins[name2]} ({rate2:.1f}%)  |  "
              f"Nuls {wins['draw']}  —  {pair_time:.1f}s")
        print(f"  Victoires en jouant en premier : {name1}: {wins_as_first[name1]}  {name2}: {wins_as_first[name2]}")

        all_results.append({
            'pair': f"{name1} vs {name2}",
            'ia1': name1,
            'ia2': name2,
            f'wins_{name1}': wins[name1],
            f'wins_{name2}': wins[name2],
            'draws': wins['draw'],
            f'winrate_{name1}_%': round(rate1, 1),
            f'winrate_{name2}_%': round(rate2, 1),
            f'wins_first_{name1}': wins_as_first[name1],
            f'wins_first_{name2}': wins_as_first[name2],
        })

    return all_results


def print_summary_table(results):
    """Affiche un tableau récapitulatif des résultats du tournoi."""
    print(f"\n{'='*60}")
    print("  TABLEAU RÉCAPITULATIF DU TOURNOI")
    print(f"{'='*60}")
    print(f"{'Paire':<28} {'IA1 wins':<10} {'IA2 wins':<10} {'Nuls':<8} {'Taux IA1':<10} {'Taux IA2'}")
    print("-" * 80)
    for r in results:
        ia1, ia2 = r['ia1'], r['ia2']
        print(f"{r['pair']:<28} "
              f"{r['wins_' + ia1]:<10} "
              f"{r['wins_' + ia2]:<10} "
              f"{r['draws']:<8} "
              f"{r['winrate_' + ia1 + '_%']}%      "
              f"{r['winrate_' + ia2 + '_%']}%")


def save_results(results, filename=None):
    if filename is None:
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tournament_results.csv')

    if not results:
        return

    # Collecter tous les champs possibles (varient selon les noms d'IA)
    all_fields = []
    seen = set()
    for row in results:
        for k in row.keys():
            if k not in seen:
                all_fields.append(k)
                seen.add(k)

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=all_fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)

    print(f"\nRésultats sauvegardés dans : {filename}")


if __name__ == '__main__':
    # Configuration des 3 IAs : même profondeur, heuristiques différentes
    # La profondeur 2 offre un bon compromis vitesse/qualité pour 50 parties
    configs = [
        {'name': 'IA-H1', 'h': 'H1', 'depth': 2},
        {'name': 'IA-H2', 'h': 'H2', 'depth': 2},
        {'name': 'IA-H3', 'h': 'H3', 'depth': 2},
    ]

    start_total = time.time()
    results = run_tournament(configs, n_games=50)
    total_time = time.time() - start_total

    print_summary_table(results)
    save_results(results)

    print(f"\nDurée totale du tournoi : {total_time:.1f}s ({total_time/60:.1f} min)")
