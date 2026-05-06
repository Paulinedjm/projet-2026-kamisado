import pytest 
from EVALUATION import get_legal_moves, check_win, find_tower_position

def create_empty_board():
    return [[("WHITE", None) for _ in range(8)] for _ in range(8)]

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
    assert (1, 3) in moves # diagonale
    assert (1, 5) in moves # diagonale
