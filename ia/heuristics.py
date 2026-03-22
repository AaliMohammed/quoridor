def evaluate_h1_simple(board):
    """
    H1 : Basée sur la progression linéaire (Manhattan simplifié).
    Critère : Différence entre les lignes atteintes.
    Interprétation : Très rapide, mais ignore les murs.
    """
    # Distance restante pour P1 (doit aller en ligne 16)
    dist_p1 = 16 - board.player1_pos[0]
    # Distance restante pour P2 (doit aller en ligne 0)
    dist_p2 = board.player2_pos[0]
    
    return dist_p1 - dist_p2

def evaluate_h2_path(board):
    """
    H2 : Basée sur le plus court chemin (BFS).
    Critère : Nombre de pas réels pour atteindre l'arrivée.
    Interprétation : Prend en compte les détours causés par les murs.
    """
    path_p1 = board.get_shortest_path_length(1)
    path_p2 = board.get_shortest_path_length(2)
    
    # Score positif = Avantage pour P2 (l'IA)
    return path_p1 - path_p2

def evaluate_h3_expert(board):
    """
    H3 : Stratégie combinée (BFS + Gestion des ressources).
    Critère : BFS + avantage numérique des murs restants.
    Interprétation : L'IA essaie de gagner tout en économisant ses murs.
    """
    base_score = evaluate_h2_path(board)
    
    # Bonus pour chaque mur que l'IA a en plus de l'adversaire
    wall_bonus = (board.walls_left[2] - board.walls_left[1]) * 2
    
    return base_score + wall_bonus