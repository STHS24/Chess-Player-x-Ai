"""
Text Interface Module
This module provides a text-based interface for the chess application.
"""

import chess
import os
from chess_ai.config.settings import Colors
from chess_ai.utils.helpers import clear_screen

class TextInterface:
    """Class for the text-based chess interface."""

    def __init__(self):
        """Initialize the text interface."""
        pass

    def print_board(self, board, last_move=None):
        """
        Print the chess board in the terminal with colored squares.

        Args:
            board: A chess.Board object
            last_move: The last move made (to highlight)
        """
        clear_screen()

        # Unicode chess pieces
        piece_symbols = {
            'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
            'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',
            '.': ' '
        }

        # Print the board
        print("\n  " + Colors.BOLD + "  a b c d e f g h  " + Colors.RESET)
        print("  " + Colors.BOLD + "┌─────────────────┐" + Colors.RESET)

        for rank in range(7, -1, -1):
            print(Colors.BOLD + f"{rank+1} │" + Colors.RESET, end="")

            for file in range(8):
                square = chess.square(file, rank)
                piece = board.piece_at(square)

                # Determine square color
                is_dark_square = (rank + file) % 2 == 1
                bg_color = Colors.BG_GRAY if is_dark_square else Colors.BG_WHITE

                # Highlight last move
                if last_move and (square == last_move.from_square or square == last_move.to_square):
                    bg_color = Colors.BG_YELLOW

                # Get piece symbol
                if piece:
                    piece_symbol = piece_symbols[piece.symbol()]
                    fg_color = Colors.BLACK if piece.color == chess.WHITE else Colors.RED
                    print(f"{bg_color}{fg_color}{piece_symbol}{Colors.RESET}", end=" ")
                else:
                    print(f"{bg_color} {Colors.RESET}", end=" ")

            print(Colors.BOLD + "│" + Colors.RESET)

        print("  " + Colors.BOLD + "└─────────────────┘" + Colors.RESET)
        print("  " + Colors.BOLD + "  a b c d e f g h  " + Colors.RESET + "\n")

    def print_game_status(self, board):
        """
        Print the current game status.

        Args:
            board: A chess.Board object
        """
        if board.is_checkmate():
            winner = "Black" if board.turn == chess.WHITE else "White"
            print(f"{Colors.BOLD}{Colors.YELLOW}Checkmate! {winner} wins.{Colors.RESET}")
        elif board.is_stalemate():
            print(f"{Colors.BOLD}{Colors.YELLOW}Stalemate! The game is a draw.{Colors.RESET}")
        elif board.is_insufficient_material():
            print(f"{Colors.BOLD}{Colors.YELLOW}Draw due to insufficient material.{Colors.RESET}")
        elif board.is_check():
            print(f"{Colors.BOLD}{Colors.RED}Check!{Colors.RESET}")

    def print_help(self):
        """Print help information."""
        print(f"\n{Colors.BOLD}Commands:{Colors.RESET}")
        print("  move: Enter a move in UCI format (e.g., 'e2e4') or algebraic notation (e.g., 'e4')")
        print("  help: Show this help message")
        print("  board: Redraw the board")
        print("  resign: Resign the game")
        print("  new: Start a new game")
        print("  flip: Switch sides with the computer")
        print("  level [1-20]: Set difficulty level (1=easiest, 20=hardest)")
        print("  hint: Get a move suggestion")
        print("  eval: Show position evaluation")
        print("  book on: Enable opening book")
        print("  book off: Disable opening book")
        print("  book status: Show opening book status")
        print("  cache on: Enable position caching (transposition table)")
        print("  cache off: Disable position caching")
        print("  cache status: Show cache statistics")
        print("  search on: Enable alpha-beta search algorithm")
        print("  search off: Disable alpha-beta search (use simple search)")
        print("  search status: Show search algorithm status")
        print("  tactical on: Enable quiescence search for tactical positions")
        print("  tactical off: Disable quiescence search")
        print("  tactical status: Show quiescence search status")
        print("  pruning on: Enable null-move pruning for faster search")
        print("  pruning off: Disable null-move pruning")
        print("  pruning status: Show null-move pruning status")
        print("  positional on: Enable advanced positional evaluation")
        print("  positional off: Disable advanced positional evaluation (use simple material counting)")
        print("  positional status: Show positional evaluation status")
        print("  style solid: Use solid, defensive opening repertoire")
        print("  style aggressive: Use aggressive, attacking opening repertoire")
        print("  style tricky: Use tricky, surprising opening repertoire with traps")
        print("  style balanced: Use balanced, standard opening repertoire")
        print("  opening stats: Show opening repertoire statistics")
        print("  undo: Undo the last move (or u)")
        print("  redo: Redo a previously undone move (or r)")
        print("  learn on: Enable machine learning system")
        print("  learn off: Disable machine learning system")
        print("  learn status: Show learning system statistics")
        print("  result [1/0.5/0]: Record game result (1=white win, 0.5=draw, 0=black win)")
        print("  learn: Process recorded positions and learn from the game")
        print("  quit: Exit the program")
        print("\nPress Enter to continue...")
        input()

    def get_user_move(self, board):
        """
        Get a move from the user.

        Args:
            board: A chess.Board object

        Returns:
            A chess.Move object or a command string
        """
        while True:
            try:
                move_str = input(f"{Colors.BOLD}Your move: {Colors.RESET}").strip().lower()

                # Handle special commands
                if move_str in ['quit', 'exit', 'q']:
                    return 'quit'
                elif move_str in ['help', 'h', '?']:
                    return 'help'
                elif move_str in ['board', 'b']:
                    return 'board'
                elif move_str in ['resign', 'r']:
                    return 'resign'
                elif move_str in ['new', 'n']:
                    return 'new'
                elif move_str in ['flip', 'f']:
                    return 'flip'
                elif move_str.startswith('level '):
                    return move_str
                elif move_str in ['hint']:
                    return 'hint'
                elif move_str in ['eval', 'evaluation']:
                    return 'eval'
                elif move_str in ['book on', 'bookon']:
                    return 'book on'
                elif move_str in ['book off', 'bookoff']:
                    return 'book off'
                elif move_str in ['book status', 'bookstatus']:
                    return 'book status'
                elif move_str in ['cache on', 'cacheon']:
                    return 'cache on'
                elif move_str in ['cache off', 'cacheoff']:
                    return 'cache off'
                elif move_str in ['cache status', 'cachestatus']:
                    return 'cache status'
                elif move_str in ['search on', 'searchon', 'alphabeta on']:
                    return 'search on'
                elif move_str in ['search off', 'searchoff', 'alphabeta off']:
                    return 'search off'
                elif move_str in ['search status', 'searchstatus']:
                    return 'search status'
                elif move_str in ['tactical on', 'tacticson', 'quiescence on']:
                    return 'tactical on'
                elif move_str in ['tactical off', 'tacticsoff', 'quiescence off']:
                    return 'tactical off'
                elif move_str in ['tactical status', 'tacticsstatus']:
                    return 'tactical status'
                elif move_str in ['pruning on', 'pruningon', 'nullmove on']:
                    return 'pruning on'
                elif move_str in ['pruning off', 'pruningoff', 'nullmove off']:
                    return 'pruning off'
                elif move_str in ['pruning status', 'pruningstatus']:
                    return 'pruning status'
                elif move_str in ['positional on', 'positionon']:
                    return 'positional on'
                elif move_str in ['positional off', 'positionoff']:
                    return 'positional off'
                elif move_str in ['positional status', 'positionalstatus']:
                    return 'positional status'
                elif move_str in ['style solid', 'solid']:
                    return 'style solid'
                elif move_str in ['style aggressive', 'aggressive']:
                    return 'style aggressive'
                elif move_str in ['style tricky', 'tricky']:
                    return 'style tricky'
                elif move_str in ['style balanced', 'balanced']:
                    return 'style balanced'
                elif move_str in ['opening stats', 'openingstats']:
                    return 'opening stats'
                elif move_str in ['undo', 'u']:
                    return 'undo'
                elif move_str in ['redo', 'r']:
                    return 'redo'
                elif move_str in ['learn on', 'learnon']:
                    return 'learn on'
                elif move_str in ['learn off', 'learnoff']:
                    return 'learn off'
                elif move_str in ['learn status', 'learnstatus']:
                    return 'learn status'
                elif move_str.startswith('result '):
                    return move_str  # Pass through result command
                elif move_str == 'learn':
                    return 'learn'

                # Try to parse as UCI move (e.g., "e2e4")
                try:
                    move = chess.Move.from_uci(move_str)
                    if move in board.legal_moves:
                        return move
                except ValueError:
                    pass

                # Try to parse as algebraic notation (e.g., "e4", "Nf3")
                try:
                    move = board.parse_san(move_str)
                    return move
                except ValueError:
                    print(f"{Colors.RED}Invalid move. Try again or type 'help' for commands.{Colors.RESET}")

            except KeyboardInterrupt:
                print("\nUse 'quit' to exit.")
            except Exception as e:
                print(f"{Colors.RED}Error: {e}{Colors.RESET}")

    def print_engine_analysis(self, engine, board):
        """
        Print the engine's analysis of the position.

        Args:
            engine: The chess engine object
            board: A chess.Board object
        """
        print(f"\n{Colors.BOLD}Engine Analysis:{Colors.RESET}")

        # Get top moves
        top_moves = engine.get_top_moves(board, num_moves=3)

        # Get evaluation
        eval_data = engine.get_board_evaluation(board)

        # Print evaluation
        if eval_data['type'] == 'cp':
            eval_value = eval_data['value'] / 100.0
            if board.turn == chess.BLACK:
                eval_value = -eval_value

            if eval_value > 0:
                eval_str = f"+{eval_value:.2f}"
                print(f"Evaluation: {Colors.GREEN}{eval_str}{Colors.RESET} (White advantage)")
            elif eval_value < 0:
                eval_str = f"{eval_value:.2f}"
                print(f"Evaluation: {Colors.RED}{eval_str}{Colors.RESET} (Black advantage)")
            else:
                print(f"Evaluation: {Colors.YELLOW}0.00{Colors.RESET} (Equal position)")
        else:  # mate
            mate_value = eval_data['value']
            if mate_value > 0:
                print(f"Evaluation: {Colors.GREEN}Mate in {mate_value}{Colors.RESET}")
            else:
                print(f"Evaluation: {Colors.RED}Mate in {-mate_value}{Colors.RESET}")

        # Print top moves
        if top_moves:
            print(f"\n{Colors.BOLD}Top moves:{Colors.RESET}")
            for i, move_data in enumerate(top_moves):
                move_uci = move_data.get('Move', '')
                try:
                    move = chess.Move.from_uci(move_uci)
                    move_san = board.san(move)

                    if 'Centipawn' in move_data:
                        cp_value = move_data['Centipawn'] / 100.0
                        print(f"{i+1}. {move_san} ({cp_value:+.2f})")
                    elif 'Mate' in move_data:
                        mate_value = move_data['Mate']
                        print(f"{i+1}. {move_san} (Mate in {mate_value})")
                    else:
                        print(f"{i+1}. {move_san}")
                except Exception:
                    pass

        print("\nPress Enter to continue...")
        input()
