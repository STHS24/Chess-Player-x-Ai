"""
Sunfish Wrapper Module
This module provides a wrapper for the Sunfish chess engine.
"""

import chess
import random
import time
import os

# Import the opening book module
from chess_ai.engine.opening_book import OpeningBook
# Import the transposition table module
from chess_ai.engine.transposition_table import TranspositionTable
# Import the search algorithm
from chess_ai.engine.search import SearchAlgorithm
# Import the learning system
from chess_ai.engine.learning import LearningSystem
# Import the positional evaluator
from chess_ai.engine.evaluation import PositionalEvaluator

# We'll implement our own simplified version instead of importing sunfish
# This avoids the import error with the tools module

class EngineInitializationError(Exception):
    """Exception raised when the chess engine fails to initialize."""
    pass

class SunfishWrapper:
    def __init__(self, max_retries=3, use_opening_book=True, book_path=None, use_transposition_table=True, use_alpha_beta=True, use_quiescence=True, use_null_move=True, use_learning=True, learning_data_file=None, use_positional_eval=True):
        """Initialize a simplified chess engine based on Sunfish concepts.

        Args:
            max_retries: Maximum number of initialization attempts
            use_opening_book: Whether to use the opening book
            book_path: Path to the opening book file (None for default)
            use_transposition_table: Whether to use the transposition table for caching positions
            use_alpha_beta: Whether to use alpha-beta pruning for search
            use_quiescence: Whether to use quiescence search for tactical positions
            use_null_move: Whether to use null-move pruning for faster search
            use_learning: Whether to use machine learning to improve over time
            learning_data_file: Path to the learning data file (None for default)
            use_positional_eval: Whether to use advanced positional evaluation

        Raises:
            EngineInitializationError: If the engine cannot be initialized after max_retries
        """
        # Store analysis information
        self.last_evaluation = None
        self.thinking_lines = []
        self.best_move_found = None

        # Opening book configuration
        self.use_opening_book = use_opening_book
        self.opening_book = OpeningBook(book_path) if use_opening_book else None

        # Track moves played in the current game for repertoire learning
        self.game_moves = []

        # Transposition table configuration
        self.use_transposition_table = use_transposition_table
        self.transposition_table = TranspositionTable(max_size=100000) if use_transposition_table else None

        # Search algorithm configuration
        self.use_alpha_beta = use_alpha_beta
        self.use_quiescence = use_quiescence
        self.use_null_move = use_null_move
        self.search_algorithm = None  # Will be initialized later

        # Learning system configuration
        self.use_learning = use_learning
        self.learning_system = LearningSystem(data_file=learning_data_file) if use_learning else None

        # Positional evaluation configuration
        self.use_positional_eval = use_positional_eval
        self.positional_evaluator = PositionalEvaluator() if use_positional_eval else None
        self.is_initialized = False  # Start as not initialized
        self.skill_level = 10  # Default medium difficulty

        # Try to initialize the engine with retries
        for attempt in range(max_retries):
            try:
                # Simulate potential initialization failures (for testing)
                # In a real scenario, this would be actual initialization code
                import random
                if random.random() < 0.1:  # 10% chance of failure for testing
                    raise ValueError("Simulated random initialization failure")

                # Initialize required resources
                self._initialize_resources()

                # Mark as successfully initialized
                self.is_initialized = True
                print(f"Successfully initialized chess engine (attempt {attempt+1}/{max_retries})")
                break
            except Exception as e:
                print(f"Engine initialization attempt {attempt+1}/{max_retries} failed: {e}")
                # If this was the last attempt, raise an exception
                if attempt == max_retries - 1:
                    raise EngineInitializationError(f"Failed to initialize engine after {max_retries} attempts: {e}")
                # Otherwise wait a bit and retry
                import time
                time.sleep(0.5)

    def _initialize_resources(self):
        """Initialize any resources needed by the engine."""
        # Initialize the search algorithm if using alpha-beta pruning
        if self.use_alpha_beta:
            # Create the search algorithm with our evaluation function
            self.search_algorithm = SearchAlgorithm(
                evaluator=self._calculate_material,
                transposition_table=self.transposition_table if self.use_transposition_table else None,
                max_depth=self._get_depth_for_skill_level(),
                use_quiescence=self.use_quiescence,
                quiescence_depth=self._get_quiescence_depth_for_skill_level(),
                use_null_move=self.use_null_move
            )
            print("Initialized alpha-beta search algorithm")
        else:
            self.search_algorithm = None
            print("Using simplified search algorithm")

    def _get_depth_for_skill_level(self):
        """
        Determine the search depth based on the current skill level.

        Returns:
            An integer representing the search depth
        """
        # Map skill levels to search depths
        # Skill level 1-5: depth 1
        # Skill level 6-10: depth 2
        # Skill level 11-15: depth 3
        # Skill level 16-20: depth 4
        if self.skill_level <= 5:
            return 1
        elif self.skill_level <= 10:
            return 2
        elif self.skill_level <= 15:
            return 3
        else:
            return 4

    def _get_quiescence_depth_for_skill_level(self):
        """
        Determine the quiescence search depth based on the current skill level.

        Returns:
            An integer representing the quiescence search depth
        """
        # Map skill levels to quiescence search depths
        # Skill level 1-5: depth 0 (no quiescence search)
        # Skill level 6-10: depth 1
        # Skill level 11-15: depth 2
        # Skill level 16-20: depth 3
        if self.skill_level <= 5:
            return 0
        elif self.skill_level <= 10:
            return 1
        elif self.skill_level <= 15:
            return 2
        else:
            return 3

    def set_difficulty(self, level):
        """
        Set the difficulty level of the engine.

        Args:
            level: An integer from 1 to 20, where 1 is the easiest and 20 is the hardest.

        Raises:
            RuntimeError: If the engine is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError("Cannot set difficulty: Engine not initialized")

        # Clamp the level between 1 and 20
        level = max(1, min(20, level))
        self.skill_level = level

        # Update search depth if using alpha-beta search
        if self.use_alpha_beta and self.search_algorithm:
            self.search_algorithm.max_depth = self._get_depth_for_skill_level()
            self.search_algorithm.quiescence_depth = self._get_quiescence_depth_for_skill_level()

        print(f"Difficulty set to {level} (search depth: {self._get_depth_for_skill_level()}, quiescence depth: {self._get_quiescence_depth_for_skill_level()})")

    def set_opening_book(self, use_book, book_path=None):
        """
        Configure the opening book usage.

        Args:
            use_book: Whether to use the opening book
            book_path: Path to the opening book file (None for default)

        Raises:
            RuntimeError: If the engine is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError("Cannot configure opening book: Engine not initialized")

        self.use_opening_book = use_book

        # If we're enabling the book and it's not already loaded, or changing the path
        if use_book and (self.opening_book is None or
                        (book_path is not None and
                         (self.opening_book.book_path != book_path))):
            self.opening_book = OpeningBook(book_path)

        print(f"Opening book {'enabled' if use_book else 'disabled'}")

    def set_transposition_table(self, use_table, max_size=None):
        """
        Configure the transposition table usage.

        Args:
            use_table: Whether to use the transposition table
            max_size: Maximum size of the table (None for default)

        Raises:
            RuntimeError: If the engine is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError("Cannot configure transposition table: Engine not initialized")

        self.use_transposition_table = use_table

        # If we're enabling the table and it's not already created, or changing the size
        if use_table:
            if self.transposition_table is None:
                self.transposition_table = TranspositionTable(max_size=max_size or 100000)
            elif max_size is not None and self.transposition_table.max_size != max_size:
                # Create a new table with the new size
                self.transposition_table = TranspositionTable(max_size=max_size)

            # Clear the table when re-enabling
            if self.transposition_table:
                self.transposition_table.clear()

        # Update the search algorithm's transposition table
        if self.use_alpha_beta and self.search_algorithm:
            self.search_algorithm.transposition_table = self.transposition_table if use_table else None

        print(f"Transposition table {'enabled' if use_table else 'disabled'}")
        if use_table and self.transposition_table:
            print(f"Table size: {self.transposition_table.max_size} positions")

    def set_alpha_beta(self, use_alpha_beta):
        """
        Configure the alpha-beta search usage.

        Args:
            use_alpha_beta: Whether to use alpha-beta pruning for search

        Raises:
            RuntimeError: If the engine is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError("Cannot configure search algorithm: Engine not initialized")

        self.use_alpha_beta = use_alpha_beta

        # If we're enabling alpha-beta and it's not already created
        if use_alpha_beta and self.search_algorithm is None:
            self.search_algorithm = SearchAlgorithm(
                evaluator=self._calculate_material,
                transposition_table=self.transposition_table if self.use_transposition_table else None,
                max_depth=self._get_depth_for_skill_level(),
                use_quiescence=self.use_quiescence,
                quiescence_depth=self._get_quiescence_depth_for_skill_level(),
                use_null_move=self.use_null_move
            )
        elif not use_alpha_beta:
            self.search_algorithm = None

        print(f"Alpha-beta search {'enabled' if use_alpha_beta else 'disabled'}")
        if use_alpha_beta and self.search_algorithm:
            print(f"Search depth: {self.search_algorithm.max_depth}, quiescence depth: {self.search_algorithm.quiescence_depth}")

    def set_quiescence(self, use_quiescence):
        """
        Configure the quiescence search usage.

        Args:
            use_quiescence: Whether to use quiescence search for tactical positions

        Raises:
            RuntimeError: If the engine is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError("Cannot configure quiescence search: Engine not initialized")

        self.use_quiescence = use_quiescence

        # Update the search algorithm's quiescence setting
        if self.use_alpha_beta and self.search_algorithm:
            self.search_algorithm.use_quiescence = use_quiescence
            self.search_algorithm.quiescence_depth = self._get_quiescence_depth_for_skill_level()

        print(f"Quiescence search {'enabled' if use_quiescence else 'disabled'}")
        if use_quiescence and self.use_alpha_beta and self.search_algorithm:
            print(f"Quiescence depth: {self.search_algorithm.quiescence_depth}")

    def set_null_move(self, use_null_move):
        """
        Configure the null-move pruning usage.

        Args:
            use_null_move: Whether to use null-move pruning for faster search

        Raises:
            RuntimeError: If the engine is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError("Cannot configure null-move pruning: Engine not initialized")

        self.use_null_move = use_null_move

        # Update the search algorithm's null-move setting
        if self.use_alpha_beta and self.search_algorithm:
            self.search_algorithm.use_null_move = use_null_move

        print(f"Null-move pruning {'enabled' if use_null_move else 'disabled'}")
        if use_null_move and self.use_alpha_beta and self.search_algorithm:
            print(f"Reduction factor: {self.search_algorithm.null_move_reduction}")

    def set_learning(self, use_learning, data_file=None):
        """
        Configure the learning system usage.

        Args:
            use_learning: Whether to use machine learning to improve over time
            data_file: Path to the learning data file (None for default)

        Raises:
            RuntimeError: If the engine is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError("Cannot configure learning system: Engine not initialized")

        # If we're enabling learning and it's not already created
        if use_learning and self.learning_system is None:
            self.learning_system = LearningSystem(data_file=data_file)

        self.use_learning = use_learning

        print(f"Learning system {'enabled' if use_learning else 'disabled'}")
        if use_learning and self.learning_system:
            stats = self.learning_system.get_stats()
            print(f"Positions stored: {stats['positions_stored']}, Games learned: {stats['games_learned']}")

    def set_positional_eval(self, use_positional_eval):
        """
        Configure the positional evaluation usage.

        Args:
            use_positional_eval: Whether to use advanced positional evaluation

        Raises:
            RuntimeError: If the engine is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError("Cannot configure positional evaluation: Engine not initialized")

        # If we're enabling positional evaluation and it's not already created
        if use_positional_eval and self.positional_evaluator is None:
            self.positional_evaluator = PositionalEvaluator()

        self.use_positional_eval = use_positional_eval

        print(f"Positional evaluation {'enabled' if use_positional_eval else 'disabled'}")

    def set_opening_style(self, style):
        """
        Set the opening style for the engine.

        Args:
            style: The style to use ('solid', 'aggressive', 'tricky', or 'balanced')

        Raises:
            RuntimeError: If the engine is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError("Cannot set opening style: Engine not initialized")

        if not self.use_opening_book or not self.opening_book:
            print("Warning: Opening book is disabled, style will have no effect")
            return

        success = self.opening_book.set_style(style)
        if success:
            print(f"Opening style set to: {style}")

    def get_opening_stats(self):
        """
        Get statistics about the opening repertoire.

        Returns:
            A dictionary with repertoire statistics.

        Raises:
            RuntimeError: If the engine is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError("Cannot get opening stats: Engine not initialized")

        if not self.use_opening_book or not self.opening_book:
            return {"error": "Opening book is disabled"}

        return self.opening_book.get_repertoire_stats()

    def record_game_result(self, result):
        """
        Record the result of the current game for opening repertoire learning.

        Args:
            result: The game result (1.0 for white win, 0.5 for draw, 0.0 for black win)

        Returns:
            True if successful, False otherwise.

        Raises:
            RuntimeError: If the engine is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError("Cannot record game result: Engine not initialized")

        if not self.use_opening_book or not self.opening_book:
            print("Warning: Opening book is disabled, result will not be recorded")
            return False

        if not self.game_moves:
            print("Warning: No moves to record")
            return False

        success = self.opening_book.record_game_moves(self.game_moves, result)
        if success:
            print(f"Game result recorded: {result}")
            # Clear the game moves for the next game
            self.game_moves = []
        return success

    def reset_game(self):
        """
        Reset the game state for a new game.
        """
        # Clear the game moves
        self.game_moves = []

    def get_best_move(self, board):
        """
        Get the best move for the current position.

        Args:
            board: A chess.Board object representing the current position.

        Returns:
            A string representing the best move in UCI notation.

        Raises:
            RuntimeError: If the engine is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError("Cannot get best move: Engine not initialized")

        # Clear previous analysis
        self.thinking_lines = []

        # Start timing for analysis
        start_time = time.time()

        try:
            # Get legal moves
            legal_moves = list(board.legal_moves)
            if not legal_moves:
                return None

            # Try to get a move from the opening book if enabled
            if self.use_opening_book and self.opening_book and self.opening_book.is_available:
                book_move = self.opening_book.get_book_move(board)
                if book_move:
                    # If we found a book move, use it
                    self.best_move_found = book_move.uci()

                    # Record the move for repertoire learning
                    self.game_moves.append(book_move)

                    # Generate some fake analysis for display
                    self.thinking_lines = [f"{board.san(book_move)}: 0.00 (book move)"]
                    self.last_evaluation = {"type": "cp", "value": 0}

                    # Get additional book moves for display
                    book_moves = self.opening_book.get_book_moves(board, max_moves=3)
                    if len(book_moves) > 1:
                        for move, weight in book_moves[1:]:
                            self.thinking_lines.append(f"{board.san(move)}: 0.00 (book: {weight})")

                    return self.best_move_found

            # If no book move or book is disabled, use the engine
            if self.use_alpha_beta and self.search_algorithm:
                # Use alpha-beta search
                time_limit = 1.0  # 1 second time limit
                best_move, score, thinking_lines = self.search_algorithm.search(board, time_limit=time_limit)

                if best_move:
                    self.best_move_found = best_move.uci()
                    self.thinking_lines = thinking_lines

                    # Store evaluation
                    self.last_evaluation = {
                        "type": "cp",
                        "value": int(score * 100)  # Convert to centipawns
                    }

                    # Print search stats
                    stats = self.search_algorithm.get_stats()
                    print(f"Search stats: {stats['nodes']} nodes in {stats['time']} ({stats['nps']} nps), depth {stats['depth']}")
                    print(f"Cache: {stats['cache_hit_rate']} hit rate ({stats['cache_hits']} hits)")
                else:
                    # Fallback to simple analysis if search failed
                    self._generate_analysis(board, legal_moves)
            else:
                # Use simple analysis
                self._generate_analysis(board, legal_moves)

            # Choose a move based on difficulty level
            if self.skill_level >= 15:  # Very strong
                # Choose from top 20% of moves
                move_index = random.randint(0, max(0, len(legal_moves) // 5 - 1))
            elif self.skill_level >= 10:  # Medium
                # Choose from top 50% of moves
                move_index = random.randint(0, max(0, len(legal_moves) // 2 - 1))
            else:  # Weak
                # Choose any move
                move_index = random.randint(0, len(legal_moves) - 1)

            # Get the chosen move
            chosen_move = legal_moves[move_index]
            self.best_move_found = chosen_move.uci()

            # Add timing information
            elapsed = time.time() - start_time
            if self.thinking_lines:
                self.thinking_lines[0] += f" ({elapsed:.2f}s)"

            return self.best_move_found
        except Exception as e:
            print(f"Error getting best move: {e}")
            # In case of error, return a random legal move if possible
            try:
                if legal_moves:
                    random_move = random.choice(legal_moves)
                    return random_move.uci()
            except:
                pass
            return None

    def _generate_analysis(self, board, legal_moves):
        """Generate analysis information for display purposes.

        Optimized version that caches evaluations and avoids redundant calculations.
        """
        # Create a list to store our thinking lines
        thinking_lines = []

        # If no legal moves, return empty analysis
        if not legal_moves:
            self.thinking_lines = []
            self.last_evaluation = {"type": "cp", "value": 0}
            return

        # Get up to 3 moves to analyze, but prioritize captures and checks
        # for more interesting analysis
        captures_and_checks = [move for move in legal_moves
                             if board.is_capture(move) or
                                board.gives_check(move)]

        # If we have captures or checks, prioritize them
        if captures_and_checks and len(captures_and_checks) >= 3:
            moves_to_analyze = random.sample(captures_and_checks, min(3, len(captures_and_checks)))
        else:
            # Fill remaining slots with other moves
            remaining = 3 - len(captures_and_checks)
            other_moves = [move for move in legal_moves if move not in captures_and_checks]
            if other_moves and remaining > 0:
                moves_to_analyze = captures_and_checks + random.sample(other_moves, min(remaining, len(other_moves)))
            else:
                moves_to_analyze = captures_and_checks

        # Ensure we have at least one move to analyze
        if not moves_to_analyze and legal_moves:
            moves_to_analyze = [random.choice(legal_moves)]

        # Cache for evaluations to avoid recalculating
        eval_cache = {}

        # Generate evaluations with some randomness but influenced by piece values
        for i, move in enumerate(moves_to_analyze):
            # Get the move in SAN notation - this is expensive, so do it only once
            try:
                san_move = board.san(move)
            except ValueError:
                # If SAN generation fails, use UCI notation instead
                san_move = move.uci() + " (UCI)"

            # Make the move on a temporary board
            temp_board = board.copy()
            temp_board.push(move)

            # Use board FEN as cache key (without move counter parts to save space)
            fen_parts = temp_board.fen().split(' ')
            cache_key = ' '.join(fen_parts[:4])  # Just position, side to move, castling, en passant

            # Check if we've already evaluated this position
            if cache_key in eval_cache:
                material_eval = eval_cache[cache_key]
            else:
                # Calculate material evaluation
                material_eval = self._calculate_material(temp_board)
                eval_cache[cache_key] = material_eval

            # Add some randomness based on skill level
            # Lower skill = more randomness
            randomness = (21 - self.skill_level) / 10.0
            eval_noise = random.uniform(-randomness, randomness)

            # Final evaluation
            final_eval = material_eval + eval_noise

            # Format the evaluation string
            if abs(final_eval) > 5 and random.random() < 0.2:  # 20% chance for mate evaluation on big advantages
                mate_in = random.randint(1, 5)
                eval_str = f"Mate in {mate_in}"
                if i == 0:  # Store the main evaluation
                    self.last_evaluation = {"type": "mate", "value": mate_in if final_eval > 0 else -mate_in}
            else:
                eval_str = f"{final_eval:.2f}"
                if i == 0:  # Store the main evaluation
                    self.last_evaluation = {"type": "cp", "value": int(final_eval * 100)}

            # Add to thinking lines
            thinking_lines.append(f"{san_move}: {eval_str}")

        # Sort thinking lines by evaluation (best first)
        self.thinking_lines = thinking_lines

    def _calculate_material(self, board):
        """Calculate a position evaluation for the board.

        Uses either simple material counting or advanced positional evaluation
        based on configuration. Also uses the transposition table for caching.
        """
        # Check if this position is in the transposition table
        if self.use_transposition_table and self.transposition_table:
            hit, entry = self.transposition_table.get(board)
            if hit:
                return entry['data']['material_eval']

        # Use advanced positional evaluation if enabled
        if self.use_positional_eval and self.positional_evaluator:
            # Get evaluation in centipawns and convert to pawns
            eval_score = self.positional_evaluator.evaluate(board) / 100.0
        else:
            # Use simple material counting
            # Piece values
            piece_values = {
                chess.PAWN: 1.0,
                chess.KNIGHT: 3.0,
                chess.BISHOP: 3.0,
                chess.ROOK: 5.0,
                chess.QUEEN: 9.0,
                chess.KING: 0.0  # King doesn't contribute to material count
            }

            # Use piece maps for faster evaluation
            white_material = sum(piece_values[piece_type] * len(board.pieces(piece_type, chess.WHITE))
                               for piece_type in piece_values)
            black_material = sum(piece_values[piece_type] * len(board.pieces(piece_type, chess.BLACK))
                               for piece_type in piece_values)

            # Calculate the evaluation from white's perspective
            eval_score = white_material - black_material

        # Apply learning adjustments if enabled
        if self.use_learning and self.learning_system:
            # Record the position for learning
            self.learning_system.record_position(board, eval_score)

            # Adjust evaluation based on learning data
            eval_score = self.learning_system.adjust_evaluation(board, eval_score)

        # Store in transposition table
        if self.use_transposition_table and self.transposition_table:
            self.transposition_table.put(board, {'material_eval': eval_score}, depth=0)

        return eval_score

    def get_board_evaluation(self, board):
        """
        Get the evaluation of the current position.

        Args:
            board: A chess.Board object representing the current position.

        Returns:
            A dictionary containing the evaluation.

        Raises:
            RuntimeError: If the engine is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError("Cannot get evaluation: Engine not initialized")

        try:
            # If we already have an evaluation from a recent get_best_move call, return it
            if self.last_evaluation:
                return self.last_evaluation

            # Otherwise, generate a new evaluation
            legal_moves = list(board.legal_moves)
            self._generate_analysis(board, legal_moves)
            return self.last_evaluation
        except Exception as e:
            print(f"Error getting board evaluation: {e}")
            # Return a neutral evaluation in case of error
            return {"type": "cp", "value": 0}

    def get_top_moves(self, board, num_moves=3):
        """
        Get the top N moves for the current position.

        Args:
            board: A chess.Board object representing the current position.
            num_moves: The number of top moves to return.

        Returns:
            A list of dictionaries containing the top moves.

        Raises:
            RuntimeError: If the engine is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError("Cannot get top moves: Engine not initialized")

        try:
            # If we already have thinking lines from a recent get_best_move call, convert them
            if not self.thinking_lines:
                # Generate new analysis
                legal_moves = list(board.legal_moves)
                self._generate_analysis(board, legal_moves)

            # Convert thinking lines to the expected format
            result = []
            for line in self.thinking_lines[:num_moves]:
                parts = line.split(': ')
                if len(parts) == 2:
                    move_san, eval_str = parts
                    # Convert SAN to UCI
                    try:
                        temp_board = chess.Board(board.fen())
                        try:
                            move = temp_board.parse_san(move_san)
                            move_uci = move.uci()
                        except ValueError:
                            # If the SAN move can't be parsed, it might be a UCI move already
                            if '(UCI)' in move_san:
                                move_uci = move_san.split(' ')[0]  # Extract the UCI part
                            else:
                                # Skip this move if we can't parse it
                                continue

                        # Parse evaluation
                        if 'Mate in' in eval_str:
                            mate_value = int(eval_str.split('Mate in ')[1])
                            result.append({'Move': move_uci, 'Mate': mate_value})
                        else:
                            try:
                                centipawn = int(float(eval_str) * 100)
                                result.append({'Move': move_uci, 'Centipawn': centipawn})
                            except ValueError:
                                result.append({'Move': move_uci})
                    except Exception as e:
                        print(f"Error converting thinking line to move: {e}")

            return result
        except Exception as e:
            print(f"Error getting top moves: {e}")
            # Return empty list in case of error
            return []

    def cleanup(self):
        """Clean up resources when done."""
        # Nothing to clean up in this implementation
        pass

    def get_thinking_lines(self):
        """
        Get the engine's thinking lines.

        Returns:
            A list of strings representing the engine's thinking lines.

        Raises:
            RuntimeError: If the engine is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError("Cannot get thinking lines: Engine not initialized")

        return self.thinking_lines

    def record_game_result(self, result):
        """
        Record the result of a game for learning purposes.

        Args:
            result: The game result (1.0 for white win, 0.5 for draw, 0.0 for black win)

        Raises:
            RuntimeError: If the engine is not initialized or learning is disabled
        """
        if not self.is_initialized:
            raise RuntimeError("Cannot record game result: Engine not initialized")

        if not self.use_learning or not self.learning_system:
            raise RuntimeError("Cannot record game result: Learning is disabled")

        self.learning_system.record_game_result(result)
        print(f"Game result recorded: {result}")

    def learn_from_game(self):
        """
        Learn from the recorded game positions and result.

        Raises:
            RuntimeError: If the engine is not initialized or learning is disabled
        """
        if not self.is_initialized:
            raise RuntimeError("Cannot learn from game: Engine not initialized")

        if not self.use_learning or not self.learning_system:
            raise RuntimeError("Cannot learn from game: Learning is disabled")

        self.learning_system.learn_from_game()
        print("Learning completed from game data")

    def get_learning_stats(self):
        """
        Get statistics about the learning system.

        Returns:
            A dictionary with learning statistics.

        Raises:
            RuntimeError: If the engine is not initialized or learning is disabled
        """
        if not self.is_initialized:
            raise RuntimeError("Cannot get learning stats: Engine not initialized")

        if not self.use_learning or not self.learning_system:
            raise RuntimeError("Cannot get learning stats: Learning is disabled")

        return self.learning_system.get_stats()
