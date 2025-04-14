#!/usr/bin/env python3
"""
Text-based Chess Interface
A simple command-line interface for playing chess against the Sunfish engine.
"""

import chess
import sys
import time
import os
from sunfish_wrapper import SunfishWrapper, EngineInitializationError

# ANSI color codes for terminal output
class Colors:
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

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_board(board, last_move=None):
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

def print_game_status(board):
    """Print the current game status."""
    if board.is_checkmate():
        winner = "Black" if board.turn == chess.WHITE else "White"
        print(f"{Colors.BOLD}{Colors.YELLOW}Checkmate! {winner} wins.{Colors.RESET}")
    elif board.is_stalemate():
        print(f"{Colors.BOLD}{Colors.YELLOW}Stalemate! The game is a draw.{Colors.RESET}")
    elif board.is_insufficient_material():
        print(f"{Colors.BOLD}{Colors.YELLOW}Draw due to insufficient material.{Colors.RESET}")
    elif board.is_check():
        print(f"{Colors.BOLD}{Colors.RED}Check!{Colors.RESET}")

def print_help():
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
    print("  quit: Exit the program")
    print("\nPress Enter to continue...")
    input()

def get_user_move(board):
    """
    Get a move from the user.

    Args:
        board: A chess.Board object

    Returns:
        A chess.Move object or None if the input was not a valid move
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

def print_engine_analysis(engine, board):
    """Print the engine's analysis of the position."""
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

def main():
    """Main function to run the text-based chess interface."""
    # Initialize the board
    board = chess.Board()

    # Initialize the engine
    try:
        print("Initializing chess engine...")
        engine = SunfishWrapper(max_retries=3)
        engine.set_difficulty(10)  # Medium difficulty
        print("Engine initialized successfully!")
    except EngineInitializationError as e:
        print(f"Error initializing engine: {e}")
        print("Using fallback random move engine.")
        # Create a simple fallback engine
        class FallbackEngine:
            def __init__(self):
                self.is_initialized = True

            def get_best_move(self, board):
                import random
                legal_moves = list(board.legal_moves)
                if legal_moves:
                    return random.choice(legal_moves).uci()
                return None

            def set_difficulty(self, level):
                print(f"Difficulty set to {level} (has no effect in fallback mode)")

            def get_board_evaluation(self, board):
                return {"type": "cp", "value": 0}

            def get_top_moves(self, board, num_moves=3):
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
                pass

        engine = FallbackEngine()

    # Game state
    player_color = chess.WHITE  # Player starts as white
    last_move = None

    # Main game loop
    try:
        while True:
            # Print the board
            print_board(board, last_move)

            # Print whose turn it is
            turn_str = "White" if board.turn == chess.WHITE else "Black"
            print(f"{Colors.BOLD}Turn: {turn_str}{Colors.RESET}")

            # Print game status
            print_game_status(board)

            # Check if game is over
            if board.is_game_over():
                result = board.result()
                if result == "1-0":
                    print(f"{Colors.GREEN}White wins!{Colors.RESET}")
                elif result == "0-1":
                    print(f"{Colors.RED}Black wins!{Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}Game drawn!{Colors.RESET}")

                print("\nPress Enter to start a new game, or type 'quit' to exit...")
                cmd = input().strip().lower()
                if cmd in ['quit', 'exit', 'q']:
                    break
                else:
                    board = chess.Board()
                    player_color = chess.WHITE
                    last_move = None
                    continue

            # Player's turn
            if board.turn == player_color:
                move = get_user_move(board)

                # Handle special commands
                if isinstance(move, str):  # Check if move is a string command
                    if move == 'quit':
                        break
                    elif move == 'help':
                        print_help()
                        continue
                    elif move == 'board':
                        continue
                    elif move == 'resign':
                        print(f"{Colors.YELLOW}You resigned. Computer wins!{Colors.RESET}")
                        print("\nPress Enter to start a new game, or type 'quit' to exit...")
                        cmd = input().strip().lower()
                        if cmd in ['quit', 'exit', 'q']:
                            break
                        else:
                            board = chess.Board()
                            player_color = chess.WHITE
                            last_move = None
                            continue
                    elif move == 'new':
                        board = chess.Board()
                        player_color = chess.WHITE
                        last_move = None
                        continue
                    elif move == 'flip':
                        player_color = not player_color
                        continue
                    elif move.startswith('level '):
                        try:
                            level = int(move.split()[1])
                            engine.set_difficulty(level)
                            print(f"Difficulty set to {level}")
                            time.sleep(1)
                        except (ValueError, IndexError):
                            print("Invalid level. Use a number between 1 and 20.")
                            time.sleep(1)
                        continue
                    elif move == 'hint':
                        hint_move = engine.get_best_move(board)
                        if hint_move:
                            hint_move_obj = chess.Move.from_uci(hint_move)
                            hint_san = board.san(hint_move_obj)
                            print(f"{Colors.CYAN}Hint: {hint_san}{Colors.RESET}")
                            time.sleep(2)
                        continue
                    elif move == 'eval':
                        print_engine_analysis(engine, board)
                        continue

                # Make the move
                board.push(move)
                last_move = move

            # Computer's turn
            else:
                print(f"{Colors.BOLD}Computer is thinking...{Colors.RESET}")

                # Get the computer's move
                try:
                    ai_move_uci = engine.get_best_move(board)
                    if ai_move_uci:
                        ai_move = chess.Move.from_uci(ai_move_uci)
                        ai_move_san = board.san(ai_move)

                        # Make the move
                        board.push(ai_move)
                        last_move = ai_move

                        # Print the engine's thinking
                        if hasattr(engine, 'thinking_lines') and engine.thinking_lines:
                            print(f"{Colors.CYAN}Computer plays: {ai_move_san}{Colors.RESET}")
                            print(f"{Colors.CYAN}Analysis: {engine.thinking_lines[0]}{Colors.RESET}")
                            time.sleep(1)
                    else:
                        print(f"{Colors.RED}Engine couldn't find a move. Making a random move.{Colors.RESET}")
                        import random
                        legal_moves = list(board.legal_moves)
                        if legal_moves:
                            random_move = random.choice(legal_moves)
                            board.push(random_move)
                            last_move = random_move
                        time.sleep(1)
                except Exception as e:
                    print(f"{Colors.RED}Error during computer move: {e}{Colors.RESET}")
                    print("Making a random move instead.")
                    import random
                    legal_moves = list(board.legal_moves)
                    if legal_moves:
                        random_move = random.choice(legal_moves)
                        board.push(random_move)
                        last_move = random_move
                    time.sleep(1)

    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        # Clean up resources
        if engine and hasattr(engine, 'cleanup'):
            engine.cleanup()

    print("Thanks for playing!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
