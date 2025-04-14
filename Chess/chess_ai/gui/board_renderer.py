"""
Board Renderer Module
This module handles rendering the chess board and pieces.
"""

import pygame
import chess
from chess_ai.config.settings import (
    WIDTH, HEIGHT, BOARD_SIZE, BOARD_OFFSET_X, BOARD_OFFSET_Y,
    DARK_SQUARE, LIGHT_SQUARE, HIGHLIGHT_COLOR
)

class BoardRenderer:
    """Class for rendering the chess board and pieces."""

    def __init__(self, screen):
        """
        Initialize the board renderer.

        Args:
            screen: The pygame screen to render on.
        """
        self.screen = screen
        self.piece_images = {}
        self._load_piece_images()

        # Cache for board squares and highlights
        self.square_surfaces = {}
        self.highlight_surface = None

        # Pre-calculate square surfaces for better performance
        self._initialize_square_surfaces()

    def _load_piece_images(self):
        """Load chess piece images."""
        piece_types = ['p', 'n', 'b', 'r', 'q', 'k']
        colors = ['b', 'w']

        # Try to load piece images from the assets directory
        try:
            for piece in piece_types:
                for color in colors:
                    piece_key = piece.upper() if color == 'w' else piece
                    image_path = f"assets/pieces/{color}{piece}.png"
                    try:
                        self.piece_images[piece_key] = pygame.image.load(image_path)
                        # Scale the image to fit the board
                        square_size = BOARD_SIZE // 8
                        self.piece_images[piece_key] = pygame.transform.scale(
                            self.piece_images[piece_key],
                            (square_size, square_size)
                        )
                    except pygame.error:
                        print(f"Warning: Could not load piece image {image_path}")
        except Exception as e:
            print(f"Error loading piece images: {e}")
            print("Using text-based pieces instead")
            self.piece_images = {}

    def _initialize_square_surfaces(self):
        """
        Pre-calculate and cache the square surfaces for better performance.
        """
        square_size = BOARD_SIZE // 8

        # Create surfaces for light and dark squares
        light_square = pygame.Surface((square_size, square_size))
        light_square.fill(LIGHT_SQUARE)
        dark_square = pygame.Surface((square_size, square_size))
        dark_square.fill(DARK_SQUARE)

        # Cache the surfaces
        self.square_surfaces['light'] = light_square
        self.square_surfaces['dark'] = dark_square

        # Create highlight surface
        highlight = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
        highlight.fill(HIGHLIGHT_COLOR)
        self.highlight_surface = highlight

    def render_board(self, board, selected_square=None):
        """
        Render the chess board and pieces.

        Args:
            board: A chess.Board object representing the current position.
            selected_square: The currently selected square, if any.
        """
        square_size = BOARD_SIZE // 8

        # Pre-calculate legal moves for the selected square (if any)
        legal_moves_from_selected = set()
        if selected_square is not None:
            legal_moves_from_selected = {move.to_square for move in board.legal_moves
                                       if move.from_square == selected_square}

        # Draw the board with cached surfaces
        for row in range(8):
            for col in range(8):
                # Determine square color
                is_light = (row + col) % 2 == 0
                square_type = 'light' if is_light else 'dark'

                # Get position
                x = BOARD_OFFSET_X + col * square_size
                y = BOARD_OFFSET_Y + row * square_size

                # Draw the square from cache
                self.screen.blit(self.square_surfaces[square_type], (x, y))

                # Get chess square
                square = chess.square(col, 7 - row)

                # Highlight selected square
                if selected_square is not None and square == selected_square:
                    self.screen.blit(self.highlight_surface, (x, y))

                # Highlight legal moves from selected square
                elif square in legal_moves_from_selected:
                    self.screen.blit(self.highlight_surface, (x, y))

        # Draw the pieces
        for row in range(8):
            for col in range(8):
                square = chess.square(col, 7 - row)
                piece = board.piece_at(square)
                if piece:
                    piece_symbol = piece.symbol()
                    x = BOARD_OFFSET_X + col * square_size
                    y = BOARD_OFFSET_Y + row * square_size

                    if piece_symbol in self.piece_images:
                        # Draw the piece image
                        self.screen.blit(self.piece_images[piece_symbol], (x, y))
                    else:
                        # Draw a text representation as fallback
                        font = pygame.font.SysFont("Arial", square_size // 2)
                        text = font.render(piece_symbol, True, (255, 255, 255) if piece_symbol.islower() else (0, 0, 0))
                        text_rect = text.get_rect(center=(x + square_size // 2, y + square_size // 2))
                        self.screen.blit(text, text_rect)

    def render_coordinates(self):
        """Render board coordinates (files and ranks)."""
        font = pygame.font.SysFont("Arial", 14)
        square_size = BOARD_SIZE // 8

        # Draw file coordinates (a-h)
        for col in range(8):
            file_label = chr(ord('a') + col)
            text = font.render(file_label, True, (200, 200, 200))
            self.screen.blit(
                text,
                (
                    BOARD_OFFSET_X + col * square_size + square_size // 2 - text.get_width() // 2,
                    BOARD_OFFSET_Y + BOARD_SIZE + 5
                )
            )

        # Draw rank coordinates (1-8)
        for row in range(8):
            rank_label = str(8 - row)
            text = font.render(rank_label, True, (200, 200, 200))
            self.screen.blit(
                text,
                (
                    BOARD_OFFSET_X - 15,
                    BOARD_OFFSET_Y + row * square_size + square_size // 2 - text.get_height() // 2
                )
            )

    def render_game_result(self, result):
        """
        Render the game result overlay.

        Args:
            result: A string representing the game result ('1-0', '0-1', '1/2-1/2').
        """
        if not result:
            return

        # Create a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with 70% opacity
        self.screen.blit(overlay, (0, 0))

        # Render the result text
        font = pygame.font.SysFont("Arial", 48, bold=True)
        if result == "1-0":
            text = font.render("White wins!", True, (255, 255, 255))
        elif result == "0-1":
            text = font.render("Black wins!", True, (255, 255, 255))
        else:  # 1/2-1/2
            text = font.render("Draw!", True, (255, 255, 255))

        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        self.screen.blit(text, text_rect)

        # Render instructions to restart
        font_small = pygame.font.SysFont("Arial", 24)
        restart_text = font_small.render("Press 'R' to restart", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
        self.screen.blit(restart_text, restart_rect)
