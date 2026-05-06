import pytest 
from EVALUATION import get_legal_moves, check_win, find_tower_position, meilleur_coup
from EVALUATION import unmake_move, simulation_move, envoyer_coup, evaluate, negamax, state, envoyé, recevoir
import struct
import json
from unittest.mock import MagicMock

def create_empty_board():
    return [[("WHITE", None) for _ in range(8)] for _ in range(8)]


#test nos legal move
def test_move_straight_line():  #verifie ligne droite
    board = create_empty_board()
    board[7][4] = ("RED", ["RED", "dark"]) # On place une tour DARK (joueur 0) en (7, 4)

    moves = get_legal_moves(board, "RED", 0)

    assert (6, 4) in moves
    assert (0, 4) in moves
    assert (7, 3) not in moves

def test_move_blocked_by_piece(): #verfie que ca s'arrete quand y a un obstacle
    board = create_empty_board()
    board[7][4] = ("RED", ["RED", "dark"]) # Tour à tester en (7, 4)
    board[5][4] = ("BLUE", ["BLUE", "light"])   # Obstacle juste devant en (5, 4)
    
    moves = get_legal_moves(board, "RED", 0)
    
    assert (6, 4) in moves      # Case libre avant l'obstacle
    assert (5, 4) not in moves  # Ne peut pas prendre la place de l'obstacle
    assert (4, 4) not in moves  # Ne peut pas sauter par-dessus l'obstacle

def test_direction_player_1(): #verifie que ca va bien en diagonale
    board = create_empty_board()
    # Tour LIGHT (joueur 1) en (0, 4)
    board[0][4] = ("GREEN", ["GREEN", "light"])
    
    moves = get_legal_moves(board, "GREEN", 1)
    
    assert (1, 4) in moves
    assert (1, 3) in moves 
    assert (1, 5) in moves 


#test find tower position
def test_find_tower():
    board = create_empty_board()
    board[7][0] = ("YELLOW", ["RED", "dark"]) #Joueur 0 (dark) : une tour rouge en (7, 0)

    board[0][7] = ("GREEN", ["RED", "light"]) #jouaur 1 (light), tour red en (0,7)

    pos_red_0 = find_tower_position(board, "RED", 0)
    assert pos_red_0 == (7, 0) #verifie la position de la tour du joueur 0

    pos_red_1 = find_tower_position(board, "RED", 1)
    assert pos_red_1 == (0, 7) #verifie la position de la tour du joueur 1

    pos_none = find_tower_position(board, "ORANGE", 0)
    assert pos_none is None #verifie qu'il ne trouve pas une tour qu'il doit pas jouer

#test notre check win
def test_checkwin():
    board = create_empty_board()

    board[0][3] = ("RED", ["RED", "dark"])
    assert check_win(0, board) is True
    # Le joueur 1 n'a pas gagné pour autant
    assert check_win(1, board) is False

    board_2 = create_empty_board()
    board_2[0][5] = ("BLUE", ["BLUE", "light"]) #pion du joueur 1
    assert check_win(0, board_2) is False #Un pion adverse ne doit pas donner la victoire


#test notre ia

def test_victoire_immediate():
    board = create_empty_board()
    board[1][4] = ("RED", ["RED", "dark"])
    coup_choisi = meilleur_coup(board, 0, "RED")
    coups_gagnants = [(0, 4), (0, 3), (0, 5)]
    assert coup_choisi in coups_gagnants


def test_unmakemove():
    board = create_empty_board()
    pion_original = ["RED", "dark"]
    board[7][4] = ("RED", pion_original)
    
    # On simule un mouvement vers (6,4)
    r_dep, c_dep, ancienne_case, piece = simulation_move(board, 0, "RED", 6, 4)
    
    # On annule le mouvement
    unmake_move(board, r_dep, c_dep, 6, 4, ancienne_case, piece)

    assert board[7][4][1] == pion_original
    assert board[6][4][1] is None #"La case d'arrivée n'a pas été vidée après unmake_move !"

def test_evaluate_mobilite():
    # Plateau 1 : Tour très libre
    board_libre = create_empty_board()
    board_libre[4][4] = ("RED", ["RED", "dark"])
    
    # Plateau 2 : Tour bloquée
    board_bloque = create_empty_board()
    board_bloque[4][4] = ("RED", ["RED", "dark"])
    board_bloque[3][4] = ("BLUE", ["BLUE", "light"]) # Bloque le haut
    
    score_libre = evaluate(board_libre, 0, "RED")
    score_bloque = evaluate(board_bloque, 0, "RED")
    
    print(score_libre, ">", score_bloque)
    assert score_libre > score_bloque #Une tour libre doit valoir plus qu'une tour bloquée 

def test_evaluate_mobilite_adversaire():
    # Situation 1 : L'adversaire est TOTALEMENT LIBRE
    board_libre = create_empty_board()
    board_libre[7][4] = ("RED", ["RED", "dark"])   # Ma tour (Joueur 0)
    board_libre[0][4] = ("RED", ["RED", "light"])  # Tour adverse (Joueur 1) de la MEME COULEUR que celle évaluée
    score_libre = evaluate(board_libre, 0, "RED")
    
    # Situation 2 : L'adversaire est BLOQUÉ
    board_bloque = create_empty_board()
    board_bloque[7][4] = ("RED", ["RED", "dark"])
    board_bloque[0][4] = ("RED", ["RED", "light"])
    board_bloque[1][4] = ("BLUE", ["BLUE", "dark"]) # On met un obstacle juste devant la tour adverse (ligne 1)
    score_bloque = evaluate(board_bloque, 0, "RED")
    
    assert score_bloque > score_libre

def test_negamax_anticipation(): #On crée une situation où le joueur 0 va perdre au tour suivant SAUF s'il fait un mouvement précis maintenant.
    board = create_empty_board()
    # Ma tour RED est proche de la fin
    board[1][4] = ("RED", ["RED", "dark"])
    
    # Si l'IA regarde à profondeur 1 ou plus, elle doit voir 
    # que le score d'un mouvement vers la ligne 0 est maximal (+1.0)
    score = negamax(board, 1, 0, "RED", float('-inf'), float('inf'))
    
    assert score > 0.5 # L'IA a vu une situation très favorable

#tester nos fonction reseau

def test_envoyer_coup_format():
    mock_client = MagicMock()     # On crée un faux client (mock)
    move = [[7, 4], [5, 4]]
    envoyer_coup(mock_client, move)  # On appelle la fonction avec le faux client
    assert mock_client.send.called  # On vérifie que la méthode .send() a été appelée
    
    donnees_envoyees = mock_client.send.call_args[0][0]
    header = donnees_envoyees[:4]
    taille = struct.unpack("I", header)[0]
    corps_json = json.loads(donnees_envoyees[4:].decode("utf-8"))
    
    assert corps_json["response"] == "move"
    assert corps_json["move"] == move
    assert taille == len(donnees_envoyees[4:])

def test_recevoir_commande_play():
    mock_socket = MagicMock()
    reponse_serveur = {"request": "play", "color": "RED", "board": []}
    message_utf8 = json.dumps(reponse_serveur).encode("utf-8")
    header = struct.pack("I", len(message_utf8))
    
    mock_socket.recv.side_effect = [header, message_utf8]
    resultat = state(mock_socket)
    
    assert resultat["request"] == "play"
    assert resultat["color"] == "RED"


def test_envoye_subscription():
    mock_client = MagicMock()
    mock_client.send.side_effect = lambda x: len(x)
    taille_retournee, taille_totale = envoyé(mock_client)

    assert mock_client.send.called
    assert taille_retournee == taille_totale
    
    sent_data = mock_client.send.call_args[0][0]
    header = sent_data[:4]
    body = json.loads(sent_data[4:].decode("utf-8"))
    
    assert body["name"] == "Pauline et Cindy"
    assert struct.unpack("I", header)[0] == len(sent_data) - 4

def test_recevoir_success():
    mock_client = MagicMock()
    data_serveur = {"response": "ok", "message": "Abonnement réussi"}
    msg_json = json.dumps(data_serveur).encode("utf-8")
    header = struct.pack("I", len(msg_json))
    
    mock_client.recv.side_effect = [header, msg_json]
    
    recevoir(mock_client, 100, 100)
    
    with open("eval.json", "r") as f:
        contenu = json.load(f)
        assert contenu["response"] == "ok"

def test_recevoir_erreur():
    mock_client = MagicMock()
    
    # On simule un header vide (0 octets) ou une réponse qui force l'échec
    header_vide = struct.pack("I", 0)
    mock_client.recv.side_effect = [header_vide, b""]
    
    recevoir(mock_client, 100, 1)
    
    # On vérifie que le fichier contient bien l'erreur
    with open("eval.json", "r") as f:
        contenu = json.load(f)
        assert contenu["response"] == "error"
        assert "error" in contenu


def test_find_tower_position_color_none():
    # Plateau vide
    board = [[(None, None) for _ in range(8)] for _ in range(8)]
    
    # Place une tour dark à la position (2, 3)
    # Structure : case[1] = (couleur, type_joueur)
    board[2][3] = ("case_info", ("RED", "dark"))
    
    # Appel avec None pour la couleur
    result = find_tower_position(board, None, 0)
    
    assert result == (2, 3)       