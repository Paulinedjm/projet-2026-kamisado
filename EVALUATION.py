import socket 
import struct 
import json
import math

def envoyé(client):
    envoi= {
      "request": "subscribe",
      "port": 8888,
      "name": "Pauline et Cindy",
      "matricules": ["24343", "24160"]
    }
    #preparation du message + taille
    message_json= json.dumps(envoi).encode("utf-8")
    taille= len(message_json)
    header=struct.pack( "I", taille)
    taille_totale=client.send(header+ message_json)
    
    return taille_totale, len(header)+len(message_json)


def recevoir(client, taille_envoyé, taille_attendu):

    if taille_envoyé== taille_attendu :
        
        # lire la taille de la réponse du serveur en 4 oct
        response= client.recv(4)
        taille_response= struct.unpack("I", response)[0]
    
        data= client.recv(taille_response)
       
        response = json.loads(data.decode("utf-8"))
        
        with open("eval.json", "w") as f:
            json.dump(response, f, indent=4)
   
    else : 
        message_reçu_erreur= {
          "response": "error",
          "error": "error message"
        }
        with open("eval.json", "w") as f:
            json.dump(message_reçu_erreur, f, indent=4)
          
            


def state(client):
    #recevoir l'état du jeu venant du serveur en créant une boucle pour recevoir être sûr de recevoir tout le message
    state_all= client.recv(4)
    taille_response= struct.unpack("I", state_all)[0]
    data = b""
    while len(data) < taille_response:
        morceau = client.recv(taille_response - len(data))
        data += morceau 
    response = json.loads(data.decode("utf-8"))

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


def find_tower_position(board, color_to_find, player_id):  
    
    current_player = "dark" if player_id == 0 else "light"
    for r in range(8): 
        for c in range(8): 
            case = board[r][c]
            
            # On vérifie si la case n'est pas vide
            if case[1] is not None :
                title_color= case[1][0]
                title_kind=case[1][1]
                if title_kind==current_player:
                    if color_to_find is None:
                        return r,c
                    elif title_color==color_to_find:
            
                      return r, c 
                    
    return None 

def get_legal_moves(state, color_to_play, player_id):   
    moves = [] 
    
    pos_r, pos_c = find_tower_position(state, color_to_play, player_id)
    
    direction = -1 if player_id == 0 else 1 #determine si on doit monter ou descendre dans le board en fonction du joueur qui joue
    
    # explore les 3 directions: gauche (-1), tout droit (0), droite (+1) 
    for dc in [-1, 0, 1]:
        r, c = pos_r + direction, pos_c + dc
        
        # Tant qu'on est sur le plateau et que la case est vide
        while 0 <= r < 8 and 0 <= c < 8 and state[r][c][1] == None:
            moves.append((r, c))
            
            r += direction
            c += dc
            
    return moves


def check_win(player_id, board):
    # determine si un joueur a atteint la ligne adverse
    if player_id==0 :
        line=0 
        kind= "dark"
    else : 
        line=7 
        kind= "light"
    # determination victoire 
    for col in range(8):
        case= board[line][col]
        if case[1] is not None and case[1][1]== kind:  
            
            
            return True
                  
    return False

#Simuler un move
def simulation_move(minimax_board, player_id, color, r_arr, c_arr):   

    pos = find_tower_position(minimax_board, color, player_id)
    r_dep, c_dep = pos 

    # sauvegarde la pièce et la case d'arrivée 
    piece = minimax_board[r_dep][c_dep][1]
    case_arrivee = minimax_board[r_arr][c_arr]
    
    #Simuler le déplacement 
    minimax_board[r_arr][c_arr] = (minimax_board[r_arr][c_arr][0], piece)
    minimax_board[r_dep][c_dep] = (minimax_board[r_dep][c_dep][0], None)
    return r_dep, c_dep, case_arrivee, piece


def unmake_move(board, r_dep, c_dep, r_arr, c_arr, case_arrivee, piece_dep):
    board[r_dep][c_dep] = (board[r_dep][c_dep][0], piece_dep)
    board[r_arr][c_arr] = case_arrivee


def evaluate(minimax_board, player_id, color_to_play):
    # fonction qui évalue les scores pour choisir le meilleur coup
    opponent = 1 if player_id == 0 else 0
    score = 0

    if check_win(player_id, minimax_board): 
        return 1.0 
    if check_win(opponent, minimax_board): 
        return -1.0 

    my_goal = 0 if player_id == 0 else 7
    opponent_goal = 7 if player_id == 0 else 0

    # Heuristique de "Deadlock" (Blocage)
    if color_to_play is not None:
        direct_moves = get_legal_moves(minimax_board, color_to_play, player_id)            
        if len(direct_moves) == 0:        
                score -= 4.0  


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
    ²                my_moves = get_legal_moves(minimax_board, tower_color, player_id)
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
        return evaluate(minimax_board, player_id, color)

    coups = get_legal_moves(minimax_board, color, player_id)
    if not coups:
        return evaluate(minimax_board, player_id, color)
    
    scoreMax = float('-inf')
    
    #on teste chaque coup possible
    for r, c in coups:
        couleur_suivante = minimax_board[r][c][0]

        
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
            break 
        
    return scoreMax

def meilleur_coup(board, player_id, color):
    opps = 1 if player_id == 0 else 0 

    coups = get_legal_moves(board, color, player_id)
    if not coups:
        return None
    
    
    best_score = float('-inf')
    best_move = coups[0]

    #on test encore chaque coup possible
    for r, c in coups:
        couleur_suivante = board[r][c][0]

        pos = find_tower_position(board, color, player_id)
        piece = board[pos[0]][pos[1]][1]
        r_dep, c_dep, ancienne_arrivee, piece = simulation_move(board, player_id, color, r, c)
        
        score = -negamax(board,3, opps, couleur_suivante, float("-inf"), float("inf"))
        unmake_move(board, r_dep, c_dep, r, c, ancienne_arrivee, piece)
        

        if score > best_score:
            best_score = score
            best_move = (r, c)
    return best_move


    
if __name__ == "__main__":
    serverAddress= ("127.0.0.1", 3000)


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
    
                    position_depart = find_tower_position(plateau, couleur_voulue, mon_id)
                    r_dep, c_dep = position_depart     
                    print(position_depart)
        
                    # On génère les coups
                    coup = get_legal_moves(plateau, couleur_voulue, mon_id)
            
                    if not coup:
                        print("Aucun coup légal trouvé")
                        move = [
                            [r_dep, c_dep], 
                            [r_dep, c_dep]
                        ]
                        envoyer_coup(client, move)
                    else:
                        r_arr, c_arr = meilleur_coup(plateau, mon_id, couleur_voulue)  
        
                        move = [
                            [r_dep, c_dep], 
                            [r_arr, c_arr]
                        ]  
                        print(move)
                       
        
                        envoyer_coup(client, move)
    
    