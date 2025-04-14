"""
Opening Book Module
This module provides support for Polyglot opening books in chess.
"""

import chess
import chess.polyglot
import random
import os
from pathlib import Path

class OpeningBook:
    """Class for handling chess opening books in Polyglot format."""

    def __init__(self, book_path=None, repertoire_file=None):
        """
        Initialize the opening book.

        Args:
            book_path: Path to the Polyglot opening book file (.bin)
                       If None, will try to use a default book if available.
            repertoire_file: Path to the repertoire data file (.json)
                            If None, will try to use a default file if available.
        """
        self.book_path = book_path
        self.is_available = False

        # Try to find a default book if none is specified
        if self.book_path is None:
            # Look in common locations
            possible_paths = [
                "books/book.bin",  # Local to the application
                "chess_ai/books/book.bin",  # Within the package
                os.path.join(os.path.dirname(__file__), "../books/book.bin"),  # Relative to this file
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    self.book_path = path
                    break

        # Check if the book exists
        if self.book_path and os.path.exists(self.book_path):
            self.is_available = True

        # Initialize repertoire data
        self.repertoire_file = repertoire_file or os.path.join(os.path.dirname(__file__), "../data/repertoire.json")
        self.repertoire_data = self._load_repertoire()

        # Initialize opening traps
        self.traps = self._initialize_traps()

        # Opening style (can be 'solid', 'aggressive', 'tricky', or 'balanced')
        self.style = 'balanced'

        # Success tracking
        self.total_games = 0
        self.successful_games = 0

    def get_book_move(self, board, weight_by_score=True, min_weight=10):
        """
        Get a move from the opening book.

        Args:
            board: A chess.Board object representing the current position.
            weight_by_score: Whether to weight moves by their score in the book.
            min_weight: Minimum weight for a move to be considered.

        Returns:
            A chess.Move object, or None if no book move is available.
        """
        # First check for trap moves
        trap_move = self.get_trap_move(board)
        if trap_move:
            return trap_move

        if not self.is_available:
            return None

        try:
            # Get all entries from the book for this position
            entries = list(chess.polyglot.MemoryMappedReader(self.book_path).find_all(board))

            # Filter entries by minimum weight
            entries = [entry for entry in entries if entry.weight >= min_weight]

            if not entries:
                return None

            # Apply style preferences to adjust weights
            entries = self._apply_style_weights(board, entries)

            # Apply repertoire learning to adjust weights
            entries = self._apply_repertoire_weights(board, entries)

            if weight_by_score:
                # Calculate total weight
                total_weight = sum(entry.weight for entry in entries)

                # Choose a move based on weight
                choice = random.randint(1, total_weight)
                current_sum = 0

                for entry in entries:
                    current_sum += entry.weight
                    if current_sum >= choice:
                        return entry.move
            else:
                # Choose a random move from the available entries
                entry = random.choice(entries)
                return entry.move

        except Exception as e:
            print(f"Error accessing opening book: {e}")
            return None

    def _apply_style_weights(self, board, entries):
        """
        Adjust move weights based on the current style preference.

        Args:
            board: A chess.Board object representing the current position.
            entries: A list of book entries.

        Returns:
            A list of entries with adjusted weights.
        """
        # Get the style preferences for this position
        fen = board.fen().split(' ')[0]  # Just the piece positions
        style_prefs = self.repertoire_data["styles"].get(self.style, {})

        # Create a copy of entries to modify
        adjusted_entries = []

        for entry in entries:
            # Create a copy of the entry with a mutable weight
            adjusted_entry = chess.polyglot.Entry(
                key=entry.key,
                move=entry.move,
                weight=entry.weight,
                learn=entry.learn
            )

            # Check if this move has a style preference
            move_uci = entry.move.uci()
            position_key = f"{fen}:{move_uci}"

            if position_key in style_prefs:
                # Adjust weight based on style preference (0.5 to 2.0 multiplier)
                style_factor = style_prefs[position_key]
                adjusted_entry.weight = int(adjusted_entry.weight * style_factor)

            # Apply general style adjustments
            if self.style == 'aggressive':
                # Favor captures and checks
                board_copy = board.copy()
                board_copy.push(entry.move)
                if board_copy.is_capture(entry.move) or board_copy.is_check():
                    adjusted_entry.weight = int(adjusted_entry.weight * 1.5)

            elif self.style == 'solid':
                # Favor moves that don't lose material
                board_copy = board.copy()
                board_copy.push(entry.move)
                if not board_copy.is_capture(entry.move):
                    adjusted_entry.weight = int(adjusted_entry.weight * 1.3)

            # Add to adjusted entries
            adjusted_entries.append(adjusted_entry)

        return adjusted_entries

    def _apply_repertoire_weights(self, board, entries):
        """
        Adjust move weights based on learned repertoire success.

        Args:
            board: A chess.Board object representing the current position.
            entries: A list of book entries.

        Returns:
            A list of entries with adjusted weights.
        """
        # Get the repertoire data for this position
        fen = board.fen().split(' ')[0]  # Just the piece positions
        openings_data = self.repertoire_data["openings"]

        # Create a copy of entries to modify
        adjusted_entries = []

        for entry in entries:
            # Create a copy of the entry with a mutable weight
            adjusted_entry = chess.polyglot.Entry(
                key=entry.key,
                move=entry.move,
                weight=entry.weight,
                learn=entry.learn
            )

            # Check if this move has repertoire data
            move_uci = entry.move.uci()
            position_key = f"{fen}:{move_uci}"

            if position_key in openings_data:
                # Get success rate data
                move_data = openings_data[position_key]
                games_played = move_data.get("games", 0)
                success_rate = move_data.get("success_rate", 0.5)

                if games_played > 0:
                    # Adjust weight based on success rate
                    # 0% success = 0.5x weight, 50% success = 1x weight, 100% success = 2x weight
                    success_factor = 0.5 + success_rate * 1.5
                    confidence = min(1.0, games_played / 10.0)  # More games = more confidence

                    # Apply the adjustment with confidence factor
                    weight_adjustment = 1.0 + (success_factor - 1.0) * confidence
                    adjusted_entry.weight = int(adjusted_entry.weight * weight_adjustment)

            # Add to adjusted entries
            adjusted_entries.append(adjusted_entry)

        return adjusted_entries

    def get_book_moves(self, board, max_moves=3):
        """
        Get multiple moves from the opening book.

        Args:
            board: A chess.Board object representing the current position.
            max_moves: Maximum number of moves to return.

        Returns:
            A list of (move, weight) tuples, or an empty list if no book moves are available.
        """
        if not self.is_available:
            return []

        try:
            # Get all entries from the book for this position
            entries = list(chess.polyglot.MemoryMappedReader(self.book_path).find_all(board))

            # Apply style and repertoire weights
            entries = self._apply_style_weights(board, entries)
            entries = self._apply_repertoire_weights(board, entries)

            # Sort by weight (highest first)
            entries.sort(key=lambda entry: entry.weight, reverse=True)

            # Return the top moves
            return [(entry.move, entry.weight) for entry in entries[:max_moves]]

        except Exception as e:
            print(f"Error accessing opening book: {e}")
            return []

    def set_style(self, style):
        """
        Set the opening style.

        Args:
            style: The style to use ('solid', 'aggressive', 'tricky', or 'balanced')

        Returns:
            True if successful, False otherwise.
        """
        valid_styles = ['solid', 'aggressive', 'tricky', 'balanced']

        if style not in valid_styles:
            print(f"Invalid style: {style}. Valid styles are: {', '.join(valid_styles)}")
            return False

        self.style = style
        print(f"Opening style set to: {style}")
        return True

    def record_game_moves(self, moves, result):
        """
        Record the moves played in a game and their outcome.

        Args:
            moves: A list of chess.Move objects played in the game
            result: The game result (1.0 for white win, 0.5 for draw, 0.0 for black win)

        Returns:
            True if successful, False otherwise.
        """
        if not moves:
            return False

        try:
            # Create a board to replay the moves
            board = chess.Board()

            # Track which moves were from the opening book
            book_moves = []

            # Replay the first 15 moves (30 plies) or fewer if the game was shorter
            for i, move in enumerate(moves[:30]):
                # Check if this move is in our opening book
                if self.is_in_book(board):
                    # Record this position and move
                    fen = board.fen().split(' ')[0]  # Just the piece positions
                    move_uci = move.uci()
                    position_key = f"{fen}:{move_uci}"

                    # Store the move and position
                    book_moves.append({
                        "position": fen,
                        "move": move_uci,
                        "position_key": position_key,
                        "ply": i
                    })

                # Make the move on the board
                board.push(move)

                # Stop if we've left the opening
                if i >= 10 and not self.is_in_book(board):
                    break

            # Update repertoire data with the results
            self._update_repertoire(book_moves, result)

            # Update success tracking
            self.total_games += 1
            if (result == 1.0 and len(moves) % 2 == 0) or (result == 0.0 and len(moves) % 2 == 1):
                # Engine won (engine played as white and white won, or engine played as black and black won)
                self.successful_games += 1

            # Save the updated repertoire
            self._save_repertoire()

            return True

        except Exception as e:
            print(f"Error recording game moves: {e}")
            return False

    def _update_repertoire(self, book_moves, result):
        """
        Update the repertoire data with the results of a game.

        Args:
            book_moves: A list of dictionaries with position and move information
            result: The game result (1.0 for white win, 0.5 for draw, 0.0 for black win)
        """
        if not book_moves:
            return

        # Process each book move
        for move_data in book_moves:
            position_key = move_data["position_key"]
            ply = move_data["ply"]

            # Determine if this move was successful based on who played it and the result
            player_is_white = (ply % 2 == 0)  # Even ply means white's move

            # Calculate success value (1.0 = success, 0.5 = draw, 0.0 = failure)
            if player_is_white:
                success_value = result  # White's success is directly the result
            else:
                success_value = 1.0 - result  # Black's success is the inverse of the result

            # Update openings data
            if position_key not in self.repertoire_data["openings"]:
                self.repertoire_data["openings"][position_key] = {
                    "games": 0,
                    "wins": 0,
                    "draws": 0,
                    "losses": 0,
                    "success_rate": 0.5
                }

            # Update statistics
            move_stats = self.repertoire_data["openings"][position_key]
            move_stats["games"] += 1

            if success_value == 1.0:
                move_stats["wins"] += 1
            elif success_value == 0.5:
                move_stats["draws"] += 1
            else:
                move_stats["losses"] += 1

            # Recalculate success rate
            total_games = move_stats["games"]
            if total_games > 0:
                move_stats["success_rate"] = (move_stats["wins"] + 0.5 * move_stats["draws"]) / total_games

            # Update style data based on success
            self._update_style_data(position_key, success_value)

    def _update_style_data(self, position_key, success_value):
        """
        Update the style data based on move success.

        Args:
            position_key: The position and move key
            success_value: The success value (1.0 = success, 0.5 = draw, 0.0 = failure)
        """
        # Determine which style this move belongs to
        current_style = self.style

        # Update the style data
        if position_key not in self.repertoire_data["styles"][current_style]:
            # Initialize with neutral weight
            self.repertoire_data["styles"][current_style][position_key] = 1.0

        # Get current weight
        current_weight = self.repertoire_data["styles"][current_style][position_key]

        # Adjust weight based on success (small adjustments to avoid wild swings)
        if success_value == 1.0:  # Win
            # Increase weight (max 2.0)
            new_weight = min(2.0, current_weight + 0.1)
        elif success_value == 0.0:  # Loss
            # Decrease weight (min 0.5)
            new_weight = max(0.5, current_weight - 0.1)
        else:  # Draw
            # Slight increase (neutral to positive)
            new_weight = min(2.0, current_weight + 0.05)

        # Update the weight
        self.repertoire_data["styles"][current_style][position_key] = new_weight

    def get_repertoire_stats(self):
        """
        Get statistics about the opening repertoire.

        Returns:
            A dictionary with repertoire statistics.
        """
        stats = {
            "total_positions": len(self.repertoire_data["openings"]),
            "total_games": self.total_games,
            "success_rate": 0.0,
            "style": self.style,
            "styles": {}
        }

        # Calculate overall success rate
        if self.total_games > 0:
            stats["success_rate"] = self.successful_games / self.total_games

        # Count positions by style
        for style, positions in self.repertoire_data["styles"].items():
            stats["styles"][style] = len(positions)

        return stats

    def is_in_book(self, board):
        """
        Check if the current position is in the opening book.

        Args:
            board: A chess.Board object representing the current position.

        Returns:
            True if the position is in the book, False otherwise.
        """
        if not self.is_available:
            return False

        try:
            # Try to find at least one entry
            reader = chess.polyglot.MemoryMappedReader(self.book_path)
            for _ in reader.find_all(board):
                return True
            return False

        except Exception as e:
            print(f"Error accessing opening book: {e}")
            return False

    def _load_repertoire(self):
        """
        Load repertoire data from file.

        Returns:
            A dictionary containing repertoire data.
        """
        import json

        # Default empty repertoire structure
        default_repertoire = {
            "openings": {},  # Maps FEN positions to move success rates
            "styles": {
                "solid": {},     # Conservative, positional openings
                "aggressive": {}, # Attacking, tactical openings
                "tricky": {},    # Unusual, surprising openings
                "balanced": {}    # Standard, well-rounded openings
            },
            "metadata": {
                "last_updated": "",
                "total_games": 0
            }
        }

        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.repertoire_file), exist_ok=True)

            # Try to load existing data
            if os.path.exists(self.repertoire_file):
                with open(self.repertoire_file, 'r') as f:
                    return json.load(f)
            else:
                # Create a new file with default structure
                with open(self.repertoire_file, 'w') as f:
                    json.dump(default_repertoire, f, indent=2)
                return default_repertoire

        except Exception as e:
            print(f"Error loading repertoire data: {e}")
            return default_repertoire

    def _save_repertoire(self):
        """
        Save repertoire data to file.

        Returns:
            True if successful, False otherwise.
        """
        import json
        import datetime

        try:
            # Update metadata
            self.repertoire_data["metadata"]["last_updated"] = datetime.datetime.now().isoformat()
            self.repertoire_data["metadata"]["total_games"] = self.total_games

            # Save to file
            with open(self.repertoire_file, 'w') as f:
                json.dump(self.repertoire_data, f, indent=2)
            return True

        except Exception as e:
            print(f"Error saving repertoire data: {e}")
            return False

    def _initialize_traps(self):
        """
        Initialize opening traps.

        Returns:
            A dictionary of opening traps.
        """
        # Format: {"trap_name": {"fen": "...", "move": "...", "description": "..."}}
        traps = {
            "Stafford Gambit": {
                "fen": "r1bqkbnr/ppp2ppp/2n5/3p4/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 4",
                "move": "e4d5",
                "description": "Stafford Gambit trap after 1.e4 e5 2.Nf3 Nf6 3.Nxe5 Nc6"
            },
            "Fried Liver Attack": {
                "fen": "r1bqkb1r/ppp2ppp/2n5/3np3/2B5/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 5",
                "move": "f3g5",
                "description": "Fried Liver Attack after 1.e4 e5 2.Nf3 Nc6 3.Bc4 Nf6 4.Ng5"
            },
            "Legal Trap": {
                "fen": "rnbqkbnr/ppp2ppp/8/3pp3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 0 3",
                "move": "d8g5",
                "description": "Legal's Mate trap after 1.e4 e5 2.Nf3 d5 3.Bc4"
            },
            "Blackburne Shilling Gambit": {
                "fen": "rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",
                "move": "f6e4",
                "description": "Blackburne Shilling Gambit after 1.e4 e5 2.Nf3 Nf6 3.Bc4 Nxe4"
            },
            "Budapest Gambit": {
                "fen": "rnbqkb1r/pppp1ppp/8/4p3/2PPn3/8/PP2PPPP/RNBQKBNR w KQkq - 0 3",
                "move": "d2d3",
                "description": "Budapest Gambit trap after 1.d4 Nf6 2.c4 e5 3.dxe5 Ng4"
            }
        }

        return traps

    def get_trap_move(self, board):
        """
        Check if the current position matches a known trap and return the trap move.

        Args:
            board: A chess.Board object representing the current position.

        Returns:
            A chess.Move object if a trap is available, None otherwise.
        """
        # Only use traps in 'tricky' style or occasionally in other styles
        if self.style != 'tricky' and random.random() > 0.2:
            return None

        # Check if the position matches any trap
        board_fen = board.fen().split(' ')[0]  # Just the piece positions

        for trap_name, trap_data in self.traps.items():
            trap_fen = trap_data["fen"].split(' ')[0]  # Just the piece positions

            if board_fen == trap_fen and board.turn == (trap_data["fen"].split(' ')[1] == 'w'):
                try:
                    # Parse the move from UCI notation
                    move = chess.Move.from_uci(trap_data["move"])

                    # Verify it's a legal move
                    if move in board.legal_moves:
                        print(f"Found trap: {trap_name} - {trap_data['description']}")
                        return move
                except Exception as e:
                    print(f"Error processing trap move: {e}")

        return None
