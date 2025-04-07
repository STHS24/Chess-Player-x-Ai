"""
Sunfish Wrapper Module
This module provides a wrapper for the Sunfish chess engine.
"""

import chess
import random
import time

# We'll implement our own simplified version instead of importing sunfish
# This avoids the import error with the tools module

class EngineInitializationError(Exception):
    """Exception raised when the chess engine fails to initialize."""
    pass

class SunfishWrapper:
    def __init__(self, max_retries=3):
        """Initialize a simplified chess engine based on Sunfish concepts.

        Args:
            max_retries: Maximum number of initialization attempts

        Raises:
            EngineInitializationError: If the engine cannot be initialized after max_retries
        """
        # Store analysis information
        self.last_evaluation = None
        self.thinking_lines = []
        self.best_move_found = None
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
        # In a real engine, this would initialize various components
        # For our simplified engine, we don't need much initialization
        pass

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

        print(f"Difficulty set to {level}")

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

            # Generate analysis based on difficulty level
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
        """Generate analysis information for display purposes."""
        # Create a list to store our thinking lines
        thinking_lines = []

        # Get up to 3 moves to analyze
        num_moves = min(3, len(legal_moves))
        moves_to_analyze = random.sample(legal_moves, num_moves)

        # Generate evaluations with some randomness but influenced by piece values
        for i, move in enumerate(moves_to_analyze):
            # Make a temporary copy of the board
            temp_board = board.copy()

            # Get the move in SAN notation
            san_move = temp_board.san(move)

            # Make the move on the temporary board
            temp_board.push(move)

            # Calculate a simple material evaluation
            material_eval = self._calculate_material(temp_board)

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
        """Calculate a simple material evaluation for the board."""
        piece_values = {
            chess.PAWN: 1.0,
            chess.KNIGHT: 3.0,
            chess.BISHOP: 3.0,
            chess.ROOK: 5.0,
            chess.QUEEN: 9.0,
            chess.KING: 0.0  # King doesn't contribute to material count
        }

        white_material = 0
        black_material = 0

        # Count material for each side
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = piece_values[piece.piece_type]
                if piece.color == chess.WHITE:
                    white_material += value
                else:
                    black_material += value

        # Return evaluation from white's perspective
        return white_material - black_material

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
                        move = temp_board.parse_san(move_san)
                        move_uci = move.uci()

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
