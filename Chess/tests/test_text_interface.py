#!/usr/bin/env python3
"""
Unit tests for the text-based chess interface.
Tests the functionality of the text_chess.py module.
"""

import unittest
import sys
import os
import io
import chess
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the text_chess module
# Note: We're using a try-except block because we'll be mocking most of the functionality
try:
    import text_chess
except ImportError:
    # Create a mock module if the real one can't be imported
    text_chess = MagicMock()

class TestTextInterface(unittest.TestCase):
    """Test cases for the text-based chess interface."""
    
    def setUp(self):
        """Set up the test environment."""
        self.board = chess.Board()
    
    def test_get_user_move_uci(self):
        """Test parsing UCI format moves."""
        # Test valid UCI move
        with patch('builtins.input', return_value='e2e4'):
            move = text_chess.get_user_move(self.board)
            self.assertIsInstance(move, chess.Move)
            self.assertEqual(move.uci(), 'e2e4')
        
        # Test invalid UCI move
        with patch('builtins.input', return_value='e2e9'):
            with patch('builtins.print') as mock_print:
                move = text_chess.get_user_move(self.board)
                mock_print.assert_called_with(
                    text_chess.Colors.RED + 
                    "Invalid move. Try again or type 'help' for commands." + 
                    text_chess.Colors.RESET
                )
    
    def test_get_user_move_san(self):
        """Test parsing algebraic notation moves."""
        # Test valid SAN move
        with patch('builtins.input', return_value='e4'):
            move = text_chess.get_user_move(self.board)
            self.assertIsInstance(move, chess.Move)
            self.assertEqual(move.uci(), 'e2e4')
        
        # Test invalid SAN move
        with patch('builtins.input', return_value='e9'):
            with patch('builtins.print') as mock_print:
                move = text_chess.get_user_move(self.board)
                mock_print.assert_called_with(
                    text_chess.Colors.RED + 
                    "Invalid move. Try again or type 'help' for commands." + 
                    text_chess.Colors.RESET
                )
    
    def test_get_user_move_commands(self):
        """Test command handling in get_user_move."""
        # Test 'help' command
        with patch('builtins.input', return_value='help'):
            move = text_chess.get_user_move(self.board)
            self.assertEqual(move, 'help')
        
        # Test 'quit' command
        with patch('builtins.input', return_value='quit'):
            move = text_chess.get_user_move(self.board)
            self.assertEqual(move, 'quit')
        
        # Test 'board' command
        with patch('builtins.input', return_value='board'):
            move = text_chess.get_user_move(self.board)
            self.assertEqual(move, 'board')
        
        # Test 'resign' command
        with patch('builtins.input', return_value='resign'):
            move = text_chess.get_user_move(self.board)
            self.assertEqual(move, 'resign')
        
        # Test 'new' command
        with patch('builtins.input', return_value='new'):
            move = text_chess.get_user_move(self.board)
            self.assertEqual(move, 'new')
        
        # Test 'flip' command
        with patch('builtins.input', return_value='flip'):
            move = text_chess.get_user_move(self.board)
            self.assertEqual(move, 'flip')
        
        # Test 'level' command
        with patch('builtins.input', return_value='level 5'):
            move = text_chess.get_user_move(self.board)
            self.assertEqual(move, 'level 5')
        
        # Test 'hint' command
        with patch('builtins.input', return_value='hint'):
            move = text_chess.get_user_move(self.board)
            self.assertEqual(move, 'hint')
        
        # Test 'eval' command
        with patch('builtins.input', return_value='eval'):
            move = text_chess.get_user_move(self.board)
            self.assertEqual(move, 'eval')
    
    def test_print_board(self):
        """Test board printing functionality."""
        # Redirect stdout to capture the output
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # Mock the clear_screen function to do nothing
        with patch('text_chess.clear_screen'):
            # Print the board
            text_chess.print_board(self.board)
            
            # Check that the output contains expected elements
            output = captured_output.getvalue()
            self.assertIn('a b c d e f g h', output)
            self.assertIn('│', output)  # Board border character
            
            # Check that all pieces are represented
            for piece in ['♙', '♘', '♗', '♖', '♕', '♔', '♟', '♞', '♝', '♜', '♛', '♚']:
                self.assertIn(piece, output)
        
        # Reset stdout
        sys.stdout = sys.__stdout__
    
    def test_print_game_status(self):
        """Test game status printing."""
        # Test checkmate status
        checkmate_fen = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"
        checkmate_board = chess.Board(checkmate_fen)
        
        with patch('builtins.print') as mock_print:
            text_chess.print_game_status(checkmate_board)
            mock_print.assert_called_with(
                text_chess.Colors.BOLD + 
                text_chess.Colors.YELLOW + 
                "Checkmate! Black wins." + 
                text_chess.Colors.RESET
            )
        
        # Test stalemate status
        stalemate_fen = "k7/8/1Q6/8/8/8/8/7K b - - 0 1"
        stalemate_board = chess.Board(stalemate_fen)
        
        with patch('builtins.print') as mock_print:
            text_chess.print_game_status(stalemate_board)
            mock_print.assert_called_with(
                text_chess.Colors.BOLD + 
                text_chess.Colors.YELLOW + 
                "Stalemate! The game is a draw." + 
                text_chess.Colors.RESET
            )
        
        # Test check status
        check_fen = "rnbqkbnr/ppp2ppp/8/3pp3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 3"
        check_board = chess.Board(check_fen)
        check_board.push_uci("d8h4")
        
        with patch('builtins.print') as mock_print:
            text_chess.print_game_status(check_board)
            mock_print.assert_called_with(
                text_chess.Colors.BOLD + 
                text_chess.Colors.RED + 
                "Check!" + 
                text_chess.Colors.RESET
            )

if __name__ == "__main__":
    unittest.main()
