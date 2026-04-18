import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from engine.board import QuoridorBoard
from ia.heuristics import evaluate_h1_simple, evaluate_h2_path, evaluate_h3_expert


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def fresh_board():
    return QuoridorBoard(verbose=False)


# ─────────────────────────────────────────────
#  1. État initial
# ─────────────────────────────────────────────

class TestInitialState:
    def test_player1_start_position(self):
        b = fresh_board()
        assert b.player1_pos == [0, 8], "P1 doit démarrer en (0, 8)"

    def test_player2_start_position(self):
        b = fresh_board()
        assert b.player2_pos == [16, 8], "P2 doit démarrer en (16, 8)"

    def test_walls_stock(self):
        b = fresh_board()
        assert b.walls_left[1] == 10
        assert b.walls_left[2] == 10

    def test_grid_markers(self):
        b = fresh_board()
        assert b.grid[0][8] == '1'
        assert b.grid[16][8] == '2'

    def test_no_winner_at_start(self):
        b = fresh_board()
        assert b.is_win() is None


# ─────────────────────────────────────────────
#  2. Mouvements valides
# ─────────────────────────────────────────────

class TestValidMoves:
    def test_player1_initial_moves(self):
        """P1 en (0,8) peut aller en bas (2,8), à gauche (0,6) et à droite (0,10)."""
        b = fresh_board()
        moves = b.get_valid_moves(1)
        assert (2, 8) in moves, "P1 doit pouvoir avancer vers (2,8)"
        assert (0, 6) in moves, "P1 doit pouvoir aller à gauche vers (0,6)"
        assert (0, 10) in moves, "P1 doit pouvoir aller à droite vers (0,10)"
        # P1 ne peut pas reculer hors de la grille
        assert (-2, 8) not in moves, "P1 ne peut pas sortir de la grille"

    def test_player2_initial_moves(self):
        """P2 en (16,8) ne peut aller que vers le haut (14,8) au départ."""
        b = fresh_board()
        moves = b.get_valid_moves(2)
        assert (14, 8) in moves
        assert (18, 8) not in moves

    def test_move_respects_wall(self):
        """Un mur horizontal doit bloquer le mouvement correspondant."""
        b = fresh_board()
        # Pose un mur horizontal entre les lignes 0 et 1 au milieu
        b.place_wall(1, 0, 3, 'H')   # mur à l'intersection (0,3)
        # P1 est en (0,8) : le mur en (0,3) ne le concerne pas directement
        # On place P1 proche du mur pour tester
        b.grid[0][8] = ' '
        b.player1_pos = [0, 6]
        b.grid[0][6] = '1'
        moves = b.get_valid_moves(1)
        # Le mur en (0,3) bloque le passage entre (0,6) et (2,6)
        assert (2, 6) not in moves


# ─────────────────────────────────────────────
#  3. Déplacement des joueurs
# ─────────────────────────────────────────────

class TestPlayerMovement:
    def test_valid_move_updates_position(self):
        b = fresh_board()
        result = b.move_player(1, 2, 8)
        assert result is True
        assert b.player1_pos == [2, 8]

    def test_invalid_move_rejected(self):
        b = fresh_board()
        result = b.move_player(1, 4, 8)   # saut de 2 cases non autorisé
        assert result is False
        assert b.player1_pos == [0, 8]

    def test_grid_updated_after_move(self):
        b = fresh_board()
        b.move_player(1, 2, 8)
        assert b.grid[0][8] == ' ', "L'ancienne case doit être vidée"
        assert b.grid[2][8] == '1', "La nouvelle case doit être marquée"

    def test_cannot_move_out_of_bounds(self):
        b = fresh_board()
        result = b.move_player(1, -2, 8)
        assert result is False


# ─────────────────────────────────────────────
#  4. Placement de murs
# ─────────────────────────────────────────────

class TestWallPlacement:
    def test_horizontal_wall_placed(self):
        b = fresh_board()
        result = b.place_wall(1, 0, 0, 'H')
        assert result is True
        assert b.walls_left[1] == 9

    def test_vertical_wall_placed(self):
        b = fresh_board()
        result = b.place_wall(1, 0, 0, 'V')
        assert result is True

    def test_overlapping_wall_rejected(self):
        b = fresh_board()
        b.place_wall(1, 0, 0, 'H')
        result = b.place_wall(2, 0, 0, 'H')
        assert result is False, "Deux murs ne peuvent pas se superposer"

    def test_blocking_wall_rejected(self):
        """Un mur qui isole complètement un joueur doit être refusé."""
        b = fresh_board()
        # Encercle P2 avec des murs — la dernière pose doit être rejetée
        b.place_wall(1, 7, 3, 'H')
        b.place_wall(1, 7, 5, 'H')
        b.place_wall(1, 7, 7, 'H')
        b.place_wall(1, 6, 3, 'H')
        b.place_wall(1, 6, 5, 'H')
        # Le BFS doit empêcher tout isolement total
        for r in range(8):
            for c in range(8):
                for o in ['H', 'V']:
                    if b.walls_left[1] > 0:
                        b.place_wall(1, r, c, o)
        # P2 doit toujours avoir un chemin
        assert b.has_path(2) is True

    def test_no_walls_left(self):
        b = fresh_board()
        b.walls_left[1] = 0
        result = b.place_wall(1, 0, 0, 'H')
        assert result is False


# ─────────────────────────────────────────────
#  5. Détection de victoire
# ─────────────────────────────────────────────

class TestWinDetection:
    def test_player1_wins_at_row_16(self):
        b = fresh_board()
        b.grid[0][8] = ' '
        b.player1_pos = [16, 4]
        b.grid[16][4] = '1'
        # Déplacer P2 ailleurs pour éviter conflit
        b.grid[16][8] = ' '
        b.player2_pos = [14, 8]
        b.grid[14][8] = '2'
        assert b.is_win() == 1

    def test_player2_wins_at_row_0(self):
        b = fresh_board()
        b.grid[16][8] = ' '
        b.player2_pos = [0, 4]
        b.grid[0][4] = '2'
        b.grid[0][8] = ' '
        b.player1_pos = [2, 8]
        b.grid[2][8] = '1'
        assert b.is_win() == 2

    def test_no_winner_midgame(self):
        b = fresh_board()
        b.move_player(1, 2, 8)
        b.move_player(2, 14, 8)
        assert b.is_win() is None


# ─────────────────────────────────────────────
#  6. BFS / Plus court chemin
# ─────────────────────────────────────────────

class TestPathFinding:
    def test_has_path_initial(self):
        b = fresh_board()
        assert b.has_path(1) is True
        assert b.has_path(2) is True

    def test_shortest_path_initial_p1(self):
        """P1 part de la ligne 0, doit atteindre la ligne 16 : 8 pas."""
        b = fresh_board()
        assert b.get_shortest_path_length(1) == 8

    def test_shortest_path_initial_p2(self):
        """P2 part de la ligne 16, doit atteindre la ligne 0 : 8 pas."""
        b = fresh_board()
        assert b.get_shortest_path_length(2) == 8

    def test_wall_increases_path_length(self):
        b = fresh_board()
        initial = b.get_shortest_path_length(1)
        # Mur horizontal devant P1
        b.place_wall(2, 0, 3, 'H')
        b.place_wall(2, 0, 5, 'H')
        after = b.get_shortest_path_length(1)
        assert after >= initial, "Un mur ne peut pas réduire le chemin"


# ─────────────────────────────────────────────
#  7. Saut diagonal (règle avancée)
# ─────────────────────────────────────────────

class TestDiagonalJump:
    def test_diagonal_jump_when_wall_behind_opponent(self):
        """
        Si P2 est juste devant P1 et un mur bloque le saut droit,
        P1 doit pouvoir sauter latéralement.
        """
        b = fresh_board()
        # Placer P1 en (8, 8) et P2 en (10, 8)
        b.grid[0][8] = ' '
        b.player1_pos = [8, 8]
        b.grid[8][8] = '1'
        b.grid[16][8] = ' '
        b.player2_pos = [10, 8]
        b.grid[10][8] = '2'

        # Mur horizontal derrière P2 (entre lignes 10 et 12 au centre)
        b.grid[11][8] = 'H'  # placement direct du mur dans la grille
        b.grid[11][7] = 'H'
        b.grid[11][9] = 'H'

        moves = b.get_valid_moves(1)
        # Le saut droit (12, 8) est bloqué → sauts latéraux (10,6) et (10,10)
        assert (12, 8) not in moves, "Le saut droit doit être bloqué"
        assert (10, 6) in moves or (10, 10) in moves, \
            "Au moins un saut diagonal doit être disponible"


# ─────────────────────────────────────────────
#  8. Heuristiques
# ─────────────────────────────────────────────

class TestHeuristics:
    def test_h1_balanced_at_start(self):
        """En position initiale, H1 doit retourner 0 (plateau symétrique)."""
        b = fresh_board()
        assert evaluate_h1_simple(b, player_id=1) == 0
        assert evaluate_h1_simple(b, player_id=2) == 0

    def test_h1_positive_when_ia_ahead(self):
        """H1 doit être positif si l'IA (P2) est plus avancée que P1."""
        b = fresh_board()
        # P2 avance vers la ligne 0 (P2 doit aller de 16 vers 0)
        b.grid[16][8] = ' '
        b.player2_pos = [4, 8]
        b.grid[4][8] = '2'
        score = evaluate_h1_simple(b, player_id=2)
        assert score > 0, "H1 doit être positif si P2 est très avancé"

    def test_h2_balanced_at_start(self):
        """En position initiale, H2 doit retourner 0 (chemins symétriques)."""
        b = fresh_board()
        assert evaluate_h2_path(b, player_id=1) == 0
        assert evaluate_h2_path(b, player_id=2) == 0

    def test_h2_detects_position_advantage(self):
        """H2 doit être positif pour P2 quand P2 est nettement plus avancé que P1."""
        b = fresh_board()
        # Avancer P2 très près de sa ligne d'arrivée (ligne 0, 2 pas restants)
        b.grid[16][8] = ' '
        b.player2_pos = [4, 8]
        b.grid[4][8] = '2'
        score = evaluate_h2_path(b, player_id=2)
        # P1 a besoin de 8 pas, P2 de 2 → score = 8 - 2 = 6 > 0
        assert score > 0, "H2 doit être positif pour P2 quand P2 est bien plus avancé"

    def test_h3_urgency_near_win(self):
        """H3 doit retourner un score élevé quand le joueur est à 1 pas de gagner."""
        b = fresh_board()
        # Placer P2 à 1 case de la ligne 0
        b.grid[16][8] = ' '
        b.player2_pos = [2, 8]
        b.grid[2][8] = '2'
        score_h3 = evaluate_h3_expert(b, player_id=2)
        score_h2 = evaluate_h2_path(b, player_id=2)
        assert score_h3 > score_h2, "H3 doit surcoter H2 quand le joueur est proche de gagner (urgence)"

    def test_h3_player1_perspective(self):
        """H3 doit fonctionner correctement du point de vue de P1."""
        b = fresh_board()
        b.grid[0][8] = ' '
        b.player1_pos = [14, 8]
        b.grid[14][8] = '1'
        score = evaluate_h3_expert(b, player_id=1)
        assert score > 0, "H3 doit être positif pour P1 quand il est très avancé"
