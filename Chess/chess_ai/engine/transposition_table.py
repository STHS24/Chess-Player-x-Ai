"""
Transposition Table Module
This module provides a transposition table implementation for caching chess positions.
"""

import chess
import random
import time
from collections import OrderedDict

class TranspositionTable:
    """
    A transposition table for caching chess positions and their evaluations.
    Uses Zobrist hashing for efficient position identification.
    """
    
    def __init__(self, max_size=1000000):
        """
        Initialize the transposition table.
        
        Args:
            max_size: Maximum number of positions to store in the table
        """
        self.max_size = max_size
        self.table = OrderedDict()  # Using OrderedDict for LRU functionality
        self.zobrist_keys = self._initialize_zobrist_keys()
        self.hits = 0
        self.misses = 0
        self.collisions = 0
    
    def _initialize_zobrist_keys(self):
        """
        Initialize Zobrist keys for efficient board hashing.
        
        Returns:
            A dictionary of random 64-bit integers for each piece on each square,
            plus additional keys for castling rights, en passant, and side to move.
        """
        # Create a random number generator with a fixed seed for consistency
        rng = random.Random(42)
        
        # Initialize the keys dictionary
        keys = {}
        
        # Generate keys for each piece on each square
        for square in range(64):
            for piece_type in range(1, 7):  # PAWN=1, KNIGHT=2, ..., KING=6
                for color in [chess.WHITE, chess.BLACK]:
                    piece = chess.Piece(piece_type, color)
                    keys[(square, piece)] = rng.getrandbits(64)
        
        # Generate keys for castling rights
        keys['castling_K'] = rng.getrandbits(64)
        keys['castling_Q'] = rng.getrandbits(64)
        keys['castling_k'] = rng.getrandbits(64)
        keys['castling_q'] = rng.getrandbits(64)
        
        # Generate keys for en passant squares
        for square in range(64):
            keys[('ep', square)] = rng.getrandbits(64)
        
        # Generate a key for side to move
        keys['side_to_move'] = rng.getrandbits(64)
        
        return keys
    
    def compute_hash(self, board):
        """
        Compute the Zobrist hash for a chess position.
        
        Args:
            board: A chess.Board object
            
        Returns:
            A 64-bit hash value for the position
        """
        h = 0
        
        # Hash pieces
        for square in range(64):
            piece = board.piece_at(square)
            if piece:
                h ^= self.zobrist_keys[(square, piece)]
        
        # Hash castling rights
        if board.has_kingside_castling_rights(chess.WHITE):
            h ^= self.zobrist_keys['castling_K']
        if board.has_queenside_castling_rights(chess.WHITE):
            h ^= self.zobrist_keys['castling_Q']
        if board.has_kingside_castling_rights(chess.BLACK):
            h ^= self.zobrist_keys['castling_k']
        if board.has_queenside_castling_rights(chess.BLACK):
            h ^= self.zobrist_keys['castling_q']
        
        # Hash en passant square
        if board.ep_square is not None:
            h ^= self.zobrist_keys[('ep', board.ep_square)]
        
        # Hash side to move
        if board.turn == chess.BLACK:
            h ^= self.zobrist_keys['side_to_move']
        
        return h
    
    def get(self, board, depth=None):
        """
        Get an evaluation from the transposition table.
        
        Args:
            board: A chess.Board object
            depth: The search depth (if None, any depth will match)
            
        Returns:
            A tuple (hit, entry) where:
            - hit is a boolean indicating if the position was found
            - entry is the stored data or None if not found
        """
        board_hash = self.compute_hash(board)
        
        if board_hash in self.table:
            entry = self.table[board_hash]
            
            # If depth is specified, check if the stored entry is deep enough
            if depth is None or entry['depth'] >= depth:
                # Move the entry to the end of the OrderedDict (most recently used)
                self.table.move_to_end(board_hash)
                self.hits += 1
                return True, entry
        
        self.misses += 1
        return False, None
    
    def put(self, board, data, depth):
        """
        Store an evaluation in the transposition table.
        
        Args:
            board: A chess.Board object
            data: The data to store (typically evaluation and best move)
            depth: The search depth used to obtain this evaluation
        """
        board_hash = self.compute_hash(board)
        
        # Check if we're replacing an existing entry
        if board_hash in self.table:
            # Only replace if the new entry is from a deeper search
            if self.table[board_hash]['depth'] <= depth:
                self.table[board_hash] = {
                    'data': data,
                    'depth': depth,
                    'timestamp': time.time()
                }
                # Move to the end (most recently used)
                self.table.move_to_end(board_hash)
            else:
                self.collisions += 1
        else:
            # Add new entry
            self.table[board_hash] = {
                'data': data,
                'depth': depth,
                'timestamp': time.time()
            }
            
            # If table is full, remove the least recently used entry
            if len(self.table) > self.max_size:
                self.table.popitem(last=False)
    
    def clear(self):
        """Clear the transposition table."""
        self.table.clear()
        self.hits = 0
        self.misses = 0
        self.collisions = 0
    
    def get_stats(self):
        """
        Get statistics about the transposition table usage.
        
        Returns:
            A dictionary with statistics
        """
        total_lookups = self.hits + self.misses
        hit_rate = (self.hits / total_lookups) * 100 if total_lookups > 0 else 0
        
        return {
            'size': len(self.table),
            'max_size': self.max_size,
            'usage': f"{len(self.table) / self.max_size * 100:.2f}%",
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.2f}%",
            'collisions': self.collisions
        }
