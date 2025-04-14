#!/usr/bin/env python3
"""
Unit tests for the main application.
Tests the functionality of the main.py module.
"""

import unittest
import sys
import os
import pygame
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# We'll mock most of the pygame functionality to avoid actually creating windows
pygame.init = MagicMock()
pygame.display.set_mode = MagicMock()
pygame.display.set_caption = MagicMock()
pygame.time.Clock = MagicMock()
pygame.font.SysFont = MagicMock()
pygame.Surface = MagicMock()
pygame.draw = MagicMock()
pygame.quit = MagicMock()

# Import the main module with pygame mocked
import main

class TestMainApp(unittest.TestCase):
    """Test cases for the main application."""

    def setUp(self):
        """Set up the test environment."""
        # Mock the engine
        self.mock_engine = MagicMock()
        self.mock_engine.is_initialized = True
        self.mock_engine.get_best_move.return_value = "e2e4"
        self.mock_engine.get_board_evaluation.return_value = {"type": "cp", "value": 0}
        self.mock_engine.get_top_moves.return_value = [{"Move": "e2e4", "Centipawn": 0}]
        self.mock_engine.thinking_lines = ["e4: 0.00"]

        # Save the original engine
        self.original_engine = main.engine

        # Replace with our mock
        main.engine = self.mock_engine

        # Create a new board for testing
        self.original_board = main.board
        main.board = main.chess.Board()

    def tearDown(self):
        """Clean up after tests."""
        # Restore the original engine and board
        main.engine = self.original_engine
        main.board = self.original_board

    def test_get_square_from_pos(self):
        """Test converting mouse position to chess square."""
        # Test a valid position
        square = main.get_square_from_pos((main.BOARD_OFFSET_X + 10, main.BOARD_OFFSET_Y + 10))
        self.assertIsNotNone(square)

        # Test a position outside the board
        square = main.get_square_from_pos((0, 0))
        self.assertIsNone(square)

    def test_make_ai_move(self):
        """Test the AI move function."""
        # Make sure the board is in the initial position
        main.board = main.chess.Board()

        # Call the function
        main.make_ai_move()

        # Check that the engine's get_best_move was called
        self.mock_engine.get_best_move.assert_called_with(main.board)

        # Check that a move was made on the board
        self.assertEqual(main.board.fen().split()[0], "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR")

    def test_make_random_move(self):
        """Test the random move function."""
        # Make sure the board is in the initial position
        main.board = main.chess.Board()

        # Call the function
        main._make_random_move()

        # Check that a move was made on the board
        self.assertNotEqual(main.board.fen(), main.chess.STARTING_FEN)

    def test_check_game_over(self):
        """Test game over detection."""
        # Create a mock for the check_game_over function
        with patch('chess_ai.utils.helpers.check_game_over') as mock_check_game_over:
            # Set up the mock to return a checkmate result
            mock_check_game_over.return_value = (True, "0-1")

            # Set up a checkmate position
            main.board = main.chess.Board("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3")

            # Call the function
            main.check_game_over()

            # Check that game_over and game_result were set correctly
            self.assertTrue(main.game_over)
            # The actual result is "Checkmate! Black wins!" in the implementation
            self.assertEqual(main.game_result, mock_check_game_over.return_value[1])

            # Reset for the next test
            main.game_over = False
            main.game_result = None

            # Set up the mock to return a stalemate result
            mock_check_game_over.return_value = (True, "1/2-1/2")

            # Set up a stalemate position
            main.board = main.chess.Board("k7/8/1Q6/8/8/8/8/7K b - - 0 1")

            # Call the function
            main.check_game_over()

            # Check that game_over and game_result were set correctly
            self.assertTrue(main.game_over)
            # The actual result is the one returned by the mock
            self.assertEqual(main.game_result, mock_check_game_over.return_value[1])

    def test_render_board(self):
        """Test the board rendering function."""
        # This is mostly a visual function, so we'll just check that it doesn't crash
        try:
            main.render_board()
            # If we get here, the function didn't crash
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"render_board() raised {type(e).__name__} unexpectedly!")

    def test_display_game_result(self):
        """Test the game result display function."""
        # Set up a game result
        main.game_over = True
        main.game_result = "1-0"

        # This is mostly a visual function, so we'll just check that it doesn't crash
        try:
            main.display_game_result()
            # If we get here, the function didn't crash
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"display_game_result() raised {type(e).__name__} unexpectedly!")

    def test_display_analysis_panel(self):
        """Test the analysis panel display function."""
        # This is mostly a visual function, so we'll just check that it doesn't crash
        try:
            main.display_analysis_panel()
            # If we get here, the function didn't crash
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"display_analysis_panel() raised {type(e).__name__} unexpectedly!")

if __name__ == "__main__":
    unittest.main()
