import os
import time
from engine.board import QuoridorBoard
from ia.minimax import QuoridorAI

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_user_input():
    while True:
        try:
            entry = input("\nEntrez votre destination (ex: 1 4) ou 'q' pour quitter : ")
            if entry.lower() == 'q': return None
            r, c = map(int, entry.split())
            return r * 2, c * 2
        except ValueError:
            print("Format invalide ! Deux chiffres séparés par un espace.")

def main():
    game = QuoridorBoard()
    current_player = 1
    
    clear_screen()
    print("=== CONFIGURATION DU JEU ===")
    mode = input("Jouer contre : (H)umain ou (I)A ? ").upper()
    
    # Si IA, on choisit la difficulté (profondeur) et l'heuristique
    ai_config = None
    if mode == 'I':
        print("\nNiveaux :")
        print("  1 - Facile  (H1 : progression lineaire,  profondeur 1, ~0.2s/coup)")
        print("  2 - Moyen   (H2 : BFS chemin court,      profondeur 2, ~0.7s/coup)")
        print("  3 - Expert  (H3 : BFS + bonus murs,      profondeur 2, ~0.5s/coup)")
        diff = input("Choisissez la difficulte (1-3) : ")
        if diff == '1':
            h_type, depth = 'H1', 1
        elif diff == '2':
            h_type, depth = 'H2', 2
        else:
            h_type, depth = 'H3', 2
        ai_config = {"depth": depth, "h": h_type}

    while True:
        clear_screen()
        print(f"=== QUORIDOR - Mode: {'Humain vs IA' if mode == 'I' else 'Humain vs Humain'} ===")
        game.display()
        
        winner = game.is_win()
        if winner:
            print(f"\n★ ★ ★ FÉLICITATIONS ! LE JOUEUR {winner} A GAGNÉ ! ★ ★ ★")
            break
            
        print(f"\nTOUR DU JOUEUR {current_player}")
        print(f"Murs restants : P1: {game.walls_left[1]} | P2: {game.walls_left[2]}")
        
        # --- LOGIQUE DU TOUR ---
        # Si c'est le tour du Joueur 2 et que le mode IA est activé
        if current_player == 2 and mode == 'I':
            print(f"\n[IA] L'ordinateur réfléchit (Stratégie {ai_config['h']})...")
            
            # Initialisation de l'IA avec la configuration choisie
            brain = QuoridorAI(game, player_id=2, depth=ai_config['depth'], heuristic_type=ai_config['h'])
            
            decision = brain.get_best_move() # Retourne ('M', (r, c)) ou ('W', (r, c, o))
            
            if decision:
                m_type, data = decision
                if m_type == 'M':
                    game.move_player(2, data[0], data[1])
                    print(f"L'IA déplace son pion vers ({data[0]//2}, {data[1]//2})")
                else:
                    game.place_wall(2, data[0], data[1], data[2])
                    print(f"L'IA place un mur {data[2]} en ({data[0]}, {data[1]})")
                
                time.sleep(1.5) # Petite pause pour laisser le temps de lire l'action de l'IA
                current_player = 1
            else:
                print("L'IA ne trouve plus de coups !")
                break

        else:
            # --- TOUR HUMAIN ---
            action = input("\nAction : (M)ouvement ou (W)all ? (Q pour quitter) ").upper()

            if action == 'M':
                legal_moves = game.get_valid_moves(current_player)
                readable_moves = [(r//2, c//2) for r, c in legal_moves]
                print(f"Mouvements légaux : {readable_moves}")
                
                target = get_user_input()
                if target is None: break
                
                if game.move_player(current_player, target[0], target[1]):
                    current_player = 2 if current_player == 1 else 1
                else:
                    input("\n[ERREUR] Déplacement interdit ! (Entrée)")

            elif action == 'W':
                try:
                    r = int(input("Ligne (0-7) : "))
                    c = int(input("Colonne (0-7) : "))
                    o = input("Orientation (H/V) : ").upper()
                    if game.place_wall(current_player, r, c, o):
                        current_player = 2 if current_player == 1 else 1
                    else:
                        input("\n[ERREUR] Pose impossible ! (Entrée)")
                except ValueError:
                    input("\n[ERREUR] Entrée invalide ! (Entrée)")
            
            elif action == 'Q':
                break

if __name__ == "__main__":
    main()