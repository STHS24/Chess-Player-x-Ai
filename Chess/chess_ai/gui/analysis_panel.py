"""
Analysis Panel Module
This module handles rendering the analysis panel.
"""

import pygame
import chess
from chess_ai.config.settings import (
    WIDTH, HEIGHT, ANALYSIS_PANEL_HEIGHT, ANALYSIS_PANEL_COLOR, ANALYSIS_TEXT_COLOR
)

class AnalysisPanel:
    """Class for rendering the analysis panel."""

    def __init__(self, screen):
        """
        Initialize the analysis panel.

        Args:
            screen: The pygame screen to render on.
        """
        self.screen = screen
        self.font = pygame.font.SysFont("Courier New", 14)
        self.info_font = pygame.font.SysFont("Arial", 12)

        # Cache for rendered text and surfaces
        self.text_cache = {}
        self.surface_cache = {}

        # Cache the panel background
        self._create_panel_background()

        # Last evaluation data for caching
        self.last_eval_data = None
        self.last_eval_text = None
        self.last_eval_color = None

    def _create_panel_background(self):
        """
        Create and cache the panel background surface.
        """
        # Create the panel background
        panel = pygame.Surface((WIDTH, ANALYSIS_PANEL_HEIGHT), pygame.SRCALPHA)
        panel.fill(ANALYSIS_PANEL_COLOR)
        self.surface_cache['panel_bg'] = panel

        # Create the evaluation bar background
        bar_height = 80
        bar_width = 20
        bar_bg = pygame.Surface((bar_width, bar_height))
        bar_bg.fill((50, 50, 50))  # Dark gray
        self.surface_cache['bar_bg'] = bar_bg

    def _get_cached_text(self, text, color, font):
        """
        Get cached text surface or create and cache a new one.

        Args:
            text: The text to render
            color: The color to render the text in
            font: The font to use

        Returns:
            A rendered text surface
        """
        cache_key = f"{text}_{color[0]}_{color[1]}_{color[2]}_{id(font)}"
        if cache_key not in self.text_cache:
            self.text_cache[cache_key] = font.render(text, True, color)
        return self.text_cache[cache_key]

    def render(self, board, engine):
        """
        Render the analysis panel.

        Args:
            board: A chess.Board object representing the current position.
            engine: The chess engine object.
        """
        try:
            # Draw the analysis panel background from cache
            self.screen.blit(self.surface_cache['panel_bg'], (0, HEIGHT))

            # Draw the evaluation
            eval_data = engine.get_board_evaluation(board)
            if eval_data:
                eval_type = eval_data.get('type')
                value = eval_data.get('value', 0)

                # Check if evaluation has changed
                eval_changed = (self.last_eval_data != eval_data)

                if eval_type == 'cp':
                    # Convert centipawns to pawns
                    pawns = value / 100.0
                    # Flip the sign if it's black's turn
                    if board.turn == chess.BLACK:
                        pawns = -pawns

                    # Format the evaluation string
                    if pawns > 0:
                        eval_str = f"+{pawns:.2f}"
                        eval_color = (50, 200, 50)  # Green for positive eval
                    elif pawns < 0:
                        eval_str = f"{pawns:.2f}"
                        eval_color = (200, 50, 50)  # Red for negative eval
                    else:
                        eval_str = "0.00"
                        eval_color = (200, 200, 200)  # White for neutral eval

                    # Use cached text if evaluation hasn't changed
                    if eval_changed or self.last_eval_text is None:
                        self.last_eval_text = self._get_cached_text(eval_str, eval_color, self.font)
                        self.last_eval_color = eval_color
                        self.last_eval_data = eval_data.copy()

                    # Draw the evaluation
                    self.screen.blit(self.last_eval_text, (10, HEIGHT + 10))

                    # Draw the evaluation bar
                    bar_height = 80
                    bar_width = 20
                    bar_x = 50
                    bar_y = HEIGHT + (ANALYSIS_PANEL_HEIGHT - bar_height) // 2

                    # Draw the background
                    pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

                    # Calculate the bar fill based on evaluation
                    # Clamp the evaluation between -5 and 5 pawns
                    clamped_eval = max(-5, min(5, pawns))
                    # Map from [-5, 5] to [0, 1]
                    normalized_eval = (clamped_eval + 5) / 10
                    # Calculate the height of the white portion
                    white_height = int(bar_height * normalized_eval)
                    black_height = bar_height - white_height

                    # Draw the white and black portions
                    pygame.draw.rect(self.screen, (200, 200, 200), (bar_x, bar_y + black_height, bar_width, white_height))
                    pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, black_height))

                elif eval_type == 'mate':
                    # Format the mate evaluation string
                    if value > 0:
                        eval_str = f"Mate in {value}"
                        eval_color = (50, 200, 50)  # Green for checkmate
                    else:
                        eval_str = f"Mate in {-value}"
                        eval_color = (200, 50, 50)  # Red for getting checkmated

                    # Draw the evaluation
                    eval_text = self.font.render(eval_str, True, eval_color)
                    self.screen.blit(eval_text, (10, HEIGHT + 10))

            # Draw the thinking lines
            if hasattr(engine, 'thinking_lines'):
                y_offset = 30
                for i, line in enumerate(engine.thinking_lines[:3]):
                    line_text = self.font.render(line, True, ANALYSIS_TEXT_COLOR)
                    self.screen.blit(line_text, (80, HEIGHT + y_offset + i * 20))

            # Draw current position information
            position_info = f"Move: {1 + board.fullmove_number//2}{'.' if board.turn == chess.WHITE else '...'}"
            position_surface = self.info_font.render(position_info, True, ANALYSIS_TEXT_COLOR)
            self.screen.blit(position_surface, (WIDTH - 120, HEIGHT + 8))

            # Draw whose turn it is
            turn_info = "White to move" if board.turn == chess.WHITE else "Black to move"
            turn_surface = self.info_font.render(turn_info, True, ANALYSIS_TEXT_COLOR)
            self.screen.blit(turn_surface, (WIDTH - 120, HEIGHT + 28))

            # Draw game state information
            if board.is_check():
                state_info = "CHECK!"
                state_color = (200, 50, 50)  # Red for check
            elif board.is_stalemate():
                state_info = "Stalemate"
                state_color = (200, 200, 50)  # Yellow for stalemate
            elif board.is_insufficient_material():
                state_info = "Draw (insufficient material)"
                state_color = (200, 200, 50)  # Yellow for draw
            elif board.can_claim_fifty_moves():
                state_info = "Draw (50-move rule)"
                state_color = (200, 200, 50)  # Yellow for draw
            elif board.can_claim_threefold_repetition():
                state_info = "Draw (repetition)"
                state_color = (200, 200, 50)  # Yellow for draw
            else:
                state_info = ""
                state_color = ANALYSIS_TEXT_COLOR

            if state_info:
                state_surface = self.info_font.render(state_info, True, state_color)
                self.screen.blit(state_surface, (WIDTH - 120, HEIGHT + 48))

        except Exception as e:
            # If there's a critical error in the analysis panel, log it but don't crash
            print(f"Error displaying analysis panel: {e}")
            error_text = self.info_font.render("Error displaying analysis", True, (200, 50, 50))
            self.screen.blit(error_text, (10, HEIGHT + 10))
