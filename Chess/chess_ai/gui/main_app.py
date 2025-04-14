"""
Main GUI Application Module
This module contains the main GUI application for the chess game.
"""

import pygame
import chess
import sys
import time

from chess_ai.config.settings import (
    WIDTH, HEIGHT, BOARD_SIZE, BOARD_OFFSET_X, BOARD_OFFSET_Y,
    FPS, BACKGROUND_COLOR, ANALYSIS_PANEL_HEIGHT, SHOW_ANALYSIS
)
from chess_ai.engine.sunfish_wrapper import SunfishWrapper, EngineInitializationError
from chess_ai.engine.fallback_engine import FallbackEngine
from chess_ai.gui.board_renderer import BoardRenderer
from chess_ai.gui.analysis_panel import AnalysisPanel
from chess_ai.utils.helpers import get_square_from_pos, check_game_over, make_random_move

class ChessApp:
    """Main chess application class."""

    def __init__(self):
        """Initialize the chess application."""
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT + ANALYSIS_PANEL_HEIGHT if SHOW_ANALYSIS else 0))
        pygame.display.set_caption("Chess AI")
        self.clock = pygame.time.Clock()

        # Initialize the chess board
        self.board = chess.Board()

        # Initialize the renderers
        self.board_renderer = BoardRenderer(self.screen)
        self.analysis_panel = AnalysisPanel(self.screen)

        # Game state variables
        self.selected_square = None
        self.player_color = chess.WHITE  # Player plays as white by default
        self.game_over = False
        self.game_result = None

        # Move history for undo/redo functionality
        self.move_history = []  # List of moves made
        self.current_move_index = -1  # Index of the current move in history
        self.redone_moves = []  # List of moves that were undone and can be redone

        # Performance optimization variables
        self.needs_redraw = True  # Flag to indicate if the screen needs to be redrawn
        self.last_board_state = None  # Store the last board state to detect changes
        self.frame_count = 0  # Count frames for limiting updates

        # Initialize the engine
        self.initialize_engine()

    def initialize_engine(self, max_attempts=3):
        """
        Initialize the chess engine with retry logic.

        Args:
            max_attempts: Maximum number of initialization attempts
        """
        try:
            for attempt in range(max_attempts):
                try:
                    print(f"Attempting to initialize chess engine (attempt {attempt+1}/{max_attempts})")
                    self.engine = SunfishWrapper()
                    # Set medium difficulty
                    self.engine.set_difficulty(10)
                    print("Successfully initialized chess engine!")
                    break
                except Exception as e:
                    print(f"Engine initialization attempt {attempt+1} failed: {e}")
                    if attempt == max_attempts - 1:
                        raise RuntimeError(f"All {max_attempts} initialization attempts failed")
                    # Wait a bit before retrying
                    time.sleep(0.5)

            # If we get here without an engine, something went wrong
            if not hasattr(self, 'engine') or not self.engine.is_initialized:
                raise RuntimeError("Failed to initialize engine for unknown reason")

        except Exception as e:
            print(f"Error initializing chess engine: {e}")
            print("Falling back to random-move engine")
            # Use the fallback engine that makes random moves
            self.engine = FallbackEngine()

    def make_ai_move(self):
        """Make a move with the chess engine, handling any errors gracefully."""
        if not self.board.is_game_over():
            try:
                if self.engine.is_initialized:
                    # This will also populate the thinking lines and evaluation
                    ai_move = self.engine.get_best_move(self.board)
                    if ai_move:
                        # Print engine's thinking to console
                        print("\nEngine analysis:")
                        for line in self.engine.thinking_lines:
                            print(f"  {line}")
                        if self.engine.last_evaluation:
                            eval_type = self.engine.last_evaluation['type']
                            value = self.engine.last_evaluation['value']
                            if eval_type == 'cp':
                                print(f"  Overall evaluation: {value/100:.2f} pawns")
                            else:  # mate
                                print(f"  Overall evaluation: Mate in {value}")
                        print(f"  Best move: {ai_move}\n")

                        # Make the move
                        self.board.push_uci(ai_move)
                    else:
                        # If no move was returned, make a random move
                        make_random_move(self.board)
                else:
                    # If engine is not available, make a random legal move
                    make_random_move(self.board)
            except Exception as e:
                # Handle any errors during AI move generation
                print(f"Error during AI move generation: {e}")
                make_random_move(self.board)

    def check_game_over(self):
        """Check if the game is over and update game state."""
        is_over, result = check_game_over(self.board)
        if is_over:
            self.game_over = True
            self.game_result = result

            # Record game result for learning if enabled
            try:
                # Convert result to learning format (1.0 for white win, 0.5 for draw, 0.0 for black win)
                if result == "White wins":
                    learn_result = 1.0
                elif result == "Black wins":
                    learn_result = 0.0
                else:  # Draw
                    learn_result = 0.5

                # Record the result for learning system
                if hasattr(self.engine, 'record_game_result') and hasattr(self.engine, 'use_learning') and self.engine.use_learning:
                    self.engine.record_game_result(learn_result)
                    print(f"Game result recorded for learning: {learn_result}")

                    # Learn from the game
                    if hasattr(self.engine, 'learn_from_game'):
                        self.engine.learn_from_game()
                        print("Learning completed from game data")

                # Record the result for opening repertoire
                if hasattr(self.engine, 'record_game_result') and hasattr(self.engine, 'use_opening_book') and self.engine.use_opening_book:
                    self.engine.record_game_result(learn_result)
                    print(f"Game result recorded for opening repertoire: {learn_result}")
            except Exception as e:
                print(f"Error recording game result: {e}")

    def reset_game(self):
        """Reset the game to the initial state."""
        self.board = chess.Board()
        self.selected_square = None
        self.game_over = False
        self.game_result = None

        # Reset move history
        self.move_history = []
        self.current_move_index = -1
        self.redone_moves = []

        # Reset the engine's game state if it has a reset method
        if hasattr(self.engine, 'reset_game'):
            self.engine.reset_game()

        # If player is black, make AI move first
        if self.player_color == chess.BLACK:
            self.make_ai_move()

    def undo_move(self):
        """Undo the last move."""
        if self.game_over:
            # Can't undo moves if the game is over
            return False

        # Need to undo both player and AI moves to maintain turn order
        moves_to_undo = 2

        # If it's the player's turn, we only need to undo one move if only one move has been made
        if self.board.turn == self.player_color and len(self.board.move_stack) == 1:
            moves_to_undo = 1

        # Check if we have enough moves to undo
        if len(self.board.move_stack) < moves_to_undo:
            return False

        # Undo the moves
        for _ in range(moves_to_undo):
            if self.board.move_stack:
                # Add the move to redone_moves for potential redo
                move = self.board.pop()
                self.redone_moves.append(move)
                print(f"Undoing move: {move.uci()}")

        self.needs_redraw = True
        return True

    def redo_move(self):
        """Redo a previously undone move."""
        if self.game_over or not self.redone_moves:
            # Can't redo moves if the game is over or no moves to redo
            return False

        # Need to redo both player and AI moves to maintain turn order
        moves_to_redo = 2

        # If it's the AI's turn, we only need to redo one move if only one move is available
        if self.board.turn != self.player_color and len(self.redone_moves) == 1:
            moves_to_redo = 1

        # Check if we have enough moves to redo
        if len(self.redone_moves) < moves_to_redo:
            moves_to_redo = len(self.redone_moves)

        # Redo the moves
        for _ in range(moves_to_redo):
            if self.redone_moves:
                move = self.redone_moves.pop()
                self.board.push(move)
                print(f"Redoing move: {move.uci()}")

        self.needs_redraw = True
        return True

    def switch_sides(self):
        """Switch the player's side."""
        self.player_color = not self.player_color
        self.reset_game()

    def run(self):
        """Run the main game loop."""
        # If player is black, make AI move first
        if self.player_color == chess.BLACK:
            self.make_ai_move()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Set redraw flag for any user interaction
                self.needs_redraw = True

                if not self.game_over and self.board.turn == self.player_color:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        square = get_square_from_pos(pos, BOARD_OFFSET_X, BOARD_OFFSET_Y, BOARD_SIZE)

                        if square is not None:
                            if self.selected_square is None:
                                # Select the square if it has a piece of the player's color
                                piece = self.board.piece_at(square)
                                if piece and piece.color == self.player_color:
                                    self.selected_square = square
                            else:
                                # Try to make a move
                                move = chess.Move(self.selected_square, square)

                                # Check for promotion
                                if (self.board.piece_at(self.selected_square) and
                                    self.board.piece_at(self.selected_square).piece_type == chess.PAWN and
                                    ((square >= 56 and self.player_color == chess.WHITE) or
                                     (square <= 7 and self.player_color == chess.BLACK))):
                                    move.promotion = chess.QUEEN  # Always promote to queen for simplicity

                                # If the move is legal, make it
                                if move in self.board.legal_moves:
                                    # Clear any redone moves when a new move is made
                                    if self.redone_moves:
                                        self.redone_moves = []

                                    # Make the move
                                    self.board.push(move)
                                    self.selected_square = None

                                    # Check if the game is over
                                    self.check_game_over()

                                    # If the game is not over, make the AI move
                                    if not self.game_over:
                                        self.make_ai_move()
                                        # Check if the game is over after AI move
                                        self.check_game_over()
                                else:
                                    # If the move is not legal, deselect the square
                                    self.selected_square = None

                # Handle keyboard events
                if event.type == pygame.KEYDOWN:
                    # Reset game with 'r' key
                    if event.key == pygame.K_r:
                        self.reset_game()

                    # Switch sides with 's' key
                    elif event.key == pygame.K_s:
                        self.switch_sides()

                    # Adjust difficulty with number keys 1-9
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
                                      pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                        level = int(event.key) - pygame.K_0
                        self.engine.set_difficulty(level * 2)  # Scale 1-9 to 2-18
                        print(f"Difficulty set to {level}")

                    # Toggle analysis panel with 'a' key
                    elif event.key == pygame.K_a:
                        global SHOW_ANALYSIS
                        SHOW_ANALYSIS = not SHOW_ANALYSIS
                        # Resize the window
                        self.screen = pygame.display.set_mode((WIDTH, HEIGHT + ANALYSIS_PANEL_HEIGHT if SHOW_ANALYSIS else HEIGHT))
                        print(f"Analysis panel {'shown' if SHOW_ANALYSIS else 'hidden'}")

                    # Toggle opening book with 'b' key
                    elif event.key == pygame.K_b:
                        if hasattr(self.engine, 'set_opening_book'):
                            # Toggle the opening book
                            new_state = not self.engine.use_opening_book
                            self.engine.set_opening_book(new_state)
                            print(f"Opening book {'enabled' if new_state else 'disabled'}")
                        else:
                            print("Opening book not supported by this engine")

                    # Toggle transposition table with 'c' key
                    elif event.key == pygame.K_c:
                        if hasattr(self.engine, 'set_transposition_table'):
                            # Toggle the transposition table
                            new_state = not self.engine.use_transposition_table
                            self.engine.set_transposition_table(new_state)
                            print(f"Position cache {'enabled' if new_state else 'disabled'}")

                            # Show cache stats if enabled
                            if new_state and self.engine.transposition_table:
                                stats = self.engine.transposition_table.get_stats()
                                print(f"Cache size: {stats['max_size']} positions")
                        else:
                            print("Position caching not supported by this engine")

                    # Toggle alpha-beta search with 's' key
                    elif event.key == pygame.K_s:
                        if hasattr(self.engine, 'set_alpha_beta'):
                            # Toggle the alpha-beta search
                            new_state = not self.engine.use_alpha_beta
                            self.engine.set_alpha_beta(new_state)
                            print(f"Alpha-beta search {'enabled' if new_state else 'disabled'}")

                            # Show search info if enabled
                            if new_state and self.engine.search_algorithm:
                                print(f"Search depth: {self.engine.search_algorithm.max_depth}")
                        else:
                            print("Alpha-beta search not supported by this engine")

                    # Toggle quiescence search with 'q' key
                    elif event.key == pygame.K_q:
                        if hasattr(self.engine, 'set_quiescence'):
                            # Toggle the quiescence search
                            new_state = not self.engine.use_quiescence
                            self.engine.set_quiescence(new_state)
                            print(f"Quiescence search {'enabled' if new_state else 'disabled'}")

                            # Show quiescence info if enabled
                            if new_state and self.engine.search_algorithm:
                                print(f"Quiescence depth: {self.engine.search_algorithm.quiescence_depth}")
                        else:
                            print("Quiescence search not supported by this engine")

                    # Toggle null-move pruning with 'n' key
                    elif event.key == pygame.K_n:
                        if hasattr(self.engine, 'set_null_move'):
                            # Toggle the null-move pruning
                            new_state = not self.engine.use_null_move
                            self.engine.set_null_move(new_state)
                            print(f"Null-move pruning {'enabled' if new_state else 'disabled'}")

                            # Show null-move info if enabled
                            if new_state and self.engine.search_algorithm:
                                print(f"Reduction factor: {self.engine.search_algorithm.null_move_reduction}")
                        else:
                            print("Null-move pruning not supported by this engine")

                    # Toggle learning system with 'l' key
                    elif event.key == pygame.K_l:
                        if hasattr(self.engine, 'set_learning'):
                            # Toggle the learning system
                            new_state = not self.engine.use_learning
                            self.engine.set_learning(new_state)
                            print(f"Learning system {'enabled' if new_state else 'disabled'}")

                            # Show learning info if enabled
                            if new_state and hasattr(self.engine, 'get_learning_stats'):
                                try:
                                    stats = self.engine.get_learning_stats()
                                    print(f"Positions stored: {stats['positions_stored']}, Games learned: {stats['games_learned']}")
                                except Exception as e:
                                    print(f"Error getting learning stats: {e}")
                        else:
                            print("Learning system not supported by this engine")

                    # Toggle positional evaluation with 'p' key
                    elif event.key == pygame.K_p:
                        if hasattr(self.engine, 'set_positional_eval'):
                            # Toggle the positional evaluation
                            new_state = not self.engine.use_positional_eval
                            self.engine.set_positional_eval(new_state)
                            print(f"Advanced positional evaluation {'enabled' if new_state else 'disabled'}")

                            if not new_state:
                                print("Using simple material counting")
                            else:
                                print("Using pawn structure, king safety, and mobility analysis")
                        else:
                            print("Positional evaluation not supported by this engine")

                    # Set opening style with number keys
                    elif event.key == pygame.K_1 and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        if hasattr(self.engine, 'set_opening_style'):
                            self.engine.set_opening_style('solid')
                        else:
                            print("Opening styles not supported by this engine")
                    elif event.key == pygame.K_2 and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        if hasattr(self.engine, 'set_opening_style'):
                            self.engine.set_opening_style('aggressive')
                        else:
                            print("Opening styles not supported by this engine")
                    elif event.key == pygame.K_3 and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        if hasattr(self.engine, 'set_opening_style'):
                            self.engine.set_opening_style('tricky')
                        else:
                            print("Opening styles not supported by this engine")
                    elif event.key == pygame.K_4 and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        if hasattr(self.engine, 'set_opening_style'):
                            self.engine.set_opening_style('balanced')
                        else:
                            print("Opening styles not supported by this engine")

                    # Show opening stats with 'o' key
                    elif event.key == pygame.K_o:
                        if hasattr(self.engine, 'get_opening_stats'):
                            stats = self.engine.get_opening_stats()
                            print("Opening Repertoire Statistics:")
                            print(f"Total positions: {stats.get('total_positions', 0)}")
                            print(f"Total games: {stats.get('total_games', 0)}")
                            print(f"Success rate: {stats.get('success_rate', 0.0):.2f}")
                            print(f"Current style: {stats.get('style', 'balanced')}")
                        else:
                            print("Opening statistics not supported by this engine")

                    # Undo move with 'z' key or left arrow
                    elif event.key in [pygame.K_z, pygame.K_LEFT]:
                        if not self.game_over:
                            if self.undo_move():
                                print("Move undone")
                            else:
                                print("Cannot undo any further")

                    # Redo move with 'y' key or right arrow
                    elif event.key in [pygame.K_y, pygame.K_RIGHT]:
                        if not self.game_over:
                            if self.redo_move():
                                print("Move redone")
                            else:
                                print("Cannot redo any further")

            # Check if we need to redraw the screen
            current_board_state = self.board.fen()
            board_changed = (current_board_state != self.last_board_state)

            # Set redraw flag if board changed or it's a key frame
            if board_changed or self.needs_redraw or self.frame_count % 5 == 0:  # Only update every 5 frames if nothing changed
                self.needs_redraw = True
                self.last_board_state = current_board_state

            # Render only if needed
            if self.needs_redraw:
                # Fill the screen with the background color
                self.screen.fill(BACKGROUND_COLOR)

                # Render the board
                self.board_renderer.render_board(self.board, self.selected_square)
                self.board_renderer.render_coordinates()

                # Display game result if game is over
                if self.game_over:
                    self.board_renderer.render_game_result(self.game_result)

                # Display analysis panel
                if SHOW_ANALYSIS:
                    self.analysis_panel.render(self.board, self.engine)

                # Update the display
                pygame.display.flip()

                # Reset the redraw flag
                self.needs_redraw = False

            # Increment frame counter
            self.frame_count = (self.frame_count + 1) % 60  # Reset every second at 60 FPS

            # Cap the frame rate
            self.clock.tick(FPS)

        # Clean up engine resources
        if hasattr(self, 'engine') and self.engine.is_initialized:
            self.engine.cleanup()

        pygame.quit()
        sys.exit()

def main():
    """Main function to run the chess application."""
    app = ChessApp()
    app.run()

if __name__ == "__main__":
    main()
