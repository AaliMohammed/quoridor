import copy
import time
from ia.heuristics import evaluate_h1_simple, evaluate_h2_path, evaluate_h3_expert

class QuoridorAI:
    def __init__(self, board, player_id, depth=2, heuristic_type='H2'):
        self.board = board
        self.player_id = player_id
        self.depth = depth
        self.heuristic_type = heuristic_type
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
            # On vérifie que le coup est valide avant de descendre dans l'arbre
            if self._apply_move(temp_board, self.player_id, move_type, data):
                score = self._minimax(temp_board, self.depth - 1, alpha, beta, False)
                
                if score > best_score:
                    best_score = score
                    best_move = (move_type, data)
                
                alpha = max(alpha, best_score)

        execution_time = time.time() - start_time
        # Ces prints sont cruciaux pour l'analyse expérimentale
        print(f"--- [Rapport IA] ---")
        print(f"Heuristique : {self.heuristic_type} | Profondeur : {self.depth}")
        print(f"Nœuds explorés : {self.nodes_explored}")
        print(f"Temps de calcul : {execution_time:.4f}s")
        return best_move

    def _get_score(self, board):
        """Fait le lien avec le fichier heuristics.py selon le sujet 5.3."""
        if self.heuristic_type == 'H1':
            return evaluate_h1_simple(board)
        elif self.heuristic_type == 'H3':
            return evaluate_h3_expert(board)
        else:
            return evaluate_h2_path(board) # Par défaut H2 (BFS)

    def _minimax(self, board, depth, alpha, beta, is_maximizing):
        self.nodes_explored += 1
        
        winner = board.is_win()
        # On ajuste le score par la profondeur pour préférer les victoires rapides
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
            opp_id = 1 if self.player_id == 2 else 2
            for move_type, data in self._get_ordered_moves(board, opp_id):
                temp_board = copy.deepcopy(board)
                if self._apply_move(temp_board, opp_id, move_type, data):
                    eval = self._minimax(temp_board, depth - 1, alpha, beta, True)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, min_eval)
                    if beta <= alpha:
                        break
            return min_eval

    def _get_ordered_moves(self, board, p_id):
        """Priorise les mouvements pour optimiser l'élagage alpha-bêta."""
        moves = []
        # Les mouvements de pions sont prioritaires car ils finissent la partie
        for m in board.get_valid_moves(p_id):
            moves.append(('M', m))
        
        if board.walls_left[p_id] > 0:
            # On limite la recherche des murs pour respecter les contraintes de temps
            # du sujet Analyse expérimentale
            for r in range(0, 8, 2):
                for c in range(0, 8, 2):
                    for o in ['H', 'V']:
                        moves.append(('W', (r, c, o)))
        return moves

    def _apply_move(self, board, p_id, move_type, data):
        if move_type == 'M':
            return board.move_player(p_id, data[0], data[1])
        else:
            # data = (r, c, o)
            return board.place_wall(p_id, data[0], data[1], data[2])