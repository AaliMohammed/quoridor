import copy
import time
from ia.heuristics import evaluate_h1_simple, evaluate_h2_path, evaluate_h3_expert

class QuoridorAI:
    def __init__(self, board, player_id, depth=2, heuristic_type='H2', verbose=True):
        self.board = board
        self.player_id = player_id
        self.opponent_id = 2 if player_id == 1 else 1
        self.depth = depth
        self.heuristic_type = heuristic_type
        self.verbose = verbose
        self.nodes_explored = 0

    def get_best_move(self):
        """Trouve le meilleur coup en utilisant Alpha-Beta."""
        self.nodes_explored = 0
        start_time = time.time()

        alpha = float('-inf')
        beta = float('inf')
        best_move = None
        best_score = float('-inf')

        moves = self._get_ordered_moves(self.board, self.player_id)

        for move_type, data in moves:
            temp_board = copy.deepcopy(self.board)
            if self._apply_move(temp_board, self.player_id, move_type, data):
                score = self._minimax(temp_board, self.depth - 1, alpha, beta, False)

                if score > best_score:
                    best_score = score
                    best_move = (move_type, data)

                alpha = max(alpha, best_score)

        execution_time = time.time() - start_time
        self.best_score = best_score  # accessible après l'appel pour le benchmark
        if self.verbose:
            print(f"--- [Rapport IA] ---")
            print(f"Heuristique : {self.heuristic_type} | Profondeur : {self.depth}")
            print(f"Nœuds explorés : {self.nodes_explored}")
            print(f"Temps de calcul : {execution_time:.4f}s")
        return best_move

    def _get_score(self, board):
        """Évalue le plateau du point de vue de self.player_id."""
        if self.heuristic_type == 'H1':
            return evaluate_h1_simple(board, self.player_id)
        elif self.heuristic_type == 'H3':
            return evaluate_h3_expert(board, self.player_id)
        else:
            return evaluate_h2_path(board, self.player_id)

    def _minimax(self, board, depth, alpha, beta, is_maximizing):
        self.nodes_explored += 1

        winner = board.is_win()
        # Préférer les victoires rapides (bonus de profondeur)
        if winner == self.player_id: return 1000 + depth
        if winner is not None: return -1000 - depth

        if depth == 0:
            return self._get_score(board)

        if is_maximizing:
            max_eval = float('-inf')
            for move_type, data in self._get_ordered_moves(board, self.player_id):
                temp_board = copy.deepcopy(board)
                if self._apply_move(temp_board, self.player_id, move_type, data):
                    eval = self._minimax(temp_board, depth - 1, alpha, beta, False)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, max_eval)
                    if beta <= alpha:
                        break
            return max_eval
        else:
            min_eval = float('inf')
            for move_type, data in self._get_ordered_moves(board, self.opponent_id):
                temp_board = copy.deepcopy(board)
                if self._apply_move(temp_board, self.opponent_id, move_type, data):
                    eval = self._minimax(temp_board, depth - 1, alpha, beta, True)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, min_eval)
                    if beta <= alpha:
                        break
            return min_eval

    def _get_ordered_moves(self, board, p_id):
        """
        Priorise les mouvements pour optimiser l'élagage alpha-bêta.

        Ordre d'exploration :
        1. Déplacements de pions (peuvent terminer la partie immédiatement).
        2. Placements de murs triés par proximité avec l'adversaire :
           les murs proches de l'adversaire ont plus de chances de bloquer
           son chemin, ce qui produit de meilleures bornes alpha/bêta plus tôt
           et améliore significativement l'élagage.
        """
        moves = []
        # 1. Mouvements de pions en priorité absolue
        for m in board.get_valid_moves(p_id):
            moves.append(('M', m))

        if board.walls_left[p_id] > 0:
            opp_id = 3 - p_id
            opp_pos = board.player2_pos if opp_id == 2 else board.player1_pos
            opp_r, opp_c = opp_pos[0] // 2, opp_pos[1] // 2

            # 2. Murs explorés en partant des lignes/colonnes les plus proches
            #    de l'adversaire → murs bloquants en premier = meilleures bornes
            #    alpha/bêta plus tôt = élagage plus efficace.
            #    Tri en O(8 log 8) sur les indices, minimal overhead.
            rows = sorted(range(8), key=lambda r: abs(r - opp_r))
            cols = sorted(range(8), key=lambda c: abs(c - opp_c))
            for r in rows:
                for c in cols:
                    for o in ['H', 'V']:
                        moves.append(('W', (r, c, o)))

        return moves

    def _apply_move(self, board, p_id, move_type, data):
        if move_type == 'M':
            return board.move_player(p_id, data[0], data[1])
        else:
            return board.place_wall(p_id, data[0], data[1], data[2])
