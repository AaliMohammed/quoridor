from collections import deque

class QuoridorBoard:
    def __init__(self):
        #Taille 17x17 pour inclure les espaces pour les murs 
        self.size = 17
        self.grid = [[' ' for _ in range(self.size)] for _ in range(self.size)]

        #Positions initiales (Coordonnees paires)
        self.player1_pos = [0,8] #ligne 0,milieu
        self.player2_pos = [16,8] #ligne 16 , milieu

        #Stock de murs pour chaque joueur
        self.walls_left = {1:10,2:10}

        #initialisation des pions sur la grille
        self.grid[self.player1_pos[0]][self.player1_pos[1]] = '1'
        self.grid[self.player2_pos[0]][self.player2_pos[1]] = '2'

    def is_win(self):
        """Verifie les conditions de victoires"""
        if self.player1_pos[0] == 16:
            return 1
        if self.player2_pos[0] == 0:
            return 2
        return None
    
    def display(self):
        # En-tête des colonnes (un espace de décalage pour l'indice de ligne)
        print("\n    0  1  2  3  4  5  6  7  8")
        
        # Bordure supérieure : + puis 8 fois (==+)
        top_border = "   +" + "==+" * 9
        print(top_border)
        
        for r in range(9):
            # --- Ligne des Pions (Indices pairs) ---
            # Format : "0 |P1 |  |  |"
            line_cells = f" {r} |"
            for c in range(9):
                cell = self.grid[2*r][2*c]
                char = "P1" if cell == '1' else "P2" if cell == '2' else "  "
                
                # Mur vertical interne
                if c < 8:
                    wall_v = "|" if self.grid[2*r][2*c+1] == 'V' else " "
                    line_cells += f"{char}{wall_v}"
                else:
                    line_cells += f"{char}" # Fin de cellule sans mur après
            line_cells += "|"
            print(line_cells)
            
            # --- Ligne des Murs Horizontaux (Indices impairs) ---
            if r < 8:
                line_walls = "   +"
                for c in range(9):
                    # Mur horizontal (==) ou vide (  )
                    wall_h = "==" if self.grid[2*r+1][2*c] == 'H' else "  "
                    line_walls += f"{wall_h}+"
                print(line_walls)

        # Bordure inférieure
        print(top_border)
    
    def get_valid_moves(self, player_id):
        """retourne la liste des cordonnees (r,c) accesssible pour le joueur"""
        moves = []
        r, c = self.player1_pos if player_id == 1 else self.player2_pos
        opponent_pos = self.player2_pos if player_id == 1 else self.player1_pos

        # Directions possibles : haut, bas, gauche, droite 
        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

        for dr, dc in directions:
            nr, nc = r + dr, c + dc

            # 1- Vérifier si on reste dans la grille (0 à 16 inclus)
            if 0 <= nr < self.size and 0 <= nc < self.size: 
                 # 2- Vérifier s'il y a un mur entre la position actuelle et la cible
                 wr, wc = r + dr // 2, c + dc // 2
                 if self.grid[wr][wc] not in ['H', 'V']:
                    
                    # 3- Gérer la rencontre avec l'adversaire (Saut)
                    if [nr, nc] == opponent_pos:
                        snr, snc = nr + dr, nc + dc
                        # Vérifier si le saut reste dans la grille
                        if 0 <= snr < self.size and 0 <= snc < self.size:
                            swr, swc = nr + dr // 2, nc + dc // 2
                            # Vérifier s'il n'y a pas de mur derrière l'adversaire
                            if self.grid[swr][swc] not in ['H', 'V']:
                                moves.append((snr, snc))
                    else:
                        moves.append((nr, nc)) 
        return moves

    def move_player(self, player_id, target_r, target_c):
        """Déplace le pion après validation"""
        valid_moves = self.get_valid_moves(player_id)
        
        if (target_r, target_c) in valid_moves:
            # Effacer l'ancienne position
            old_r, old_c = self.player1_pos if player_id == 1 else self.player2_pos
            self.grid[old_r][old_c] = ' '
            
            # Mettre à jour les coordonnées
            if player_id == 1:
                self.player1_pos = [target_r, target_c]
            else:
                self.player2_pos = [target_r, target_c]
            
            # Marquer la nouvelle position
            self.grid[target_r][target_c] = str(player_id)
            return True
        return False       

    
    def has_path(self,player_id):
        """verifier par l'algorithme BFS si un chemin existe vers la victoire"""
        #position de depart du joueur concerné
        start = tuple(self.player1_pos if player_id == 1 else self.player2_pos)
        #ligne d'arrive cible 
        goal_row = 16 if player_id == 1 else 0

        queue = deque([start])
        visited = {start}

        while queue:
            r, c = queue.popleft()
            #si on atteint n'import quelle case de la ligne d'arrivee
            if r == goal_row:
                return True

            #tester les 4 direction 
            for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                nr, nc = r + dr, c + dc 

                if 0 <= nr <= 17 and 0 <= nc <=17:
                    #verifier les murs
                    wr, wc = r + dr//2, c + dc//2
                    if self.grid[wr][wc] not in ['H','v'] and (nr,nc) not in visited:
                        visited.add((nr,nc))
                        queue.append((nr,nc))
        return False
    

    def place_wall(self, player_id, r, c, orientation):
        """r,c : cordonnees de l'intersection (0,7) avec orientation 'H' ou 'V' 
        'H' pour un murs horizontal et 'V' pour un mur vertical
        """
        #verification s'il reste des murs pour le joueur
        if self.walls_left[player_id] <= 0:
            print("plus de murs disponibles !!!")
            return False

        #conversion on coordonnees internes(impaires)
        #l'intersection (r,c) correspond a l'index (2*r+1, 2*c+1)
        ir, ic = 2*r+1, 2*c+1

        #verifier si la place est libre ou non 
        if orientation == 'H':
            # Un mur horizontal occupe (ir, ic-1), (ir, ic) et (ir, ic+1)
            if ic + 1 >= 17 or self.grid[ir][ic-1] != ' ' or self.grid[ir][ic+1] != ' ' or self.grid[ir][ic] != ' ':
                return False
            # Placement temporaire pour vérification BFS
            self.grid[ir][ic-1] = self.grid[ir][ic+1] = self.grid[ir][ic] = 'H'
        
        elif orientation == 'V':
            # Un mur vertical occupe (ir-1, ic), (ir, ic) et (ir+1, ic)
            if ir + 1 >= 17 or self.grid[ir-1][ic] != ' ' or self.grid[ir+1][ic] != ' ' or self.grid[ir][ic] != ' ':
                return False
            # Placement temporaire
            self.grid[ir-1][ic] = self.grid[ir+1][ic] = self.grid[ir][ic] = 'V'

        # 4. Validation BFS : Est-ce qu'un chemin existe encore pour les deux joueurs ?
        if self.has_path(1) and self.has_path(2):
            self.walls_left[player_id] -= 1
            return True
        else:
            # Annulation du placement si le chemin est bloqué
            if orientation == 'H':
                self.grid[ir][ic-1] = self.grid[ir][ic+1] = self.grid[ir][ic] = ' '
            else:
                self.grid[ir-1][ic] = self.grid[ir+1][ic] = self.grid[ir][ic] = ' '
            print("Action interdite : vous ne pouvez pas bloquer tous les accès !")
            return False
        
    