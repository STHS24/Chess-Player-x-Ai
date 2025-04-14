"""
Search Module
This module provides optimized search algorithms for the chess engine.
"""

import chess
import time
from chess_ai.engine.transposition_table import TranspositionTable

class SearchAlgorithm:
    """
    Class implementing advanced search algorithms for chess position evaluation.
    """

    def __init__(self, evaluator, transposition_table=None, max_depth=3, use_quiescence=True, quiescence_depth=3, use_null_move=True):
        """
        Initialize the search algorithm.

        Args:
            evaluator: A function that evaluates a position and returns a score
            transposition_table: Optional TranspositionTable for caching positions
            max_depth: Maximum search depth
            use_quiescence: Whether to use quiescence search for tactical positions
            quiescence_depth: Maximum depth for quiescence search
            use_null_move: Whether to use null-move pruning for faster search
        """
        self.evaluator = evaluator
        self.transposition_table = transposition_table
        self.max_depth = max_depth
        self.use_quiescence = use_quiescence
        self.quiescence_depth = quiescence_depth
        self.use_null_move = use_null_move
        self.null_move_reduction = 2  # Reduction factor for null-move pruning (R value)
        self.nodes_searched = 0
        self.q_nodes_searched = 0  # Nodes searched in quiescence search
        self.null_move_cutoffs = 0  # Count of null-move pruning cutoffs
        self.positions_cached = 0
        self.cache_hits = 0
        self.start_time = 0
        self.time_limit = 0
        self.best_move = None
        self.best_score = 0
        self.thinking_lines = []

    def reset_stats(self):
        """Reset search statistics."""
        self.nodes_searched = 0
        self.q_nodes_searched = 0
        self.null_move_cutoffs = 0
        self.positions_cached = 0
        self.cache_hits = 0

    def set_time_limit(self, seconds):
        """Set a time limit for the search."""
        self.time_limit = seconds

    def is_time_up(self):
        """Check if the search time limit has been reached."""
        if self.time_limit <= 0:
            return False
        return time.time() - self.start_time >= self.time_limit

    def search(self, board, depth=None, time_limit=None):
        """
        Search for the best move using iterative deepening and alpha-beta pruning.

        Args:
            board: A chess.Board object
            depth: Maximum search depth (overrides self.max_depth if provided)
            time_limit: Time limit in seconds (overrides self.time_limit if provided)

        Returns:
            A tuple (best_move, score, thinking_lines)
        """
        if depth is not None:
            self.max_depth = depth

        if time_limit is not None:
            self.time_limit = time_limit

        self.reset_stats()
        self.start_time = time.time()
        self.thinking_lines = []

        # Use iterative deepening
        for current_depth in range(1, self.max_depth + 1):
            if self.is_time_up():
                break

            # Search with alpha-beta pruning
            score = self.alpha_beta(board, current_depth, float('-inf'), float('inf'), True)

            # Store the best move and score at this depth
            if not self.is_time_up():
                self.best_score = score

                # Add thinking line for this depth
                if self.best_move:
                    try:
                        move_san = board.san(self.best_move)
                        self.thinking_lines.append(f"depth {current_depth}: {move_san} ({score:.2f})")
                    except ValueError:
                        # If SAN generation fails, use UCI notation
                        self.thinking_lines.append(f"depth {current_depth}: {self.best_move.uci()} ({score:.2f})")

        # Return the best move found, its score, and thinking lines
        return self.best_move, self.best_score, self.thinking_lines

    def alpha_beta(self, board, depth, alpha, beta, maximizing_player):
        """
        Alpha-beta pruning search algorithm.

        Args:
            board: A chess.Board object
            depth: Current search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            maximizing_player: Whether the current player is maximizing

        Returns:
            The evaluation score for the position
        """
        # Increment nodes searched counter
        self.nodes_searched += 1

        # Check if we should stop the search due to time limit
        if self.is_time_up():
            return 0

        # Check transposition table
        if self.transposition_table:
            hit, entry = self.transposition_table.get(board, depth)
            if hit:
                self.cache_hits += 1
                return entry['data']['score']

        # Base case: leaf node or terminal position
        if board.is_game_over():
            # Handle checkmate, stalemate, etc.
            if board.is_checkmate():
                # Return a high value for checkmate, adjusted by depth to prefer quicker mates
                return -10000 + (self.max_depth - depth) if board.turn == maximizing_player else 10000 - (self.max_depth - depth)
            else:
                # Draw (stalemate, insufficient material, etc.)
                return 0

        # If we've reached the depth limit, use quiescence search if enabled
        if depth <= 0:
            if self.use_quiescence:
                return self.quiescence_search(board, alpha, beta, maximizing_player, self.quiescence_depth)
            else:
                # Evaluate the position
                score = self.evaluator(board)
                # Adjust score based on perspective
                return score if board.turn == chess.WHITE else -score

        # Try null-move pruning if enabled and appropriate
        if self.use_null_move and depth >= 2 and not self.is_endgame(board) and not board.is_check():
            # Skip the current player's turn (make a "null move")
            board.push(chess.Move.null())

            # Search with reduced depth (R=2 or R=3 typically)
            null_score = -self.alpha_beta(board, depth - 1 - self.null_move_reduction, -beta, -beta + 1, not maximizing_player)

            # Undo the null move
            board.pop()

            # If the score is good enough, we can prune this branch
            if null_score >= beta and not self.is_time_up():
                self.null_move_cutoffs += 1
                return beta

        # Get legal moves and sort them for better pruning
        legal_moves = list(board.legal_moves)
        ordered_moves = self.order_moves(board, legal_moves)

        if maximizing_player:
            best_score = float('-inf')
            for move in ordered_moves:
                # Make the move
                board.push(move)

                # Recursively evaluate the position
                score = self.alpha_beta(board, depth - 1, alpha, beta, False)

                # Undo the move
                board.pop()

                # Update best score and alpha
                if score > best_score:
                    best_score = score
                    if depth == self.max_depth:
                        self.best_move = move

                alpha = max(alpha, best_score)

                # Alpha-beta pruning
                if beta <= alpha:
                    break

                # Check time limit
                if self.is_time_up():
                    break

            # Store in transposition table
            if self.transposition_table and not self.is_time_up():
                self.transposition_table.put(board, {'score': best_score}, depth)
                self.positions_cached += 1

            return best_score
        else:
            best_score = float('inf')
            for move in ordered_moves:
                # Make the move
                board.push(move)

                # Recursively evaluate the position
                score = self.alpha_beta(board, depth - 1, alpha, beta, True)

                # Undo the move
                board.pop()

                # Update best score and beta
                if score < best_score:
                    best_score = score
                    if depth == self.max_depth:
                        self.best_move = move

                beta = min(beta, best_score)

                # Alpha-beta pruning
                if beta <= alpha:
                    break

                # Check time limit
                if self.is_time_up():
                    break

            # Store in transposition table
            if self.transposition_table and not self.is_time_up():
                self.transposition_table.put(board, {'score': best_score}, depth)
                self.positions_cached += 1

            return best_score

    def order_moves(self, board, moves):
        """
        Order moves to improve alpha-beta pruning efficiency.
        Captures, checks, and promotions are examined first.

        Args:
            board: A chess.Board object
            moves: List of legal moves

        Returns:
            Ordered list of moves
        """
        # Score each move for ordering
        move_scores = []

        for move in moves:
            score = 0

            # Prioritize captures by MVV-LVA (Most Valuable Victim - Least Valuable Aggressor)
            if board.is_capture(move):
                victim_value = self.get_piece_value(board.piece_at(move.to_square))
                aggressor_value = self.get_piece_value(board.piece_at(move.from_square))
                score += 10 * victim_value - aggressor_value

            # Prioritize promotions
            if move.promotion:
                score += 900  # Queen promotion value

            # Prioritize checks
            board.push(move)
            if board.is_check():
                score += 50
            board.pop()

            # Add a small random factor to avoid deterministic behavior
            score += 0.01 * hash(move.uci()) % 100

            move_scores.append((move, score))

        # Sort moves by score (descending)
        move_scores.sort(key=lambda x: x[1], reverse=True)

        # Return ordered moves
        return [move for move, _ in move_scores]

    def get_piece_value(self, piece):
        """
        Get the value of a piece for move ordering.

        Args:
            piece: A chess.Piece object or None

        Returns:
            The value of the piece
        """
        if piece is None:
            return 0

        # Piece values for move ordering
        values = {
            chess.PAWN: 10,
            chess.KNIGHT: 30,
            chess.BISHOP: 30,
            chess.ROOK: 50,
            chess.QUEEN: 90,
            chess.KING: 900
        }

        return values.get(piece.piece_type, 0)

    def quiescence_search(self, board, alpha, beta, maximizing_player, depth):
        """
        Quiescence search to evaluate tactical positions more accurately.
        Only considers captures and checks to reach a "quiet" position.

        Args:
            board: A chess.Board object
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            maximizing_player: Whether the current player is maximizing
            depth: Maximum quiescence search depth

        Returns:
            The evaluation score for the position
        """
        # Increment quiescence nodes searched counter
        self.q_nodes_searched += 1

        # Check if we should stop the search due to time limit
        if self.is_time_up():
            return 0

        # Stand pat: Evaluate the current position
        stand_pat = self.evaluator(board)
        stand_pat = stand_pat if board.turn == chess.WHITE else -stand_pat

        # Beta cutoff
        if stand_pat >= beta:
            return beta

        # Update alpha if stand pat is better
        if stand_pat > alpha:
            alpha = stand_pat

        # Base case: maximum quiescence depth reached
        if depth <= 0:
            return stand_pat

        # Get only captures and checks for quiescence search
        tactical_moves = self.get_tactical_moves(board)

        # If no tactical moves, return stand pat evaluation
        if not tactical_moves:
            return stand_pat

        # Order moves for better pruning
        ordered_moves = self.order_moves(board, tactical_moves)

        # Search tactical moves
        for move in ordered_moves:
            # Make the move
            board.push(move)

            # Recursively evaluate the position
            score = -self.quiescence_search(board, -beta, -alpha, not maximizing_player, depth - 1)

            # Undo the move
            board.pop()

            # Beta cutoff
            if score >= beta:
                return beta

            # Update alpha if score is better
            if score > alpha:
                alpha = score

        return alpha

    def get_tactical_moves(self, board):
        """
        Get tactical moves (captures and checks) for quiescence search.

        Args:
            board: A chess.Board object

        Returns:
            A list of tactical moves
        """
        tactical_moves = []

        for move in board.legal_moves:
            # Include captures
            if board.is_capture(move):
                tactical_moves.append(move)
                continue

            # Include checks (more expensive to calculate, so do it last)
            board.push(move)
            gives_check = board.is_check()
            board.pop()

            if gives_check:
                tactical_moves.append(move)

        return tactical_moves

    def is_endgame(self, board):
        """
        Determine if the position is an endgame position.
        Null-move pruning is less effective in endgames, so we disable it.

        Args:
            board: A chess.Board object

        Returns:
            True if the position is an endgame, False otherwise
        """
        # Count the number of non-pawn pieces for each side
        white_pieces = 0
        black_pieces = 0

        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type != chess.PAWN:
                if piece.color == chess.WHITE:
                    white_pieces += 1
                else:
                    black_pieces += 1

        # Consider it an endgame if either side has <= 2 non-pawn pieces
        return white_pieces <= 2 or black_pieces <= 2

    def get_stats(self):
        """
        Get statistics about the search.

        Returns:
            A dictionary with search statistics
        """
        elapsed = time.time() - self.start_time
        total_nodes = self.nodes_searched + self.q_nodes_searched

        return {
            'nodes': self.nodes_searched,
            'q_nodes': self.q_nodes_searched,
            'total_nodes': total_nodes,
            'null_move_cutoffs': self.null_move_cutoffs,
            'time': f"{elapsed:.2f}s",
            'nps': int(total_nodes / elapsed) if elapsed > 0 else 0,
            'depth': self.max_depth,
            'q_depth': self.quiescence_depth,
            'cache_hits': self.cache_hits,
            'positions_cached': self.positions_cached,
            'cache_hit_rate': f"{(self.cache_hits / total_nodes * 100):.1f}%" if total_nodes > 0 else "0%",
            'quiescence': "enabled" if self.use_quiescence else "disabled",
            'null_move': "enabled" if self.use_null_move else "disabled"
        }
