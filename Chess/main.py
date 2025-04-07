"""
Chess AI Bot using Sunfish
This program creates a chess game where you can play against the Sunfish chess engine.
"""

import pygame
import chess
import os
import sys
from sunfish_wrapper import SunfishWrapper

# Constants
WIDTH, HEIGHT = 600, 600  # Reduced from 800x800
BOARD_SIZE = 550  # Reduced from 700
BOARD_OFFSET_X = (WIDTH - BOARD_SIZE) // 2
BOARD_OFFSET_Y = (HEIGHT - BOARD_SIZE) // 2
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_SQUARE = (50, 50, 50)  # Dark gray (almost black) for dark squares
LIGHT_SQUARE = (150, 150, 150)  # Light gray for light squares
BACKGROUND_COLOR = (100, 100, 100)  # Medium gray for background
HIGHLIGHT_COLOR = (124, 252, 0, 128)  # Light green with some transparency

# Analysis panel constants
ANALYSIS_PANEL_HEIGHT = 120  # Reduced from 150
ANALYSIS_PANEL_COLOR = (30, 30, 30, 200)  # Dark gray with transparency
ANALYSIS_TEXT_COLOR = (220, 220, 220)  # Light gray text
SHOW_ANALYSIS = True  # Toggle analysis panel

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT + ANALYSIS_PANEL_HEIGHT if SHOW_ANALYSIS else 0))
pygame.display.set_caption("Chess AI with Sunfish - Compact")
clock = pygame.time.Clock()

# Initialize the chess board
board = chess.Board()

# Initialize Sunfish with error handling
MAX_ENGINE_INIT_ATTEMPTS = 3
engine = None

# Create a fallback engine class for when initialization fails completely
class FallbackEngine:
    """A simple fallback engine that makes random moves when the main engine fails."""
    def __init__(self):
        self.is_initialized = True
        self.thinking_lines = []
        self.last_evaluation = {"type": "cp", "value": 0}
        print("Initialized fallback random-move engine")

    def get_best_move(self, board):
        """Make a random legal move."""
        import random
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        move = random.choice(legal_moves)
        self.thinking_lines = [f"{board.san(move)}: 0.00 (random)"]
        return move.uci()

    def set_difficulty(self, level):
        """Difficulty doesn't affect random moves."""
        print(f"Fallback engine: difficulty setting has no effect")

    def get_board_evaluation(self, board):
        """Return a neutral evaluation."""
        return {"type": "cp", "value": 0}

    def get_top_moves(self, board, num_moves=3):
        """Return random top moves."""
        import random
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

# Try to initialize the main engine with multiple attempts
try:
    for attempt in range(MAX_ENGINE_INIT_ATTEMPTS):
        try:
            print(f"Attempting to initialize chess engine (attempt {attempt+1}/{MAX_ENGINE_INIT_ATTEMPTS})")
            engine = SunfishWrapper()
            # Set medium difficulty
            engine.set_difficulty(10)
            print("Successfully initialized chess engine!")
            break
        except Exception as e:
            print(f"Engine initialization attempt {attempt+1} failed: {e}")
            if attempt == MAX_ENGINE_INIT_ATTEMPTS - 1:
                raise RuntimeError(f"All {MAX_ENGINE_INIT_ATTEMPTS} initialization attempts failed")
            # Wait a bit before retrying
            import time
            time.sleep(0.5)

    # If we get here without an engine, something went wrong
    if engine is None:
        raise RuntimeError("Failed to initialize engine for unknown reason")

except Exception as e:
    print(f"Error initializing chess engine: {e}")
    print("Falling back to random-move engine")
    # Use the fallback engine that makes random moves
    engine = FallbackEngine()

# Game state variables
selected_square = None
player_color = chess.WHITE  # Player plays as white by default
game_over = False
game_result = None

def get_square_from_pos(pos):
    """Convert mouse position to chess square."""
    x, y = pos
    if (x < BOARD_OFFSET_X or x > BOARD_OFFSET_X + BOARD_SIZE or
        y < BOARD_OFFSET_Y or y > BOARD_OFFSET_Y + BOARD_SIZE):
        return None

    file_idx = int((x - BOARD_OFFSET_X) / (BOARD_SIZE / 8))
    rank_idx = 7 - int((y - BOARD_OFFSET_Y) / (BOARD_SIZE / 8))

    return chess.square(file_idx, rank_idx)

def render_board():
    """Render the chess board with pieces."""
    # Fill the background with medium gray
    screen.fill(BACKGROUND_COLOR)

    # Draw the chess board
    square_size = BOARD_SIZE // 8
    for row in range(8):
        for col in range(8):
            # Determine square color (alternating light gray and dark gray/black)
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            # Draw the square
            pygame.draw.rect(screen, color, (
                BOARD_OFFSET_X + col * square_size,
                BOARD_OFFSET_Y + row * square_size,
                square_size,
                square_size
            ))

            # Get the piece at this square
            square = chess.square(col, 7-row)  # Convert to chess.square format
            piece = board.piece_at(square)

            # Highlight selected square
            if selected_square is not None and square == selected_square:
                highlight = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
                highlight.fill((124, 252, 0, 128))  # Light green with transparency
                screen.blit(highlight, (BOARD_OFFSET_X + col * square_size, BOARD_OFFSET_Y + row * square_size))

            # Highlight last move
            if board.move_stack:
                last_move = board.peek()
                if square == last_move.from_square or square == last_move.to_square:
                    highlight = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
                    highlight.fill((135, 206, 250, 128))  # Light blue with transparency
                    screen.blit(highlight, (BOARD_OFFSET_X + col * square_size, BOARD_OFFSET_Y + row * square_size))

            # Draw the piece if there is one
            if piece:
                # Create a text representation of the piece
                piece_chars = {
                    chess.PAWN: '♙' if piece.color == chess.WHITE else '♟',
                    chess.KNIGHT: '♘' if piece.color == chess.WHITE else '♞',
                    chess.BISHOP: '♗' if piece.color == chess.WHITE else '♝',
                    chess.ROOK: '♖' if piece.color == chess.WHITE else '♜',
                    chess.QUEEN: '♕' if piece.color == chess.WHITE else '♛',
                    chess.KING: '♔' if piece.color == chess.WHITE else '♚'
                }
                piece_char = piece_chars[piece.piece_type]

                # Render the piece with improved visibility
                font = pygame.font.SysFont('segoeuisymbol', square_size - 8)  # Adjusted for smaller squares

                # Use gold color for white pieces and silver for black pieces
                piece_color = (212, 175, 55) if piece.color == chess.WHITE else (192, 192, 192)

                # Add a black outline/shadow for better contrast
                shadow_offset = 1
                shadow = font.render(piece_char, True, (0, 0, 0))
                shadow_rect = shadow.get_rect(center=(
                    BOARD_OFFSET_X + col * square_size + square_size // 2 + shadow_offset,
                    BOARD_OFFSET_Y + row * square_size + square_size // 2 + shadow_offset
                ))
                screen.blit(shadow, shadow_rect)

                # Render the actual piece
                text = font.render(piece_char, True, piece_color)
                text_rect = text.get_rect(center=(
                    BOARD_OFFSET_X + col * square_size + square_size // 2,
                    BOARD_OFFSET_Y + row * square_size + square_size // 2
                ))
                screen.blit(text, text_rect)

def make_ai_move():
    """Make a move with the chess engine, handling any errors gracefully."""
    if not board.is_game_over():
        try:
            if engine.is_initialized:
                # This will also populate the thinking lines and evaluation
                ai_move = engine.get_best_move(board)
                if ai_move:
                    # Print engine's thinking to console
                    print("\nEngine analysis:")
                    for line in engine.thinking_lines:
                        print(f"  {line}")
                    if engine.last_evaluation:
                        eval_type = engine.last_evaluation['type']
                        value = engine.last_evaluation['value']
                        if eval_type == 'cp':
                            print(f"  Overall evaluation: {value/100:.2f} pawns")
                        else:  # mate
                            print(f"  Overall evaluation: Mate in {value}")
                    print(f"  Best move: {ai_move}\n")

                    # Make the move
                    board.push_uci(ai_move)
                else:
                    # If no move was returned, make a random move
                    _make_random_move()
            else:
                # If engine is not available, make a random legal move
                _make_random_move()
        except Exception as e:
            # Handle any errors during AI move generation
            print(f"Error during AI move generation: {e}")
            _make_random_move()

def _make_random_move():
    """Make a random legal move as a fallback."""
    import random
    legal_moves = list(board.legal_moves)
    if legal_moves:
        random_move = random.choice(legal_moves)
        print(f"Making random move: {board.san(random_move)}")
        board.push(random_move)

def check_game_over():
    """Check if the game is over and determine the result."""
    global game_over, game_result

    if board.is_game_over():
        game_over = True

        if board.is_checkmate():
            winner = "Black" if board.turn == chess.WHITE else "White"
            game_result = f"Checkmate! {winner} wins!"
        elif board.is_stalemate():
            game_result = "Draw by stalemate!"
        elif board.is_insufficient_material():
            game_result = "Draw by insufficient material!"
        elif board.is_fifty_moves():
            game_result = "Draw by fifty-move rule!"
        elif board.is_repetition():
            game_result = "Draw by repetition!"
        else:
            game_result = "Game over!"

def display_game_result():
    """Display the game result on the screen."""
    if game_result:
        # Create a semi-transparent background for the text
        overlay = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with 70% opacity
        screen.blit(overlay, (0, 0))

        # Render the text with a shadow for better visibility
        font = pygame.font.SysFont('Arial', 32)

        # Shadow
        shadow = font.render(game_result, True, BLACK)
        shadow_rect = shadow.get_rect(center=(WIDTH//2 + 2, 50 + 2))
        screen.blit(shadow, shadow_rect)

        # Main text
        text = font.render(game_result, True, (255, 215, 0))  # Gold color
        text_rect = text.get_rect(center=(WIDTH//2, 50))
        screen.blit(text, text_rect)

def display_analysis_panel():
    """Display engine's analysis information with error handling."""
    if not SHOW_ANALYSIS:
        return

    try:
        if not engine or not engine.is_initialized:
            return

        # Create the analysis panel at the bottom of the screen
        panel_rect = pygame.Rect(0, HEIGHT, WIDTH, ANALYSIS_PANEL_HEIGHT)

        # Draw panel background
        panel_surface = pygame.Surface((WIDTH, ANALYSIS_PANEL_HEIGHT), pygame.SRCALPHA)
        panel_surface.fill(ANALYSIS_PANEL_COLOR)
        screen.blit(panel_surface, panel_rect)

        # Draw border line
        pygame.draw.line(screen, (50, 50, 50), (0, HEIGHT), (WIDTH, HEIGHT), 2)

        # Prepare fonts
        title_font = pygame.font.SysFont('Arial', 16, bold=True)  # Reduced from 18
        info_font = pygame.font.SysFont('Arial', 14)  # Reduced from 16

        # Draw title
        engine_name = "Chess Engine Analysis"
        title = title_font.render(engine_name, True, (255, 215, 0))  # Gold color
        screen.blit(title, (10, HEIGHT + 8))  # Adjusted position

        # Draw evaluation
        y_offset = HEIGHT + 30  # Reduced from 40
        try:
            if engine.last_evaluation:
                eval_type = engine.last_evaluation['type']
                value = engine.last_evaluation['value']

                if eval_type == 'cp':
                    eval_text = f"Evaluation: {value/100:.2f} pawns"
                    # Color based on who's winning (positive is good for white, negative for black)
                    if value > 0:
                        eval_color = (150, 255, 150) if board.turn == chess.WHITE else (255, 150, 150)  # Green/Red
                    elif value < 0:
                        eval_color = (255, 150, 150) if board.turn == chess.WHITE else (150, 255, 150)  # Red/Green
                    else:
                        eval_color = ANALYSIS_TEXT_COLOR  # Neutral
                else:  # mate
                    eval_text = f"Mate in {abs(value)}"
                    # Mate is always bad for the side to move
                    eval_color = (255, 150, 150) if value < 0 else (150, 255, 150)

                eval_surface = info_font.render(eval_text, True, eval_color)
                screen.blit(eval_surface, (20, y_offset))
        except Exception as e:
            # If there's an error getting evaluation, show a neutral message
            error_text = "Evaluation unavailable"
            error_surface = info_font.render(error_text, True, ANALYSIS_TEXT_COLOR)
            screen.blit(error_surface, (20, y_offset))

        # Draw thinking lines
        y_offset = HEIGHT + 55  # Reduced from 70
        try:
            if engine.thinking_lines:
                for i, line in enumerate(engine.thinking_lines[:3]):  # Show top 3 lines
                    line_surface = info_font.render(f"{i+1}. {line}", True, ANALYSIS_TEXT_COLOR)
                    screen.blit(line_surface, (10, y_offset + i * 20))  # Reduced spacing from 25 to 20
        except Exception as e:
            # If there's an error getting thinking lines, show a message
            error_text = "Analysis unavailable"
            error_surface = info_font.render(error_text, True, ANALYSIS_TEXT_COLOR)
            screen.blit(error_surface, (10, y_offset))

        # Draw current position information
        position_info = f"Move: {1 + board.fullmove_number//2}{'.' if board.turn == chess.WHITE else '...'}"
        position_surface = info_font.render(position_info, True, ANALYSIS_TEXT_COLOR)
        screen.blit(position_surface, (WIDTH - 120, HEIGHT + 8))  # Adjusted position
    except Exception as e:
        # If there's a critical error in the analysis panel, log it but don't crash
        print(f"Error displaying analysis panel: {e}")

def main():
    global selected_square, game_over, player_color, game_result

    # If player is black, make AI move first
    if player_color == chess.BLACK:
        make_ai_move()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not game_over and board.turn == player_color:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    square = get_square_from_pos(pos)

                    if square is not None:
                        if selected_square is None:
                            # Select the square if it has a piece of the player's color
                            piece = board.piece_at(square)
                            if piece and piece.color == player_color:
                                selected_square = square
                        else:
                            # Try to make a move
                            move = chess.Move(selected_square, square)
                            # Check for promotion
                            if (board.piece_at(selected_square).piece_type == chess.PAWN and
                                ((square >= 56 and player_color == chess.WHITE) or
                                 (square <= 7 and player_color == chess.BLACK))):
                                move.promotion = chess.QUEEN  # Always promote to queen for simplicity

                            if move in board.legal_moves:
                                board.push(move)
                                selected_square = None

                                # After player's move, let AI respond
                                if not board.is_game_over():
                                    make_ai_move()
                            else:
                                # If the move is not legal, deselect or select a new piece
                                piece = board.piece_at(square)
                                if piece and piece.color == player_color:
                                    selected_square = square
                                else:
                                    selected_square = None

            # Reset game with 'r' key
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    board.reset()
                    selected_square = None
                    game_over = False
                    game_result = None
                    if player_color == chess.BLACK:
                        make_ai_move()

                # Switch sides with 's' key
                elif event.key == pygame.K_s:
                    player_color = not player_color
                    board.reset()
                    selected_square = None
                    game_over = False
                    game_result = None
                    if player_color == chess.BLACK:
                        make_ai_move()

                # Adjust difficulty with number keys 1-9
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
                                  pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                    level = int(event.key) - pygame.K_0
                    engine.set_difficulty(level * 2)  # Scale 1-9 to 2-18
                    print(f"Difficulty set to {level}")

                # Toggle analysis panel with 'a' key
                elif event.key == pygame.K_a:
                    global SHOW_ANALYSIS, screen
                    SHOW_ANALYSIS = not SHOW_ANALYSIS
                    # Resize the window
                    screen = pygame.display.set_mode((WIDTH, HEIGHT + ANALYSIS_PANEL_HEIGHT if SHOW_ANALYSIS else HEIGHT))
                    print(f"Analysis panel {'shown' if SHOW_ANALYSIS else 'hidden'}")

        # Fill the screen with the background color
        screen.fill(BACKGROUND_COLOR)

        # Render the board
        render_board()

        # Check if the game is over
        check_game_over()

        # Display game result if game is over
        if game_over:
            display_game_result()

        # Display analysis panel
        if SHOW_ANALYSIS:
            display_analysis_panel()

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    # Clean up engine resources
    if engine and engine.is_initialized:
        engine.cleanup()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
