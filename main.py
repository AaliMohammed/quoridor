import os
from engine.board import QuoridorBoard

def clear_screen():
    #juste pour effacer la fenetre terminal 
    os.system('cls' if os.name == 'nt' else 'clear')

def get_user_input():
    """Demande la saisie au format 'ligne col' et retourne des entiers."""
    while True:
        try:
            entry = input("\nEntrez votre destination (ex: 1 4) ou 'q' pour quitter : ")
            if entry.lower() == 'q':
                return None
            r, c = map(int, entry.split())
            # Conversion en coordonnées de grille interne (17x17)
            return r * 2, c * 2
        except ValueError:
            print("Format invalide ! Veuillez entrer deux chiffres séparés par un espace.")

def main():
    game = QuoridorBoard()
    current_player = 1
    
    
    while True:

        clear_screen()
        print("=== BIENVENUE AU QUORIDOR ===")
        game.display()
        
        # Vérification de la victoire [cite: 38, 40]
        winner = game.is_win()
        if winner:
            print(f"\n★ ★ ★ FÉLICITATIONS ! LE JOUEUR {winner} A GAGNÉ ! ★ ★ ★")
            break
            
        print(f"\nTOUR DU JOUEUR {current_player}")
        print(f"Murs restants : {game.walls_left[current_player]}")
        
        # Choix de l'action
        action = input("\nAction : (M)ouvement ou (W)all ? ").upper()

        if action == 'M':
            legal_moves = game.get_valid_moves(current_player)
            readable_moves = [(r//2, c//2) for r, c in legal_moves]
            print(f"Mouvements légaux : {readable_moves}")
            
            target = get_user_input()
            if target is None: break
            
            if game.move_player(current_player, target[0], target[1]):
                current_player = 2 if current_player == 1 else 1
            else:
                input("\n[ERREUR] Déplacement invalide ! (Appuyez sur Entrée)")

        elif action == 'W':
            try:
                print("\nPose d'un mur (Intersections 0-7)")
                r = int(input("Ligne (0-7) : "))
                c = int(input("Colonne (0-7) : "))
                o = input("Orientation (H/V) : ").upper()
                
                if game.place_wall(current_player, r, c, o):
                    current_player = 2 if current_player == 1 else 1
                else:
                    input("\n[ERREUR] Pose impossible (collision ou blocage complet) ! (Entrée)")
            except ValueError:
                input("\n[ERREUR] Entrée invalide ! Utilisez des chiffres. (Entrée)")
        
        elif action == 'Q':
            break


if __name__ == "__main__":
    main()