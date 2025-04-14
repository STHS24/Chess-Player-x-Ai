"""
Fallback Engine Module
This module provides a simple fallback engine that makes random moves when the main engine fails.
"""

import chess
import random

class FallbackEngine:
    """A simple fallback engine that makes random moves when the main engine fails."""
    
    def __init__(self):
        """Initialize the fallback engine."""
        self.is_initialized = True
        self.thinking_lines = []
        self.last_evaluation = {"type": "cp", "value": 0}
        print("Initialized fallback random-move engine")

    def get_best_move(self, board):
        """
        Make a random legal move.
        
        Args:
            board: A chess.Board object representing the current position.
            
        Returns:
            A string representing a random move in UCI notation, or None if no legal moves.
        """
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        move = random.choice(legal_moves)
        self.thinking_lines = [f"{board.san(move)}: 0.00 (random)"]
        return move.uci()

    def set_difficulty(self, level):
        """
        Difficulty doesn't affect random moves.
        
        Args:
            level: An integer from 1 to 20 (ignored in fallback engine).
        """
        print(f"Fallback engine: difficulty setting has no effect")

    def get_board_evaluation(self, board):
        """
        Return a neutral evaluation.
        
        Args:
            board: A chess.Board object representing the current position.
            
        Returns:
            A dictionary with a neutral evaluation.
        """
        return {"type": "cp", "value": 0}

    def get_top_moves(self, board, num_moves=3):
        """
        Return random top moves.
        
        Args:
            board: A chess.Board object representing the current position.
            num_moves: The number of top moves to return.
            
        Returns:
            A list of dictionaries containing random moves.
        """
        result = []
        legal_moves = list(board.legal_moves)
        moves_to_return = min(num_moves, len(legal_moves))
        if moves_to_return > 0:
            selected_moves = random.sample(legal_moves, moves_to_return)
            for move in selected_moves:
                result.append({"Move": move.uci(), "Centipawn": 0})
        return result

    def cleanup(self):
        """Nothing to clean up."""
        pass
