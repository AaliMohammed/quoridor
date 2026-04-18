"""
Script de generation des graphiques pour le rapport.
Lit les fichiers CSV produits par benchmark.py et tournament.py.

Usage :
    python -m evaluation.generate_graphs
"""

import os
import csv
import sys

try:
    import matplotlib
    matplotlib.use('Agg')  # pas besoin d'affichage graphique
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
except ImportError:
    print("matplotlib et numpy sont requis : pip install matplotlib numpy")
    sys.exit(1)

EVAL_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(EVAL_DIR, 'graphs')
os.makedirs(OUT_DIR, exist_ok=True)

COLORS = {'H1': '#4C72B0', 'H2': '#DD8452', 'H3': '#55A868'}
HEURISTICS = ['H1', 'H2', 'H3']


# ─────────────────────────────────────────────────────────────
#  Chargement des CSV
# ─────────────────────────────────────────────────────────────

def load_csv(filename):
    path = os.path.join(EVAL_DIR, filename)
    if not os.path.exists(path):
        print(f"[ATTENTION] Fichier introuvable : {path}")
        print(f"  -> Lancez d'abord : python -m evaluation.{'benchmark' if 'analyse' in filename else 'tournament'}")
        return []
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


# ─────────────────────────────────────────────────────────────
#  Graphiques Benchmark
# ─────────────────────────────────────────────────────────────

def graph_time_vs_depth(data):
    """Temps de calcul moyen par heuristique en fonction de la profondeur."""
    fig, ax = plt.subplots(figsize=(8, 5))

    for h in HEURISTICS:
        rows = [r for r in data if r['heuristic'] == h]
        depths = [int(r['depth']) for r in rows]
        times = [float(r['time_mean']) for r in rows]
        ax.plot(depths, times, marker='o', label=h, color=COLORS[h], linewidth=2)

    ax.set_xlabel('Profondeur de recherche', fontsize=12)
    ax.set_ylabel('Temps moyen (secondes)', fontsize=12)
    ax.set_title('Temps de calcul par heuristique selon la profondeur', fontsize=13)
    ax.legend(title='Heuristique')
    ax.set_xticks([1, 2, 3])
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    path = os.path.join(OUT_DIR, 'benchmark_temps_vs_profondeur.png')
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  [OK] {path}")


def graph_nodes_vs_depth(data):
    """Nombre de noeuds explores par heuristique en fonction de la profondeur."""
    fig, ax = plt.subplots(figsize=(8, 5))

    for h in HEURISTICS:
        rows = [r for r in data if r['heuristic'] == h]
        depths = [int(r['depth']) for r in rows]
        nodes = [int(r['nodes_mean']) for r in rows]
        ax.plot(depths, nodes, marker='s', label=h, color=COLORS[h], linewidth=2)

    ax.set_xlabel('Profondeur de recherche', fontsize=12)
    ax.set_ylabel('Noeuds explores (moyenne)', fontsize=12)
    ax.set_title('Noeuds explores par heuristique selon la profondeur', fontsize=13)
    ax.legend(title='Heuristique')
    ax.set_xticks([1, 2, 3])
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    path = os.path.join(OUT_DIR, 'benchmark_noeuds_vs_profondeur.png')
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  [OK] {path}")


def graph_time_bar(data):
    """Comparaison des temps en barres groupees pour chaque profondeur."""
    depths = sorted(set(int(r['depth']) for r in data))
    x = np.arange(len(depths))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9, 5))

    for i, h in enumerate(HEURISTICS):
        times = []
        errors = []
        for d in depths:
            row = next((r for r in data if r['heuristic'] == h and int(r['depth']) == d), None)
            if row:
                t_mean = float(row['time_mean'])
                t_min = float(row['time_min'])
                t_max = float(row['time_max'])
                times.append(t_mean)
                errors.append([t_mean - t_min, t_max - t_mean])
            else:
                times.append(0)
                errors.append([0, 0])

        err_low = [e[0] for e in errors]
        err_high = [e[1] for e in errors]
        ax.bar(x + i * width, times, width, label=h, color=COLORS[h],
               yerr=[err_low, err_high], capsize=4, alpha=0.85)

    ax.set_xlabel('Profondeur', fontsize=12)
    ax.set_ylabel('Temps (secondes)', fontsize=12)
    ax.set_title('Comparaison des temps de calcul (avec min/max)', fontsize=13)
    ax.set_xticks(x + width)
    ax.set_xticklabels([f'Profondeur {d}' for d in depths])
    ax.legend(title='Heuristique')
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    path = os.path.join(OUT_DIR, 'benchmark_comparaison_barres.png')
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  [OK] {path}")


# ─────────────────────────────────────────────────────────────
#  Graphiques Tournoi
# ─────────────────────────────────────────────────────────────

def graph_tournament_winrates(data):
    """Taux de victoire de chaque IA pour chaque paire."""
    if not data:
        return

    fig, axes = plt.subplots(1, len(data), figsize=(5 * len(data), 5))
    if len(data) == 1:
        axes = [axes]

    for ax, row in zip(axes, data):
        ia1 = row['ia1']
        ia2 = row['ia2']
        w1 = int(row[f'wins_{ia1}'])
        w2 = int(row[f'wins_{ia2}'])
        draws = int(row['draws'])
        total = w1 + w2 + draws

        labels = [ia1, ia2]
        values = [w1, w2]
        colors = [COLORS.get(ia1[-2:], '#7B9EC7'), COLORS.get(ia2[-2:], '#E8A87C')]

        if draws > 0:
            labels.append('Nul')
            values.append(draws)
            colors.append('#AAAAAA')

        wedges, texts, autotexts = ax.pie(
            values, labels=labels, colors=colors,
            autopct=lambda p: f'{p:.1f}%\n({int(round(p * total / 100))})',
            startangle=90, textprops={'fontsize': 10}
        )
        for autotext in autotexts:
            autotext.set_fontsize(9)

        ax.set_title(f'{ia1} vs {ia2}\n({total} parties)', fontsize=11)

    plt.suptitle('Resultats du tournoi — Taux de victoire par paire', fontsize=13, y=1.02)
    plt.tight_layout()
    path = os.path.join(OUT_DIR, 'tournoi_taux_victoire.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  [OK] {path}")


def graph_tournament_first_player_advantage(data):
    """Analyse de l'avantage du premier joueur par paire."""
    if not data:
        return

    pairs = []
    adv_first = []
    adv_second = []

    for row in data:
        ia1 = row['ia1']
        ia2 = row['ia2']
        pairs.append(f'{ia1}\nvs\n{ia2}')
        adv_first.append(int(row.get(f'wins_first_{ia1}', 0)) +
                         int(row.get(f'wins_first_{ia2}', 0)))
        total_wins = int(row[f'wins_{ia1}']) + int(row[f'wins_{ia2}'])
        adv_second.append(total_wins - adv_first[-1])

    x = np.arange(len(pairs))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width/2, adv_first, width, label='Victoires du 1er joueur', color='#4C72B0', alpha=0.85)
    ax.bar(x + width/2, adv_second, width, label='Victoires du 2e joueur', color='#DD8452', alpha=0.85)

    ax.set_xlabel('Paire', fontsize=12)
    ax.set_ylabel('Nombre de victoires', fontsize=12)
    ax.set_title("Avantage du premier joueur par paire", fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels(pairs, fontsize=9)
    ax.legend()
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    path = os.path.join(OUT_DIR, 'tournoi_avantage_premier_joueur.png')
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  [OK] {path}")


def graph_tournament_summary_bar(data):
    """Bilan global : nombre total de victoires par IA."""
    if not data:
        return

    totals = {}
    for row in data:
        ia1, ia2 = row['ia1'], row['ia2']
        totals[ia1] = totals.get(ia1, 0) + int(row[f'wins_{ia1}'])
        totals[ia2] = totals.get(ia2, 0) + int(row[f'wins_{ia2}'])

    names = list(totals.keys())
    values = [totals[n] for n in names]
    colors = [COLORS.get(n[-2:], '#888888') for n in names]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(names, values, color=colors, alpha=0.85, edgecolor='white', linewidth=1.2)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                str(val), ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax.set_xlabel('Intelligence Artificielle', fontsize=12)
    ax.set_ylabel('Victoires totales (toutes paires)', fontsize=12)
    ax.set_title('Classement global du tournoi', fontsize=13)
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    path = os.path.join(OUT_DIR, 'tournoi_classement_global.png')
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  [OK] {path}")


# ─────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=== GENERATION DES GRAPHIQUES ===\n")

    # --- Benchmark ---
    bench_data = load_csv('analyse_ia.csv')
    if bench_data:
        print("Benchmark :")
        graph_time_vs_depth(bench_data)
        graph_nodes_vs_depth(bench_data)
        graph_time_bar(bench_data)

    # --- Tournoi ---
    tour_data = load_csv('tournament_results.csv')
    if tour_data:
        print("\nTournoi :")
        graph_tournament_winrates(tour_data)
        graph_tournament_first_player_advantage(tour_data)
        graph_tournament_summary_bar(tour_data)

    print(f"\nTous les graphiques sont dans : {OUT_DIR}")
