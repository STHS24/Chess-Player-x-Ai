#!/usr/bin/env python3
"""
Unit tests for the chess engine wrapper.
Tests the core functionality of the SunfishWrapper class.
"""

import unittest
import chess
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sunfish_wrapper import SunfishWrapper, EngineInitializationError

class TestSunfishWrapper(unittest.TestCase):
    """Test cases for the SunfishWrapper class."""
    
    def setUp(self):
        """Set up the test environment."""
        try:
            self.engine = SunfishWrapper(max_retries=3)
        except EngineInitializationError:
            self.skipTest("Engine initialization failed, skipping tests")
    
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'engine') and self.engine.is_initialized:
            self.engine.cleanup()
    
    def test_initialization(self):
        """Test that the engine initializes correctly."""
        self.assertTrue(self.engine.is_initialized)
        self.assertEqual(self.engine.skill_level, 10)  # Default skill level
    
    def test_set_difficulty(self):
        """Test setting difficulty levels."""
        # Test valid difficulty levels
        self.engine.set_difficulty(1)
        self.assertEqual(self.engine.skill_level, 1)
        
        self.engine.set_difficulty(20)
        self.assertEqual(self.engine.skill_level, 20)
        
        # Test clamping of out-of-range values
        self.engine.set_difficulty(0)
        self.assertEqual(self.engine.skill_level, 1)
        
        self.engine.set_difficulty(25)
        self.assertEqual(self.engine.skill_level, 20)
    
    def test_get_best_move(self):
        """Test that the engine returns a valid move."""
        board = chess.Board()
        move = self.engine.get_best_move(board)
        
        # Check that a move is returned
        self.assertIsNotNone(move)
        
        # Check that the move is valid
        move_obj = chess.Move.from_uci(move)
        self.assertIn(move_obj, board.legal_moves)
    
    def test_get_best_move_empty_board(self):
        """Test behavior with an empty board."""
        board = chess.Board.empty()
        move = self.engine.get_best_move(board)
        
        # Should return None for an empty board with no legal moves
        self.assertIsNone(move)
    
    def test_get_board_evaluation(self):
        """Test board evaluation."""
        board = chess.Board()
        eval_data = self.engine.get_board_evaluation(board)
        
        # Check that evaluation data is returned
        self.assertIsNotNone(eval_data)
        
        # Check that it has the expected format
        self.assertIn('type', eval_data)
        self.assertIn('value', eval_data)
        
        # Type should be either 'cp' (centipawns) or 'mate'
        self.assertIn(eval_data['type'], ['cp', 'mate'])
    
    def test_get_top_moves(self):
        """Test getting top moves."""
        board = chess.Board()
        top_moves = self.engine.get_top_moves(board, num_moves=3)
        
        # Check that moves are returned
        self.assertTrue(len(top_moves) > 0)
        
        # Check that each move is valid
        for move_data in top_moves:
            self.assertIn('Move', move_data)
            move_obj = chess.Move.from_uci(move_data['Move'])
            self.assertIn(move_obj, board.legal_moves)
    
    def test_thinking_lines(self):
        """Test that thinking lines are generated."""
        board = chess.Board()
        self.engine.get_best_move(board)
        
        # Check that thinking lines are generated
        self.assertTrue(len(self.engine.thinking_lines) > 0)
    
    def test_different_positions(self):
        """Test engine behavior with different positions."""
        # Test a middle game position
        fen = "r1bqkbnr/ppp2ppp/2np4/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 4"
        board = chess.Board(fen)
        move = self.engine.get_best_move(board)
        
        # Check that a move is returned
        self.assertIsNotNone(move)
        
        # Check that the move is valid
        move_obj = chess.Move.from_uci(move)
        self.assertIn(move_obj, board.legal_moves)
    
    def test_checkmate_position(self):
        """Test engine behavior with a checkmate position."""
        # Scholar's mate position
        fen = "rnbqkbnr/pppp1ppp/8/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR b KQkq - 0 3"
        board = chess.Board(fen)
        
        # Make the losing move
        board.push_uci("b8c6")
        
        # Queen delivers checkmate
        board.push_uci("f3f7")
        
        # Board should be in checkmate
        self.assertTrue(board.is_checkmate())
        
        # Engine should return None for a checkmate position
        move = self.engine.get_best_move(board)
        self.assertIsNone(move)
    
    def test_stalemate_position(self):
        """Test engine behavior with a stalemate position."""
        # A simple stalemate position
        fen = "k7/8/1Q6/8/8/8/8/7K b - - 0 1"
        board = chess.Board(fen)
        
        # Board should be in stalemate
        self.assertTrue(board.is_stalemate())
        
        # Engine should return None for a stalemate position
        move = self.engine.get_best_move(board)
        self.assertIsNone(move)

if __name__ == "__main__":
    unittest.main()
