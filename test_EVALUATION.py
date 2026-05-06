import pytest 
from EVALUATION import get_legal_moves, check_win, find_tower_position, meilleur_coup, unmake_move, simulation_move, envoyer_coup
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

# def test_ia_evite_donner_victoire():
#     board = create_empty_board()

#     couleurs = ["ORANGE", "BLUE", "PURPLE", "PINK", "YELLOW", "RED", "GREEN", "BROWN"]
    
#     # On remplit la ligne de départ du joueur 0 (bas) et du joueur 1 (haut)
#     for i in range(8):
#         # Joueur 1 (Haut, ligne 0)
#         board[0][i] = (couleurs[i], [couleurs[i], "light"])
#         # Joueur 0 (Bas, ligne 7)
#         board[7][i] = (couleurs[i], [couleurs[i], "dark"])

#     board[7][4] = ("RED", ["RED", "dark"])# Notre tour (Joueur 0, DARK) est en (7,4)
#     board[6][0] = ("ORANGE", ["BLUE", "light"]) #tour de l'adversaire

#     coup_choisi = meilleur_coup(board, 0, "RED")
#     assert coup_choisi is not None

#     assert coup_choisi is not None
#     r, c = coup_choisi
#     assert board[r][c][0] != "ORANGE"


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

#tester nos fonction reseau

def test_envoyer_coup_format():
    # 1. On crée un faux client (mock)
    mock_client = MagicMock()
    move = [[7, 4], [5, 4]]
    
    # 2. On appelle ta fonction avec ce faux client
    envoyer_coup(mock_client, move)
    
    # 3. On vérifie que la méthode .send() a été appelée
    assert mock_client.send.called
    
    # 4. On récupère les données envoyées pour les inspecter
    # call_args[0][0] récupère le premier argument du premier appel de .send()
    donnees_envoyees = mock_client.send.call_args[0][0]
    
    # On vérifie le header (4 octets, entier 'I')
    header = donnees_envoyees[:4]
    taille = struct.unpack("I", header)[0]
    
    # On vérifie le contenu JSON
    corps_json = json.loads(donnees_envoyees[4:].decode("utf-8"))
    
    assert corps_json["response"] == "move"
    assert corps_json["move"] == move
    assert taille == len(donnees_envoyees[4:])