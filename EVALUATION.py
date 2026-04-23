import socket 
import struct 
import random
import json
import threading

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
    #recevoir 
    data= client.recv(taille_response)
    #On décode et on transforme en dictionnaire
    response = json.loads(data.decode("utf-8"))

    #écrire dans le fichier json eval l'état de la board, le joueur qui doit jouer, et le pion à jouer
    with open("eval.json", "w") as f:
        json.dump(response, f, indent=4)
    
    return response

def envoyer_coup(client, move):
    reponse = {
        "response": "move",
        "move": move
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
        while 0 <= r < 8 and 0 <= c < 8 and state[r][c] == None:
            moves.append((r, c)) # On ajoute la coordonnée comme coup possible
            
            # On continue d'avancer dans cette direction (comme une tour d'échecs)
            r += direction
            c += dc
            
    return moves



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
                plateau = message["state"]["board"]
                couleur_voulue = message["state"]["color"]
                mon_id = message["state"]["current"]
    
                position_depart = find_tower_position(plateau, couleur_voulue, mon_id)   # On trouve d'abord où est notre tour (le départ)
                r_dep, c_dep = position_depart     # On récupère les coordonnées de départ
    
    
    
                # On génère les coups
                coup = get_legal_moves(plateau, couleur_voulue, mon_id)
        
                if not coup:
                    reponse = {"response": "giveup"}
                else:
                    r_arr, c_arr = random.choice(coup)    # Pour l'instant on choisit au hasard, plus tard ce sera le meilleur coup du Negamax
    
                    move = [
                        [r_dep, c_dep], 
                        [r_arr, c_arr]
                    ]  #notre move dans le bon format
                    print(move)
                    reponse = {"response": "move", "move": move}
                    #envoyer move au serveur
    
                    envoyer_coup(client, move)
