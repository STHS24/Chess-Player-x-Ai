"""
Text-based Chess Application Module
This module contains the text-based application for the chess game.
"""

import chess
import sys
import time

from chess_ai.engine.sunfish_wrapper import SunfishWrapper, EngineInitializationError
from chess_ai.engine.fallback_engine import FallbackEngine
from chess_ai.cli.text_interface import TextInterface
from chess_ai.config.settings import Colors
from chess_ai.utils.helpers import check_game_over

class TextChessApp:
    """Text-based chess application class."""

    def __init__(self):
        """Initialize the text-based chess application."""
        # Initialize the chess board
        self.board = chess.Board()

        # Initialize the text interface
        self.interface = TextInterface()

        # Game state variables
        self.player_color = chess.WHITE  # Player plays as white by default
        self.last_move = None

        # Move history for undo/redo functionality
        self.redone_moves = []  # List of moves that were undone and can be redone

        # Initialize the engine
        self.initialize_engine()

    def initialize_engine(self, max_attempts=3):
        """
        Initialize the chess engine with retry logic.

        Args:
            max_attempts: Maximum number of initialization attempts
        """
        try:
            print("Initializing chess engine...")
            self.engine = SunfishWrapper(max_retries=max_attempts)
            self.engine.set_difficulty(10)  # Medium difficulty
            print("Engine initialized successfully!")
        except EngineInitializationError as e:
            print(f"Error initializing engine: {e}")
            print("Using fallback random move engine.")
            # Create a simple fallback engine
            self.engine = FallbackEngine()

    def reset_game(self):
        """Reset the game to the initial state."""
        self.board = chess.Board()
        self.last_move = None
        self.redone_moves = []

        # Reset the engine's game state if it has a reset method
        if hasattr(self.engine, 'reset_game'):
            self.engine.reset_game()

        # If player is black, make AI move first
        if self.player_color == chess.BLACK:
            self.make_ai_move()

    def undo_move(self):
        """Undo the last move."""
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
                print(f"{Colors.CYAN}Undoing move: {move.uci()}{Colors.RESET}")

        # Update last move
        self.last_move = self.board.move_stack[-1] if self.board.move_stack else None
        return True

    def redo_move(self):
        """Redo a previously undone move."""
        if not self.redone_moves:
            # No moves to redo
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
                print(f"{Colors.CYAN}Redoing move: {move.uci()}{Colors.RESET}")

        # Update last move
        self.last_move = self.board.move_stack[-1] if self.board.move_stack else None
        return True

    def run(self):
        """Run the main game loop."""
        try:
            while True:
                # Print the board
                self.interface.print_board(self.board, self.last_move)

                # Print whose turn it is
                turn_str = "White" if self.board.turn == chess.WHITE else "Black"
                print(f"{Colors.BOLD}Turn: {turn_str}{Colors.RESET}")

                # Print game status
                self.interface.print_game_status(self.board)

                # Check if game is over
                is_over, result = check_game_over(self.board)
                if is_over:
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
                        self.board = chess.Board()
                        self.player_color = chess.WHITE
                        self.last_move = None
                        continue

                # Player's turn
                if self.board.turn == self.player_color:
                    move = self.interface.get_user_move(self.board)

                    # Handle special commands
                    if isinstance(move, str):  # Check if move is a string command
                        if move == 'quit':
                            break
                        elif move == 'help':
                            self.interface.print_help()
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
                                self.board = chess.Board()
                                self.player_color = chess.WHITE
                                self.last_move = None
                                continue
                        elif move == 'new':
                            self.board = chess.Board()
                            self.player_color = chess.WHITE
                            self.last_move = None
                            continue
                        elif move == 'flip':
                            self.player_color = not self.player_color
                            continue
                        elif move.startswith('level '):
                            try:
                                level = int(move.split()[1])
                                self.engine.set_difficulty(level)
                                print(f"Difficulty set to {level}")
                                time.sleep(1)
                            except (ValueError, IndexError):
                                print("Invalid level. Use a number between 1 and 20.")
                                time.sleep(1)
                            continue
                        elif move == 'hint':
                            hint_move = self.engine.get_best_move(self.board)
                            if hint_move:
                                hint_move_obj = chess.Move.from_uci(hint_move)
                                hint_san = self.board.san(hint_move_obj)
                                print(f"{Colors.CYAN}Hint: {hint_san}{Colors.RESET}")
                                time.sleep(2)
                            continue
                        elif move == 'eval':
                            self.interface.print_engine_analysis(self.engine, self.board)
                            continue
                        elif move == 'book on':
                            self.engine.set_opening_book(True)
                            print(f"{Colors.GREEN}Opening book enabled.{Colors.RESET}")
                            time.sleep(1)
                            continue
                        elif move == 'book off':
                            self.engine.set_opening_book(False)
                            print(f"{Colors.YELLOW}Opening book disabled.{Colors.RESET}")
                            time.sleep(1)
                            continue
                        elif move == 'book status':
                            if hasattr(self.engine, 'use_opening_book') and hasattr(self.engine, 'opening_book'):
                                status = "enabled" if self.engine.use_opening_book else "disabled"
                                book_available = "available" if (self.engine.opening_book and self.engine.opening_book.is_available) else "not available"
                                book_path = self.engine.opening_book.book_path if self.engine.opening_book else "None"
                                print(f"{Colors.CYAN}Opening book is {status}.{Colors.RESET}")
                                print(f"{Colors.CYAN}Book file is {book_available}.{Colors.RESET}")
                                print(f"{Colors.CYAN}Book path: {book_path}{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Opening book not supported by this engine.{Colors.RESET}")
                            time.sleep(2)
                            continue
                        elif move == 'cache on':
                            if hasattr(self.engine, 'set_transposition_table'):
                                self.engine.set_transposition_table(True)
                                print(f"{Colors.GREEN}Position cache enabled.{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Position caching not supported by this engine.{Colors.RESET}")
                            time.sleep(1)
                            continue
                        elif move == 'cache off':
                            if hasattr(self.engine, 'set_transposition_table'):
                                self.engine.set_transposition_table(False)
                                print(f"{Colors.YELLOW}Position cache disabled.{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Position caching not supported by this engine.{Colors.RESET}")
                            time.sleep(1)
                            continue
                        elif move == 'cache status':
                            if hasattr(self.engine, 'use_transposition_table') and hasattr(self.engine, 'transposition_table'):
                                status = "enabled" if self.engine.use_transposition_table else "disabled"
                                print(f"{Colors.CYAN}Position cache is {status}.{Colors.RESET}")

                                if self.engine.transposition_table:
                                    stats = self.engine.transposition_table.get_stats()
                                    print(f"{Colors.CYAN}Cache size: {stats['size']} / {stats['max_size']} positions ({stats['usage']}){Colors.RESET}")
                                    print(f"{Colors.CYAN}Hit rate: {stats['hit_rate']} ({stats['hits']} hits, {stats['misses']} misses){Colors.RESET}")
                                    print(f"{Colors.CYAN}Collisions: {stats['collisions']}{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Position caching not supported by this engine.{Colors.RESET}")
                            time.sleep(2)
                            continue
                        elif move == 'search on':
                            if hasattr(self.engine, 'set_alpha_beta'):
                                self.engine.set_alpha_beta(True)
                                print(f"{Colors.GREEN}Alpha-beta search enabled.{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Alpha-beta search not supported by this engine.{Colors.RESET}")
                            time.sleep(1)
                            continue
                        elif move == 'search off':
                            if hasattr(self.engine, 'set_alpha_beta'):
                                self.engine.set_alpha_beta(False)
                                print(f"{Colors.YELLOW}Alpha-beta search disabled.{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Alpha-beta search not supported by this engine.{Colors.RESET}")
                            time.sleep(1)
                            continue
                        elif move == 'search status':
                            if hasattr(self.engine, 'use_alpha_beta') and hasattr(self.engine, 'search_algorithm'):
                                status = "enabled" if self.engine.use_alpha_beta else "disabled"
                                print(f"{Colors.CYAN}Alpha-beta search is {status}.{Colors.RESET}")

                                if self.engine.search_algorithm:
                                    depth = self.engine.search_algorithm.max_depth
                                    print(f"{Colors.CYAN}Search depth: {depth}{Colors.RESET}")
                                    if hasattr(self.engine.search_algorithm, 'get_stats'):
                                        stats = self.engine.search_algorithm.get_stats()
                                        print(f"{Colors.CYAN}Last search: {stats['total_nodes']} nodes, {stats['nps']} nodes/sec{Colors.RESET}")
                                        print(f"{Colors.CYAN}Cache hit rate: {stats['cache_hit_rate']}{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Alpha-beta search not supported by this engine.{Colors.RESET}")
                            time.sleep(2)
                            continue
                        elif move == 'tactical on':
                            if hasattr(self.engine, 'set_quiescence'):
                                self.engine.set_quiescence(True)
                                print(f"{Colors.GREEN}Quiescence search enabled.{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Quiescence search not supported by this engine.{Colors.RESET}")
                            time.sleep(1)
                            continue
                        elif move == 'tactical off':
                            if hasattr(self.engine, 'set_quiescence'):
                                self.engine.set_quiescence(False)
                                print(f"{Colors.YELLOW}Quiescence search disabled.{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Quiescence search not supported by this engine.{Colors.RESET}")
                            time.sleep(1)
                            continue
                        elif move == 'tactical status':
                            if hasattr(self.engine, 'use_quiescence') and hasattr(self.engine, 'search_algorithm'):
                                status = "enabled" if self.engine.use_quiescence else "disabled"
                                print(f"{Colors.CYAN}Quiescence search is {status}.{Colors.RESET}")

                                if self.engine.search_algorithm and self.engine.use_quiescence:
                                    depth = self.engine.search_algorithm.quiescence_depth
                                    print(f"{Colors.CYAN}Quiescence depth: {depth}{Colors.RESET}")
                                    if hasattr(self.engine.search_algorithm, 'get_stats'):
                                        stats = self.engine.search_algorithm.get_stats()
                                        print(f"{Colors.CYAN}Regular nodes: {stats['nodes']}, Quiescence nodes: {stats['q_nodes']}{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Quiescence search not supported by this engine.{Colors.RESET}")
                            time.sleep(2)
                            continue
                        elif move == 'pruning on':
                            if hasattr(self.engine, 'set_null_move'):
                                self.engine.set_null_move(True)
                                print(f"{Colors.GREEN}Null-move pruning enabled.{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Null-move pruning not supported by this engine.{Colors.RESET}")
                            time.sleep(1)
                            continue
                        elif move == 'pruning off':
                            if hasattr(self.engine, 'set_null_move'):
                                self.engine.set_null_move(False)
                                print(f"{Colors.YELLOW}Null-move pruning disabled.{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Null-move pruning not supported by this engine.{Colors.RESET}")
                            time.sleep(1)
                            continue
                        elif move == 'pruning status':
                            if hasattr(self.engine, 'use_null_move') and hasattr(self.engine, 'search_algorithm'):
                                status = "enabled" if self.engine.use_null_move else "disabled"
                                print(f"{Colors.CYAN}Null-move pruning is {status}.{Colors.RESET}")

                                if self.engine.search_algorithm and self.engine.use_null_move:
                                    reduction = self.engine.search_algorithm.null_move_reduction
                                    print(f"{Colors.CYAN}Reduction factor: {reduction}{Colors.RESET}")
                                    if hasattr(self.engine.search_algorithm, 'get_stats'):
                                        stats = self.engine.search_algorithm.get_stats()
                                        print(f"{Colors.CYAN}Null-move cutoffs: {stats['null_move_cutoffs']}{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Null-move pruning not supported by this engine.{Colors.RESET}")
                            time.sleep(2)
                            continue
                        elif move == 'positional on':
                            if hasattr(self.engine, 'set_positional_eval'):
                                self.engine.set_positional_eval(True)
                                print(f"{Colors.GREEN}Advanced positional evaluation enabled.{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Positional evaluation not supported by this engine.{Colors.RESET}")
                            time.sleep(1)
                            continue
                        elif move == 'positional off':
                            if hasattr(self.engine, 'set_positional_eval'):
                                self.engine.set_positional_eval(False)
                                print(f"{Colors.YELLOW}Advanced positional evaluation disabled.{Colors.RESET}")
                                print(f"{Colors.YELLOW}Using simple material counting.{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Positional evaluation not supported by this engine.{Colors.RESET}")
                            time.sleep(1)
                            continue
                        elif move == 'positional status':
                            if hasattr(self.engine, 'use_positional_eval'):
                                status = "enabled" if self.engine.use_positional_eval else "disabled"
                                print(f"{Colors.CYAN}Advanced positional evaluation is {status}.{Colors.RESET}")
                                if not self.engine.use_positional_eval:
                                    print(f"{Colors.CYAN}Using simple material counting.{Colors.RESET}")
                                else:
                                    print(f"{Colors.CYAN}Using pawn structure, king safety, and mobility analysis.{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Positional evaluation not supported by this engine.{Colors.RESET}")
                            time.sleep(2)
                            continue
                        elif move.startswith('style '):
                            style = move.split(' ')[1]
                            if hasattr(self.engine, 'set_opening_style'):
                                self.engine.set_opening_style(style)
                            else:
                                print(f"{Colors.RED}Opening styles not supported by this engine.{Colors.RESET}")
                            time.sleep(1)
                            continue
                        elif move == 'opening stats':
                            if hasattr(self.engine, 'get_opening_stats'):
                                stats = self.engine.get_opening_stats()
                                print(f"{Colors.CYAN}Opening Repertoire Statistics:{Colors.RESET}")
                                print(f"{Colors.CYAN}Total positions: {stats.get('total_positions', 0)}{Colors.RESET}")
                                print(f"{Colors.CYAN}Total games: {stats.get('total_games', 0)}{Colors.RESET}")
                                print(f"{Colors.CYAN}Success rate: {stats.get('success_rate', 0.0):.2f}{Colors.RESET}")
                                print(f"{Colors.CYAN}Current style: {stats.get('style', 'balanced')}{Colors.RESET}")

                                # Show style statistics
                                if 'styles' in stats:
                                    print(f"{Colors.CYAN}Style positions:{Colors.RESET}")
                                    for style, count in stats['styles'].items():
                                        print(f"{Colors.CYAN}  {style}: {count}{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Opening statistics not supported by this engine.{Colors.RESET}")
                            time.sleep(3)
                            continue
                        elif move == 'undo':
                            if self.undo_move():
                                print(f"{Colors.GREEN}Move undone.{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Cannot undo any further.{Colors.RESET}")
                            time.sleep(1)
                            continue
                        elif move == 'redo':
                            if self.redo_move():
                                print(f"{Colors.GREEN}Move redone.{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Cannot redo any further.{Colors.RESET}")
                            time.sleep(1)
                            continue
                        elif move == 'learn on':
                            if hasattr(self.engine, 'set_learning'):
                                self.engine.set_learning(True)
                                print(f"{Colors.GREEN}Learning system enabled.{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Learning system not supported by this engine.{Colors.RESET}")
                            time.sleep(1)
                            continue
                        elif move == 'learn off':
                            if hasattr(self.engine, 'set_learning'):
                                self.engine.set_learning(False)
                                print(f"{Colors.YELLOW}Learning system disabled.{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Learning system not supported by this engine.{Colors.RESET}")
                            time.sleep(1)
                            continue
                        elif move == 'learn status':
                            if hasattr(self.engine, 'use_learning') and hasattr(self.engine, 'get_learning_stats'):
                                status = "enabled" if self.engine.use_learning else "disabled"
                                print(f"{Colors.CYAN}Learning system is {status}.{Colors.RESET}")

                                if self.engine.use_learning:
                                    try:
                                        stats = self.engine.get_learning_stats()
                                        print(f"{Colors.CYAN}Positions stored: {stats['positions_stored']}{Colors.RESET}")
                                        print(f"{Colors.CYAN}Games learned: {stats['games_learned']}{Colors.RESET}")
                                        print(f"{Colors.CYAN}Learning rate: {stats['learning_rate']}{Colors.RESET}")
                                    except Exception as e:
                                        print(f"{Colors.RED}Error getting learning stats: {e}{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Learning system not supported by this engine.{Colors.RESET}")
                            time.sleep(2)
                            continue
                        elif move.startswith('result '):
                            if hasattr(self.engine, 'record_game_result'):
                                try:
                                    result_str = move.split(' ')[1]
                                    result = float(result_str)
                                    if result not in [0.0, 0.5, 1.0]:
                                        print(f"{Colors.RED}Invalid result value. Use 1 (white win), 0.5 (draw), or 0 (black win).{Colors.RESET}")
                                    else:
                                        self.engine.record_game_result(result)
                                        print(f"{Colors.GREEN}Game result recorded: {result}{Colors.RESET}")
                                except ValueError:
                                    print(f"{Colors.RED}Invalid result format. Use 'result 1', 'result 0.5', or 'result 0'.{Colors.RESET}")
                                except Exception as e:
                                    print(f"{Colors.RED}Error recording game result: {e}{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Learning system not supported by this engine.{Colors.RESET}")
                            time.sleep(1)
                            continue
                        elif move == 'learn':
                            if hasattr(self.engine, 'learn_from_game'):
                                try:
                                    self.engine.learn_from_game()
                                    print(f"{Colors.GREEN}Learning completed from game data.{Colors.RESET}")
                                except Exception as e:
                                    print(f"{Colors.RED}Error learning from game: {e}{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Learning system not supported by this engine.{Colors.RESET}")
                            time.sleep(1)
                            continue

                    # Clear any redone moves when a new move is made
                    if self.redone_moves:
                        self.redone_moves = []

                    # Make the move
                    self.board.push(move)
                    self.last_move = move

                # Computer's turn
                else:
                    print(f"{Colors.BOLD}Computer is thinking...{Colors.RESET}")

                    # Get the computer's move
                    try:
                        ai_move_uci = self.engine.get_best_move(self.board)
                        if ai_move_uci:
                            ai_move = chess.Move.from_uci(ai_move_uci)
                            ai_move_san = self.board.san(ai_move)

                            # Clear any redone moves when a new move is made
                            if self.redone_moves:
                                self.redone_moves = []

                            # Make the move
                            self.board.push(ai_move)
                            self.last_move = ai_move

                            # Print the engine's thinking
                            if hasattr(self.engine, 'thinking_lines') and self.engine.thinking_lines:
                                print(f"{Colors.CYAN}Computer plays: {ai_move_san}{Colors.RESET}")
                                print(f"{Colors.CYAN}Analysis: {self.engine.thinking_lines[0]}{Colors.RESET}")
                                time.sleep(1)
                        else:
                            print(f"{Colors.RED}Engine couldn't find a move. Making a random move.{Colors.RESET}")
                            import random
                            legal_moves = list(self.board.legal_moves)
                            if legal_moves:
                                random_move = random.choice(legal_moves)
                                self.board.push(random_move)
                                self.last_move = random_move
                            time.sleep(1)
                    except Exception as e:
                        print(f"{Colors.RED}Error during computer move: {e}{Colors.RESET}")
                        print("Making a random move instead.")
                        import random
                        legal_moves = list(self.board.legal_moves)
                        if legal_moves:
                            random_move = random.choice(legal_moves)
                            self.board.push(random_move)
                            self.last_move = random_move
                        time.sleep(1)

        except KeyboardInterrupt:
            print("\nExiting...")

        finally:
            # Clean up resources
            if hasattr(self, 'engine') and hasattr(self.engine, 'cleanup'):
                self.engine.cleanup()

        print("Thanks for playing!")
        return 0

def main():
    """Main function to run the text-based chess application."""
    app = TextChessApp()
    return app.run()

if __name__ == "__main__":
    sys.exit(main())
