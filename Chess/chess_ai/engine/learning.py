"""
Learning Module
This module provides machine learning capabilities for the chess engine.
"""

import os
import json
import time
import random
import chess
from collections import defaultdict

class LearningSystem:
    """
    Class implementing a simple learning system for the chess engine.
    Stores position evaluations and outcomes to improve future play.
    """
    
    def __init__(self, data_file=None, learning_rate=0.1, max_positions=10000):
        """
        Initialize the learning system.
        
        Args:
            data_file: Path to the data file (None for default)
            learning_rate: Rate at which to adjust evaluations (0.0-1.0)
            max_positions: Maximum number of positions to store
        """
        self.data_file = data_file or os.path.join(os.path.dirname(__file__), '..', 'data', 'learning_data.json')
        self.learning_rate = learning_rate
        self.max_positions = max_positions
        
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        # Position database: maps FEN (simplified) -> {evaluation, count, result_sum}
        self.position_data = {}
        
        # Game history for the current session
        self.game_positions = []
        self.game_result = None
        
        # Statistics
        self.positions_learned = 0
        self.games_learned = 0
        self.cache_hits = 0
        
        # Load existing data if available
        self.load_data()
    
    def load_data(self):
        """Load learning data from file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.position_data = data.get('positions', {})
                    self.positions_learned = data.get('stats', {}).get('positions_learned', 0)
                    self.games_learned = data.get('stats', {}).get('games_learned', 0)
                    print(f"Loaded learning data: {len(self.position_data)} positions from {self.games_learned} games")
            else:
                print("No learning data found, starting fresh")
        except Exception as e:
            print(f"Error loading learning data: {e}")
            # Start with empty data if loading fails
            self.position_data = {}
    
    def save_data(self):
        """Save learning data to file."""
        try:
            # Trim the database if it's too large
            if len(self.position_data) > self.max_positions:
                # Keep positions with higher counts
                sorted_positions = sorted(
                    self.position_data.items(), 
                    key=lambda x: x[1]['count'], 
                    reverse=True
                )
                self.position_data = dict(sorted_positions[:self.max_positions])
            
            # Prepare data for saving
            data = {
                'positions': self.position_data,
                'stats': {
                    'positions_learned': self.positions_learned,
                    'games_learned': self.games_learned,
                    'last_update': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
            # Save to file
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            print(f"Saved learning data: {len(self.position_data)} positions from {self.games_learned} games")
        except Exception as e:
            print(f"Error saving learning data: {e}")
    
    def simplify_fen(self, fen):
        """
        Simplify a FEN string to focus on piece positions only.
        This helps generalize positions and reduce storage needs.
        
        Args:
            fen: A chess.Board FEN string
            
        Returns:
            A simplified FEN string
        """
        # Just keep the piece positions part of the FEN
        return fen.split(' ')[0]
    
    def record_position(self, board, evaluation):
        """
        Record a position and its evaluation during a game.
        
        Args:
            board: A chess.Board object
            evaluation: The evaluation score for the position
        """
        # Simplify the FEN to focus on piece positions
        simple_fen = self.simplify_fen(board.fen())
        
        # Store the position and evaluation for later learning
        self.game_positions.append({
            'fen': simple_fen,
            'eval': evaluation,
            'move_number': board.fullmove_number,
            'side_to_move': 'w' if board.turn == chess.WHITE else 'b'
        })
    
    def record_game_result(self, result):
        """
        Record the result of a game.
        
        Args:
            result: The game result (1.0 for white win, 0.5 for draw, 0.0 for black win)
        """
        self.game_result = result
    
    def learn_from_game(self):
        """
        Learn from the recorded game positions and result.
        Updates the position database based on the game outcome.
        """
        if self.game_result is None or not self.game_positions:
            print("No game data to learn from")
            return
        
        # Update position data based on game result
        for pos_data in self.game_positions:
            fen = pos_data['fen']
            eval_score = pos_data['eval']
            side_to_move = pos_data['side_to_move']
            
            # Adjust the result based on side to move
            # If black is to move, invert the result
            position_result = self.game_result
            if side_to_move == 'b':
                position_result = 1.0 - position_result
            
            # Initialize position data if not seen before
            if fen not in self.position_data:
                self.position_data[fen] = {
                    'eval': eval_score,
                    'count': 0,
                    'result_sum': 0.0
                }
            
            # Update position data
            self.position_data[fen]['count'] += 1
            self.position_data[fen]['result_sum'] += position_result
            
            # Adjust evaluation based on actual result vs expected result
            expected_result = self._eval_to_expected_result(eval_score)
            adjustment = self.learning_rate * (position_result - expected_result)
            self.position_data[fen]['eval'] += adjustment
            
            self.positions_learned += 1
        
        # Update statistics
        self.games_learned += 1
        
        # Clear game data for next game
        self.game_positions = []
        self.game_result = None
        
        # Save updated data
        self.save_data()
    
    def get_learned_evaluation(self, board):
        """
        Get the learned evaluation for a position if available.
        
        Args:
            board: A chess.Board object
            
        Returns:
            A tuple (has_data, evaluation) where has_data is a boolean
            indicating if we have data for this position
        """
        simple_fen = self.simplify_fen(board.fen())
        
        if simple_fen in self.position_data:
            self.cache_hits += 1
            data = self.position_data[simple_fen]
            
            # Calculate win rate for this position
            win_rate = data['result_sum'] / data['count'] if data['count'] > 0 else 0.5
            
            # Blend stored evaluation with win rate
            confidence = min(1.0, data['count'] / 10.0)  # Confidence increases with more samples
            blended_eval = (1 - confidence) * data['eval'] + confidence * self._win_rate_to_eval(win_rate)
            
            # Adjust for side to move
            if not board.turn == chess.WHITE:
                blended_eval = -blended_eval
                
            return True, blended_eval
        
        return False, 0.0
    
    def adjust_evaluation(self, board, base_eval):
        """
        Adjust an evaluation based on learning data.
        
        Args:
            board: A chess.Board object
            base_eval: The base evaluation from the engine
            
        Returns:
            An adjusted evaluation score
        """
        has_data, learned_eval = self.get_learned_evaluation(board)
        
        if has_data:
            # Blend the base evaluation with the learned evaluation
            # Weight depends on how many times we've seen this position
            simple_fen = self.simplify_fen(board.fen())
            count = self.position_data[simple_fen]['count']
            
            # Calculate weight based on count (max 0.5)
            weight = min(0.5, count / 20.0)
            
            # Blend evaluations
            return (1 - weight) * base_eval + weight * learned_eval
        
        return base_eval
    
    def _eval_to_expected_result(self, eval_score):
        """
        Convert an evaluation score to an expected result.
        Uses a sigmoid function to map scores to [0, 1].
        
        Args:
            eval_score: The evaluation score
            
        Returns:
            The expected result (0.0-1.0)
        """
        # Sigmoid function to convert eval to win probability
        # Scale factor of 1/4 means +4.0 is ~98% win chance
        return 1.0 / (1.0 + 10 ** (-eval_score / 4.0))
    
    def _win_rate_to_eval(self, win_rate):
        """
        Convert a win rate to an evaluation score.
        Inverse of _eval_to_expected_result.
        
        Args:
            win_rate: The win rate (0.0-1.0)
            
        Returns:
            The corresponding evaluation score
        """
        # Avoid division by zero
        win_rate = max(0.001, min(0.999, win_rate))
        
        # Inverse sigmoid
        return 4.0 * math.log10(win_rate / (1.0 - win_rate))
    
    def get_stats(self):
        """
        Get statistics about the learning system.
        
        Returns:
            A dictionary with learning statistics
        """
        return {
            'positions_stored': len(self.position_data),
            'positions_learned': self.positions_learned,
            'games_learned': self.games_learned,
            'cache_hits': self.cache_hits,
            'learning_rate': self.learning_rate,
            'max_positions': self.max_positions
        }
    
    def clear_data(self):
        """Clear all learning data."""
        self.position_data = {}
        self.positions_learned = 0
        self.games_learned = 0
        self.cache_hits = 0
        self.save_data()
        print("Learning data cleared")

# Add missing import
import math
