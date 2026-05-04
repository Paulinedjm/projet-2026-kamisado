import socket 
import struct 
import random
import json
import threading
import math

def envoyé(client):
    envoi= {
      "request": "subscribe",
      "port": 8888,
      "name": "Pauline",
      "matricules": ["24343", "24160"]
    }
    #preparation du message + taille
    message_json= json.dumps(envoi).encode("utf-8")
    taille= len(message_json)

    #envoie (4 octect, taille, contenu du message)
    header=struct.pack( "I", taille)

    taille_totale=client.send(header+ message_json)
    
    return taille_totale, len(header)+len(message_json)


def recevoir(client, taille_envoyé, taille_attendu):

    if taille_envoyé== taille_attendu :
        
        # lire la taille de la réponse 4 oct
        response= client.recv(4)
        taille_response= struct.unpack("I", response)[0]
    
        #recevoir 
        data= client.recv(taille_response)
        #On décode et on transforme en dictionnaire
        response = json.loads(data.decode("utf-8"))
        
        # Écriture dans le fichier
        with open("eval.json", "w") as f:
            json.dump(response, f, indent=4)
   
    else : 
        message_reçu_erreur= {
          "response": "error",
          "error": "error message"
        }
        with open("eval.json", "w") as f:
            json.dump(message_reçu_erreur, f, indent=4)




#def attendre_ping():
    # On crée un nouveau socket pour écouter le serveur
        # Permet de relancer le script sans attendre que le port se libère
        #listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        #while True:
            # On accepte la connexion entrante du serveur
            
            #with server_sock:
            #    # Lire la taille (4 octets - entier non signé "I")
            #    header = lsiterner.recv(server_sock, 4)
            #    #mesure la taille
            #    taille = struct.unpack("I", header)[0]
            #    #lit exactement le nombre d'octet annonce
            #    data = receive_all(server_sock, taille)
            #    requete = json.loads(data.decode("utf-8"))

              
              
serverAddress= ("127.0.0.1", 3000)


def state(client):
    state_all= client.recv(4)
    taille_response= struct.unpack("I", state_all)[0]
    #cree une boucle pour etre sur qu'on recoit tout le message 
    data = b""
    while len(data) < taille_response:
        morceau = client.recv(taille_response - len(data))
        data += morceau 
    #On décode et on transforme en dictionnaire
    response = json.loads(data.decode("utf-8"))

    #écrire dans le fichier json eval l'état de la board, le joueur qui doit jouer, et le pion à jouer
    with open("eval.json", "w") as f:
        json.dump(response, f, indent=4)
    
    return response

def envoyer_coup(client, move):
    reponse = {
        "response": "move",
        "move": move,
        "message" : "On joue!"
    }
    message_json = json.dumps(reponse).encode("utf-8")
    header = struct.pack("I", len(message_json))
    client.send(header + message_json)



def find_tower_position(board, color_to_find, player_id):  ##  board: la grille 8x8, color_to_find: la couleur imposée (ex: "RED"),  player_id: ton numéro de joueur (ex: 0 ou 1)
    
    current_player = "dark" if player_id == 0 else "light"
    for r in range(8): # Parcourt les lignes de 0 à 7
        for c in range(8): # Parcourt les colonnes de 0 à 7
            case = board[r][c]
            
            # On vérifie si la case n'est pas vide
            if case[1] is not None :
                title_color= case[1][0]
                title_kind=case[1][1]
                if title_kind==current_player:
                    if color_to_find is None:
                        return r,c
                    elif title_color==color_to_find:
            
                      return r, c # On a trouvé, On renvoie la position 
                    
    return None # Si on n'a rien trouvé (ne devrait pas arriver)

def get_legal_moves(state, color_to_play, player_id):   # state: le plateau (grille 8x8), color_to_play: la couleur de la tour que je DOIS bouger, player_id: 0 pour le joueur du bas (monte), 1 pour le joueur du haut (descend)
    moves = [] #on cree une liste de coordonnées de coups possible
    
    # 1. Trouver les coordonnées (r, c) de la tour de la bonne couleur
    pos_r, pos_c = find_tower_position(state, color_to_play, player_id)
    
    # 2. Définir les directions "avant" selon le joueur
    direction = -1 if player_id == 0 else 1 #determine si on doit monter ou descendre dans le board en fonction du joueur qui joue, Si player_id == 0, on monte (ligne -1), si 1 on descend (ligne +1)
    
    # Les 3 colonnes à tester : gauche (-1), tout droit (0), droite (+1), explore les 3 directions 
    for dc in [-1, 0, 1]:
        r, c = pos_r + direction, pos_c + dc
        
        # Tant qu'on est sur le plateau et que la case est vide
        while 0 <= r < 8 and 0 <= c < 8 and state[r][c][1] == None:
            moves.append((r, c)) # On ajoute la coordonnée comme coup possible
            
            # On continue d'avancer dans cette direction (comme une tour d'échecs)
            r += direction
            c += dc
            
    return moves

#Determination victoire 
def check_win(player_id, board):
    if player_id==0 :
        line=0 #joueur 1 va à 0
        kind= "dark"
    else : 
        line=7 #joueur 2 va à 7
        kind= "light"
    
    for col in range(8):
        case= board[line][col]
        if case[1] is not None and case[1][1]== kind:  #si à la ligne 0 ou 7 pour chaque colone, on a un pion qui a notre kind alors on a gagné 
            
            return True
                  
    return False #il y a pas encore ou pas du tout de win  

#Simuler un move
def simulation_move(minimax_board, player_id, color, r_arr, c_arr):
    #1 : trouver la pièce à bouger (par rapport à la case de l'adv)
    
    #Tour de la bonne couleur (color) et le bon joueur(player_id)
    pos = find_tower_position(minimax_board, color, player_id)
    r_dep, c_dep = pos #pos de départ

    #sauvegarde la pièce (case=(couleur_case, piece) )
    piece = minimax_board[r_dep][c_dep][1]
    #sauvegarder la case d'arrivé (car on va la modifier donc on doit pouvoir la restaurer après)
    case_arrivee = minimax_board[r_arr][c_arr]
    
    #ex: je veux aller de (5,3)= ("blue", (pièce)) à (2,3)=("green", None)
    # enregistrer la case (2,3) ce qu'il y avait avant 
    #simuler le deplacement (2,3)= ("green", (pièce))
    #du coup (5,3)= ("blue", None) après on efface le deplacement 

    #2
    #Simuler le déplacement 
    minimax_board[r_arr][c_arr] = (minimax_board[r_arr][c_arr][0], piece)
    minimax_board[r_dep][c_dep] = (minimax_board[r_dep][c_dep][0], None)
    return r_dep, c_dep, case_arrivee, piece


def unmake_move(board, r_dep, c_dep, r_arr, c_arr, case_arrivee, piece_dep):
    """Annule le coup"""
    board[r_dep][c_dep] = (board[r_dep][c_dep][0], piece_dep)
    board[r_arr][c_arr] = case_arrivee

#fonction qui évalue les scores pour choisir le meilleur coup
def evaluate(minimax_board, player_id, color_to_play):
    opponent = 1 if player_id == 0 else 0
    score = 0

    if check_win(player_id, minimax_board): 
        return 1.0  # Victoire immédiate
    if check_win(opponent, minimax_board): 
        return -1.0 # Défaite immédiate

    my_goal = 0 if player_id == 0 else 7
    opponent_goal = 7 if player_id == 0 else 0

    # Heuristique de "Deadlock" (Blocage)
    if color_to_play is not None:
        direct_moves = get_legal_moves(minimax_board, color_to_play, player_id)            
        if len(direct_moves) == 0:        
                score -= 4.0  

    # Mobilité et Menaces
    my_mobility = 0
    opps_mobility = 0
    our_type = "dark" if player_id == 0 else "light"
    opponent_type = "light" if player_id == 0 else "dark"

    for r in range(8):
        for c in range(8):
            case = minimax_board[r][c]
            if case[1] is not None:
                tower_color, tower_type = case[1][0], case[1][1]
                
                if tower_type == our_type:
                    my_moves = get_legal_moves(minimax_board, tower_color, player_id)
                    my_mobility += len(my_moves)
                    # Menace directe de gagner
                    for coup_r, _ in my_moves:
                        if coup_r == my_goal:
                            score += 1.5
                            break 
                            
                elif tower_type == opponent_type:
                    opps_moves = get_legal_moves(minimax_board, tower_color, opponent)
                    opps_mobility += len(opps_moves)
                    # Menace adverse directe
                    for pos_r, _ in opps_moves:
                        if pos_r == opponent_goal:
                            score -= 2.0
                            break

    score += (my_mobility - opps_mobility) * 0.1


    return math.tanh(score)

def negamax(minimax_board, depth, player_id, color, alpha, beta):
    opps = 1 if player_id == 0 else 0
    #Condition d'arret: si depth==0 fin d'exploration pour pouvoir evaluer
    if check_win(player_id, minimax_board) or check_win(opps, minimax_board) or depth == 0:
        return evaluer(minimax_board, player_id, color)

    #Recuperation des coups possibles sinon on évalue la pos directement  
    coups = get_legal_moves(minimax_board, color, player_id)
    if not coups:
        return evaluer(minimax_board, player_id, color)
    
    #initialise le score maximum
    scoreMax = float('-inf')
    
    #on teste chaque coup possible
    for r, c in coups:
        #recuperation de la couleur de notre case d'arrivé 
        couleur_suivante = minimax_board[r][c][0]

        #Position de départ de la pièce qu'on va bouger 
        pos = find_tower_position(minimax_board, color, player_id)
        piece = minimax_board[pos[0]][pos[1]][1]

        #on simule un coup 
        r_dep, c_dep, ancienne_arrivee, piece = simulation_move(minimax_board, player_id, color, r, c)

        score = -negamax(minimax_board, depth - 1, opps, couleur_suivante, -beta, -alpha)
  
        unmake_move(minimax_board, r_dep, c_dep, r, c, ancienne_arrivee, piece)
        
        #on garde le meilleur coup trouvé 
        if score > scoreMax:
                scoreMax = score
        if scoreMax > alpha:
                alpha = scoreMax
        if alpha >= beta:
            break #il n'a pas besoin d'explorer cette branche 
        
    return scoreMax

def meilleur_coup(board, player_id, color):
    opps = 1 if player_id == 0 else 0 

    coups = get_legal_moves(board, color, player_id)
    # Si la liste est vide, on s'arrête tout de suite
    if not coups:
        return None
    
    # Initialiser avec le premier coup de la liste 
    best_score = float('-inf')
    best_move = coups[0]

    #on test encore chaque coup possible
    for r, c in coups:
        couleur_suivante = board[r][c][0]

        pos = find_tower_position(board, color, player_id)
        piece = board[pos[0]][pos[1]][1]
        r_dep, c_dep, ancienne_arrivee, piece = simulation_move(board, player_id, color, r, c)
        
        score = -negamax(board,4, opps, couleur_suivante, float("-inf"), float("inf"))
        unmake_move(board, r_dep, c_dep, r, c, ancienne_arrivee, piece)
        

        if score > best_score:
            best_score = score
            best_move = (r, c)
    return best_move


    


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((serverAddress)) 

    taille_envoyé, taille_attendu = envoyé(client) #recupérer la taille du messages envoyé
    recevoir(client, taille_envoyé, taille_attendu)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
    listener.bind(("0.0.0.0", 8888))
    listener.listen()

    print("listen on 8888")
    while True:
        client, addr= listener.accept()
        print(f"accept connection from {addr}")
       
        with client : 
            message = state(client)
         
            if message["request"]== "ping":
        
                # Préparation et envoi du pong
                reponse = json.dumps({"response": "pong"}).encode("utf-8")
                taille_resp = struct.pack("I", len(reponse))
                client.sendall(taille_resp + reponse)
                print(f"Ping reçu de -> Pong envoyé !")
    
            elif message["request"] == "play":
    
                # On récupère les infos du message serveur
                game_state = message["state"]
                plateau = game_state["board"]
                couleur_voulue = game_state["color"]
                mon_id = game_state["current"]

                position_depart = find_tower_position(plateau, couleur_voulue, mon_id)   # On trouve d'abord où est notre tour (le départ)
                r_dep, c_dep = position_depart     # On récupère les coordonnées de départ
                print(position_depart)
    
                # On génère les coups
                coup = get_legal_moves(plateau, couleur_voulue, mon_id)
        
                if not coup:
                    reponse = {"response": "giveup"}
                else:
                    r_arr, c_arr = meilleur_coup(plateau, mon_id, couleur_voulue)   # Pour l'instant on choisit au hasard, plus tard ce sera le meilleur coup du Negamax
    
                    move = [
                        [r_dep, c_dep], 
                        [r_arr, c_arr]
                    ]  #notre move dans le bon format
                    print(move)
                    # reponse = {"response": "move", "move": move}
                    #envoyer move au serveur
    
                    envoyer_coup(client, move)
