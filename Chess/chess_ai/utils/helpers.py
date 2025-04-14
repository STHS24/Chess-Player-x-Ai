"""
Helper Functions Module
This module contains utility functions used across the application.
"""

import os
import chess
import random

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def make_random_move(board):
    """
    Make a random legal move as a fallback.

    Args:
        board: A chess.Board object representing the current position.

    Returns:
        The move that was made, or None if no legal moves.
    """
    legal_moves = list(board.legal_moves)
    if legal_moves:
        random_move = random.choice(legal_moves)
        print(f"Making random move: {board.san(random_move)}")
        board.push(random_move)
        return random_move
    return None

def check_game_over(board):
    """
    Check if the game is over and return the result.

    Args:
        board: A chess.Board object representing the current position.

    Returns:
        A tuple (is_game_over, result) where:
        - is_game_over is a boolean indicating if the game is over
        - result is a string representing the result ('1-0', '0-1', '1/2-1/2', or None)
    """
    # First check if the game is over according to python-chess
    if board.is_game_over():
        if board.is_checkmate():
            # If it's checkmate, the side that just moved won
            result = "0-1" if board.turn == chess.WHITE else "1-0"
        elif board.is_stalemate():
            result = "1/2-1/2"  # Stalemate is a draw
        elif board.is_insufficient_material():
            result = "1/2-1/2"  # Insufficient material is a draw
        elif board.can_claim_fifty_moves():
            result = "1/2-1/2"  # Fifty-move rule is a draw
        elif board.can_claim_threefold_repetition():
            result = "1/2-1/2"  # Threefold repetition is a draw
        else:
            result = "1/2-1/2"  # Default to draw for other game-over conditions
        return True, result

    # If not game over according to python-chess, check additional conditions
    # that might be considered game over in our application
    return False, None

def get_square_from_pos(pos, board_offset_x, board_offset_y, board_size):
    """
    Convert mouse position to chess square.

    Args:
        pos: A tuple (x, y) representing the mouse position.
        board_offset_x: The x offset of the board.
        board_offset_y: The y offset of the board.
        board_size: The size of the board in pixels.

    Returns:
        A chess.Square representing the square at the given position, or None if outside the board.
    """
    x, y = pos
    if (x < board_offset_x or x > board_offset_x + board_size or
        y < board_offset_y or y > board_offset_y + board_size):
        return None

    file_idx = int((x - board_offset_x) / (board_size / 8))
    rank_idx = 7 - int((y - board_offset_y) / (board_size / 8))

    return chess.square(file_idx, rank_idx)
