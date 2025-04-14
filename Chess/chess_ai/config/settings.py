"""
Settings Module
This module contains configuration settings for the chess application.
"""

# GUI settings
WIDTH = 600
HEIGHT = 600
BOARD_SIZE = 550
BOARD_OFFSET_X = (WIDTH - BOARD_SIZE) // 2
BOARD_OFFSET_Y = (HEIGHT - BOARD_SIZE) // 2
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_SQUARE = (50, 50, 50)  # Dark gray (almost black) for dark squares
LIGHT_SQUARE = (150, 150, 150)  # Light gray for light squares
BACKGROUND_COLOR = (100, 100, 100)  # Medium gray for background
HIGHLIGHT_COLOR = (124, 252, 0, 128)  # Light green with some transparency

# Analysis panel settings
ANALYSIS_PANEL_HEIGHT = 120
ANALYSIS_PANEL_COLOR = (30, 30, 30, 200)  # Dark gray with transparency
ANALYSIS_TEXT_COLOR = (220, 220, 220)  # Light gray text
SHOW_ANALYSIS = True  # Toggle analysis panel

# Engine settings
MAX_ENGINE_INIT_ATTEMPTS = 3
DEFAULT_DIFFICULTY = 10  # Medium difficulty (1-20 scale)

# CLI settings
class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    BG_GRAY = "\033[100m"
