from engine.board import QuoridorBoard


def is_valid_wall_position(r, c):
    """Vérifie que les coordonnées d'un mur sont dans les limites (0-7)."""
    return 0 <= r <= 7 and 0 <= c <= 7


def is_valid_orientation(orientation):
    """Vérifie que l'orientation est 'H' ou 'V'."""
    return orientation in ('H', 'V')


def is_valid_cell(r, c):
    """Vérifie qu'une case (0-8) est dans les limites du plateau."""
    return 0 <= r <= 8 and 0 <= c <= 8


def validate_move(board, player_id, target_r, target_c):
    """
    Retourne True si le déplacement vers (target_r, target_c) est légal
    pour le joueur donné. Les coordonnées sont en indices internes (0-16).
    """
    return (target_r, target_c) in board.get_valid_moves(player_id)


def validate_wall(board, player_id, r, c, orientation):
    """
    Retourne True si la pose d'un mur en (r, c) avec l'orientation donnée
    est légale pour le joueur donné.
    Effectue toutes les vérifications : limites, superposition, blocage BFS.
    """
    if not is_valid_wall_position(r, c):
        return False, "Coordonnees hors limites (0-7)"
    if not is_valid_orientation(orientation):
        return False, "Orientation invalide : utilisez 'H' ou 'V'"
    if board.walls_left[player_id] <= 0:
        return False, "Plus de murs disponibles"

    ir, ic = 2 * r + 1, 2 * c + 1
    if orientation == 'H':
        if ic + 1 >= 17:
            return False, "Mur hors limites"
        if (board.grid[ir][ic - 1] != ' ' or
                board.grid[ir][ic] != ' ' or
                board.grid[ir][ic + 1] != ' '):
            return False, "Emplacement deja occupe"
    else:
        if ir + 1 >= 17:
            return False, "Mur hors limites"
        if (board.grid[ir - 1][ic] != ' ' or
                board.grid[ir][ic] != ' ' or
                board.grid[ir + 1][ic] != ' '):
            return False, "Emplacement deja occupe"

    # Vérification BFS (simulation temporaire)
    import copy
    temp = copy.deepcopy(board)
    if not temp.place_wall(player_id, r, c, orientation):
        return False, "Ce mur bloquerait totalement un joueur"

    return True, "OK"
