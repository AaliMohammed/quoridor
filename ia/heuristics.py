def evaluate_h1_simple(board, player_id=2):
    """
    H1 : Basée sur la progression linéaire (distance en lignes).
    Critère : Différence entre les distances restantes jusqu'à la ligne d'arrivée.
    Interprétation : Score positif = avantage pour le joueur `player_id`.
    Très rapide (O(1)), mais ignore totalement les murs posés.
    """
    dist_p1 = 16 - board.player1_pos[0]  # P1 doit atteindre la ligne 16
    dist_p2 = board.player2_pos[0]        # P2 doit atteindre la ligne 0

    if player_id == 2:
        return dist_p1 - dist_p2   # positif = P2 plus proche de gagner
    else:
        return dist_p2 - dist_p1   # positif = P1 plus proche de gagner


def evaluate_h2_path(board, player_id=2):
    """
    H2 : Basée sur le plus court chemin réel (BFS).
    Critère : Nombre de pas réels nécessaires pour atteindre l'arrivée.
    Interprétation : Score positif = l'adversaire a un chemin plus long = avantage pour `player_id`.
    Prend en compte les détours causés par les murs, contrairement à H1.
    """
    path_p1 = board.get_shortest_path_length(1)
    path_p2 = board.get_shortest_path_length(2)

    if player_id == 2:
        return path_p1 - path_p2
    else:
        return path_p2 - path_p1


def evaluate_h3_expert(board, player_id=2):
    """
    H3 : Stratégie experte (BFS + urgence + gestion des ressources).

    Critères combines :
    1. Difference de plus court chemin BFS (identique a H2).
    2. Bonus d'urgence : quand le joueur est a 1-4 pas de la victoire,
       il priorise fortement l'avancement plutot que la pose de murs.
       Cela evite le piege ou l'IA gaspille un tour a poser un mur
       alors qu'une avance directe menerait plus vite a la victoire.
    3. Leger bonus de conservation des murs (simple departage a egalite).

    Score positif = avantage pour le joueur `player_id`.
    """
    base_score = evaluate_h2_path(board, player_id)

    if player_id == 2:
        own_path = board.get_shortest_path_length(2)
        own_walls = board.walls_left[2]
        opp_walls = board.walls_left[1]
    else:
        own_path = board.get_shortest_path_length(1)
        own_walls = board.walls_left[1]
        opp_walls = board.walls_left[2]

    # Bonus d'urgence : prioriser l'avancement quand on est proche de gagner
    if own_path <= 2:
        urgency = 4.0
    elif own_path <= 4:
        urgency = 1.5
    else:
        urgency = 0.0

    # Leger bonus de murs : simple tiebreaker, n'ecrase pas la strategie BFS
    wall_bonus = (own_walls - opp_walls) * 0.3

    return base_score + urgency + wall_bonus
