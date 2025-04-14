"""
Evaluation Module
This module provides advanced positional evaluation for the chess engine.
"""

import chess

class PositionalEvaluator:
    """
    Class implementing advanced positional evaluation for chess positions.
    """
    
    # Piece values in centipawns
    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }
    
    # Piece-square tables for positional bonuses
    # Values are in centipawns and represent bonuses for each piece on each square
    # These tables are from white's perspective; they are flipped for black
    
    # Pawn positional bonuses
    PAWN_TABLE = [
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5, -5,-10,  0,  0,-10, -5,  5,
        5, 10, 10,-20,-20, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0
    ]
    
    # Knight positional bonuses
    KNIGHT_TABLE = [
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50
    ]
    
    # Bishop positional bonuses
    BISHOP_TABLE = [
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5,  5,  5,  5,  5,-10,
        -10,  0,  5,  0,  0,  5,  0,-10,
        -20,-10,-10,-10,-10,-10,-10,-20
    ]
    
    # Rook positional bonuses
    ROOK_TABLE = [
        0,  0,  0,  0,  0,  0,  0,  0,
        5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        0,  0,  0,  5,  5,  0,  0,  0
    ]
    
    # Queen positional bonuses
    QUEEN_TABLE = [
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
        -5,  0,  5,  5,  5,  5,  0, -5,
        0,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20
    ]
    
    # King middlegame positional bonuses
    KING_MIDDLE_TABLE = [
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
        20, 20,  0,  0,  0,  0, 20, 20,
        20, 30, 10,  0,  0, 10, 30, 20
    ]
    
    # King endgame positional bonuses
    KING_END_TABLE = [
        -50,-40,-30,-20,-20,-30,-40,-50,
        -30,-20,-10,  0,  0,-10,-20,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-30,  0,  0,  0,  0,-30,-30,
        -50,-30,-30,-30,-30,-30,-30,-50
    ]
    
    # Mapping of piece types to their tables
    PIECE_TABLES = {
        chess.PAWN: PAWN_TABLE,
        chess.KNIGHT: KNIGHT_TABLE,
        chess.BISHOP: BISHOP_TABLE,
        chess.ROOK: ROOK_TABLE,
        chess.QUEEN: QUEEN_TABLE,
        chess.KING: KING_MIDDLE_TABLE  # Default to middlegame
    }
    
    # Pawn structure penalties
    ISOLATED_PAWN_PENALTY = 20
    DOUBLED_PAWN_PENALTY = 10
    BACKWARD_PAWN_PENALTY = 8
    
    # Pawn structure bonuses
    PASSED_PAWN_BONUS = [0, 10, 20, 40, 60, 90, 120, 0]  # Bonus by rank (0-7)
    PAWN_SHIELD_BONUS = 10  # Bonus for each pawn shielding the king
    
    # Mobility bonuses
    MOBILITY_BONUS = {
        chess.KNIGHT: 4,
        chess.BISHOP: 3,
        chess.ROOK: 2,
        chess.QUEEN: 1
    }
    
    # King safety
    KING_ATTACK_WEIGHT = {
        chess.PAWN: 0,
        chess.KNIGHT: 2,
        chess.BISHOP: 2,
        chess.ROOK: 3,
        chess.QUEEN: 5
    }
    
    # Other evaluation parameters
    BISHOP_PAIR_BONUS = 30
    KNIGHT_OUTPOST_BONUS = 15
    ROOK_ON_OPEN_FILE_BONUS = 20
    ROOK_ON_SEMI_OPEN_FILE_BONUS = 10
    
    def __init__(self):
        """Initialize the positional evaluator."""
        pass
    
    def evaluate(self, board):
        """
        Evaluate a chess position with advanced positional understanding.
        
        Args:
            board: A chess.Board object
            
        Returns:
            An evaluation score in centipawns from white's perspective
        """
        if board.is_checkmate():
            # Return a high value for checkmate, adjusted by remaining depth
            return -10000 if board.turn == chess.WHITE else 10000
        
        if board.is_stalemate() or board.is_insufficient_material():
            # Draw
            return 0
        
        # Start with material evaluation
        score = self.evaluate_material(board)
        
        # Add positional evaluation
        score += self.evaluate_piece_position(board)
        
        # Add pawn structure evaluation
        score += self.evaluate_pawn_structure(board)
        
        # Add king safety evaluation
        score += self.evaluate_king_safety(board)
        
        # Add mobility evaluation
        score += self.evaluate_mobility(board)
        
        # Add other positional factors
        score += self.evaluate_other_factors(board)
        
        # Return the score from white's perspective
        return score
    
    def evaluate_material(self, board):
        """
        Evaluate the material balance of the position.
        
        Args:
            board: A chess.Board object
            
        Returns:
            The material balance in centipawns from white's perspective
        """
        score = 0
        
        # Count material for each piece type
        for piece_type in chess.PIECE_TYPES:
            score += len(board.pieces(piece_type, chess.WHITE)) * self.PIECE_VALUES[piece_type]
            score -= len(board.pieces(piece_type, chess.BLACK)) * self.PIECE_VALUES[piece_type]
        
        return score
    
    def evaluate_piece_position(self, board):
        """
        Evaluate the positional value of pieces based on piece-square tables.
        
        Args:
            board: A chess.Board object
            
        Returns:
            The positional score in centipawns from white's perspective
        """
        score = 0
        
        # Determine if we're in an endgame
        is_endgame = self.is_endgame(board)
        
        # Evaluate each piece's position
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None:
                continue
            
            # Get the appropriate piece-square table
            if piece.piece_type == chess.KING:
                table = self.KING_END_TABLE if is_endgame else self.KING_MIDDLE_TABLE
            else:
                table = self.PIECE_TABLES[piece.piece_type]
            
            # Get the position value (flip for black)
            if piece.color == chess.WHITE:
                position_value = table[square]
            else:
                # Flip the square for black's perspective (mirror vertically)
                flipped_square = square ^ 56  # XOR with 56 (7 * 8) flips the rank
                position_value = table[flipped_square]
            
            # Add to score (positive for white, negative for black)
            if piece.color == chess.WHITE:
                score += position_value
            else:
                score -= position_value
        
        return score
    
    def evaluate_pawn_structure(self, board):
        """
        Evaluate the pawn structure (isolated, doubled, passed pawns).
        
        Args:
            board: A chess.Board object
            
        Returns:
            The pawn structure score in centipawns from white's perspective
        """
        score = 0
        
        # Get pawn positions for both sides
        white_pawns = board.pieces(chess.PAWN, chess.WHITE)
        black_pawns = board.pieces(chess.PAWN, chess.BLACK)
        
        # Count pawns on each file
        white_pawn_files = [0] * 8
        black_pawn_files = [0] * 8
        
        # Track which files have pawns
        for pawn in white_pawns:
            file = chess.square_file(pawn)
            white_pawn_files[file] += 1
        
        for pawn in black_pawns:
            file = chess.square_file(pawn)
            black_pawn_files[file] += 1
        
        # Evaluate white pawns
        for pawn in white_pawns:
            file = chess.square_file(pawn)
            rank = chess.square_rank(pawn)
            
            # Check for doubled pawns
            if white_pawn_files[file] > 1:
                score -= self.DOUBLED_PAWN_PENALTY
            
            # Check for isolated pawns
            is_isolated = True
            for adj_file in [file - 1, file + 1]:
                if 0 <= adj_file < 8 and white_pawn_files[adj_file] > 0:
                    is_isolated = False
                    break
            
            if is_isolated:
                score -= self.ISOLATED_PAWN_PENALTY
            
            # Check for passed pawns
            is_passed = True
            for adj_file in range(max(0, file - 1), min(8, file + 2)):
                # Check if any black pawns are ahead on this file or adjacent files
                for r in range(rank + 1, 8):
                    if board.piece_at(chess.square(adj_file, r)) == chess.Piece(chess.PAWN, chess.BLACK):
                        is_passed = False
                        break
                if not is_passed:
                    break
            
            if is_passed:
                score += self.PASSED_PAWN_BONUS[rank]
            
            # Check for backward pawns
            is_backward = True
            for adj_file in [file - 1, file + 1]:
                if 0 <= adj_file < 8:
                    for r in range(rank):
                        if board.piece_at(chess.square(adj_file, r)) == chess.Piece(chess.PAWN, chess.WHITE):
                            is_backward = False
                            break
            
            if is_backward and (file == 0 or white_pawn_files[file - 1] == 0) and (file == 7 or white_pawn_files[file + 1] == 0):
                score -= self.BACKWARD_PAWN_PENALTY
        
        # Evaluate black pawns
        for pawn in black_pawns:
            file = chess.square_file(pawn)
            rank = chess.square_rank(pawn)
            
            # Check for doubled pawns
            if black_pawn_files[file] > 1:
                score += self.DOUBLED_PAWN_PENALTY
            
            # Check for isolated pawns
            is_isolated = True
            for adj_file in [file - 1, file + 1]:
                if 0 <= adj_file < 8 and black_pawn_files[adj_file] > 0:
                    is_isolated = False
                    break
            
            if is_isolated:
                score += self.ISOLATED_PAWN_PENALTY
            
            # Check for passed pawns
            is_passed = True
            for adj_file in range(max(0, file - 1), min(8, file + 2)):
                # Check if any white pawns are ahead on this file or adjacent files
                for r in range(0, rank):
                    if board.piece_at(chess.square(adj_file, r)) == chess.Piece(chess.PAWN, chess.WHITE):
                        is_passed = False
                        break
                if not is_passed:
                    break
            
            if is_passed:
                score -= self.PASSED_PAWN_BONUS[7 - rank]  # Flip rank for black
            
            # Check for backward pawns
            is_backward = True
            for adj_file in [file - 1, file + 1]:
                if 0 <= adj_file < 8:
                    for r in range(rank + 1, 8):
                        if board.piece_at(chess.square(adj_file, r)) == chess.Piece(chess.PAWN, chess.BLACK):
                            is_backward = False
                            break
            
            if is_backward and (file == 0 or black_pawn_files[file - 1] == 0) and (file == 7 or black_pawn_files[file + 1] == 0):
                score += self.BACKWARD_PAWN_PENALTY
        
        return score
    
    def evaluate_king_safety(self, board):
        """
        Evaluate the safety of both kings.
        
        Args:
            board: A chess.Board object
            
        Returns:
            The king safety score in centipawns from white's perspective
        """
        score = 0
        
        # If we're in an endgame, king safety is less important
        if self.is_endgame(board):
            return score
        
        # Get king positions
        white_king = board.king(chess.WHITE)
        black_king = board.king(chess.BLACK)
        
        if white_king is None or black_king is None:
            return score
        
        # Evaluate pawn shield for white king
        white_king_file = chess.square_file(white_king)
        white_king_rank = chess.square_rank(white_king)
        
        # King should be castled (on the back rank)
        if white_king_rank == 0:
            # Check for pawn shield
            for file in range(max(0, white_king_file - 1), min(8, white_king_file + 2)):
                for rank in range(1, 3):  # Check first and second rank in front of king
                    square = chess.square(file, rank)
                    if board.piece_at(square) == chess.Piece(chess.PAWN, chess.WHITE):
                        score += self.PAWN_SHIELD_BONUS
        
        # Evaluate pawn shield for black king
        black_king_file = chess.square_file(black_king)
        black_king_rank = chess.square_rank(black_king)
        
        # King should be castled (on the back rank)
        if black_king_rank == 7:
            # Check for pawn shield
            for file in range(max(0, black_king_file - 1), min(8, black_king_file + 2)):
                for rank in range(5, 7):  # Check first and second rank in front of king
                    square = chess.square(file, rank)
                    if board.piece_at(square) == chess.Piece(chess.PAWN, chess.BLACK):
                        score -= self.PAWN_SHIELD_BONUS
        
        # Evaluate king attackers
        white_king_attackers = 0
        black_king_attackers = 0
        
        # Count attackers around white king
        for square in self.get_king_attack_zone(white_king):
            attacker = board.piece_at(square)
            if attacker and attacker.color == chess.BLACK:
                white_king_attackers += self.KING_ATTACK_WEIGHT.get(attacker.piece_type, 0)
        
        # Count attackers around black king
        for square in self.get_king_attack_zone(black_king):
            attacker = board.piece_at(square)
            if attacker and attacker.color == chess.WHITE:
                black_king_attackers += self.KING_ATTACK_WEIGHT.get(attacker.piece_type, 0)
        
        # Apply king safety score
        score -= white_king_attackers * 5  # Penalty for white king attackers
        score += black_king_attackers * 5  # Penalty for black king attackers
        
        return score
    
    def evaluate_mobility(self, board):
        """
        Evaluate the mobility of pieces (number of legal moves).
        
        Args:
            board: A chess.Board object
            
        Returns:
            The mobility score in centipawns from white's perspective
        """
        score = 0
        
        # Create a copy of the board to avoid side effects
        board_copy = board.copy()
        
        # Evaluate white mobility
        board_copy.turn = chess.WHITE
        white_mobility = self.count_piece_mobility(board_copy)
        
        # Evaluate black mobility
        board_copy.turn = chess.BLACK
        black_mobility = self.count_piece_mobility(board_copy)
        
        # Apply mobility score
        for piece_type in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
            score += white_mobility.get(piece_type, 0) * self.MOBILITY_BONUS[piece_type]
            score -= black_mobility.get(piece_type, 0) * self.MOBILITY_BONUS[piece_type]
        
        return score
    
    def evaluate_other_factors(self, board):
        """
        Evaluate other positional factors.
        
        Args:
            board: A chess.Board object
            
        Returns:
            The score for other positional factors in centipawns from white's perspective
        """
        score = 0
        
        # Bishop pair bonus
        if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
            score += self.BISHOP_PAIR_BONUS
        if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
            score -= self.BISHOP_PAIR_BONUS
        
        # Rook on open file
        for rook in board.pieces(chess.ROOK, chess.WHITE):
            file = chess.square_file(rook)
            if self.is_open_file(board, file):
                score += self.ROOK_ON_OPEN_FILE_BONUS
            elif self.is_semi_open_file(board, file, chess.WHITE):
                score += self.ROOK_ON_SEMI_OPEN_FILE_BONUS
        
        for rook in board.pieces(chess.ROOK, chess.BLACK):
            file = chess.square_file(rook)
            if self.is_open_file(board, file):
                score -= self.ROOK_ON_OPEN_FILE_BONUS
            elif self.is_semi_open_file(board, file, chess.BLACK):
                score -= self.ROOK_ON_SEMI_OPEN_FILE_BONUS
        
        # Knight outposts
        for knight in board.pieces(chess.KNIGHT, chess.WHITE):
            if self.is_outpost(board, knight, chess.WHITE):
                score += self.KNIGHT_OUTPOST_BONUS
        
        for knight in board.pieces(chess.KNIGHT, chess.BLACK):
            if self.is_outpost(board, knight, chess.BLACK):
                score -= self.KNIGHT_OUTPOST_BONUS
        
        return score
    
    def is_endgame(self, board):
        """
        Determine if the position is an endgame.
        
        Args:
            board: A chess.Board object
            
        Returns:
            True if the position is an endgame, False otherwise
        """
        # Count the number of non-pawn pieces for each side
        white_pieces = 0
        black_pieces = 0
        
        for piece_type in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
            white_pieces += len(board.pieces(piece_type, chess.WHITE))
            black_pieces += len(board.pieces(piece_type, chess.BLACK))
        
        # Consider it an endgame if both sides have <= 3 non-pawn pieces
        # or if one side has a queen and no other pieces
        return (white_pieces <= 3 and black_pieces <= 3) or \
               (white_pieces == 1 and len(board.pieces(chess.QUEEN, chess.WHITE)) == 1) or \
               (black_pieces == 1 and len(board.pieces(chess.QUEEN, chess.BLACK)) == 1)
    
    def count_piece_mobility(self, board):
        """
        Count the number of legal moves for each piece type.
        
        Args:
            board: A chess.Board object with the correct side to move
            
        Returns:
            A dictionary mapping piece types to mobility counts
        """
        mobility = {
            chess.KNIGHT: 0,
            chess.BISHOP: 0,
            chess.ROOK: 0,
            chess.QUEEN: 0
        }
        
        # Get all legal moves
        legal_moves = list(board.legal_moves)
        
        # Count moves by piece type
        for move in legal_moves:
            from_square = move.from_square
            piece = board.piece_at(from_square)
            if piece and piece.piece_type in mobility:
                mobility[piece.piece_type] += 1
        
        return mobility
    
    def get_king_attack_zone(self, king_square):
        """
        Get the squares in the attack zone around a king.
        
        Args:
            king_square: The square where the king is located
            
        Returns:
            A list of squares in the king's attack zone
        """
        attack_zone = []
        king_file = chess.square_file(king_square)
        king_rank = chess.square_rank(king_square)
        
        # Include squares around the king
        for file in range(max(0, king_file - 1), min(8, king_file + 2)):
            for rank in range(max(0, king_rank - 1), min(8, king_rank + 2)):
                if file != king_file or rank != king_rank:  # Exclude the king's square
                    attack_zone.append(chess.square(file, rank))
        
        return attack_zone
    
    def is_open_file(self, board, file):
        """
        Check if a file is completely open (no pawns).
        
        Args:
            board: A chess.Board object
            file: The file to check (0-7)
            
        Returns:
            True if the file is open, False otherwise
        """
        for rank in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.PAWN:
                return False
        return True
    
    def is_semi_open_file(self, board, file, color):
        """
        Check if a file is semi-open (no pawns of the specified color).
        
        Args:
            board: A chess.Board object
            file: The file to check (0-7)
            color: The color to check for pawns
            
        Returns:
            True if the file is semi-open, False otherwise
        """
        for rank in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.PAWN and piece.color == color:
                return False
        return True
    
    def is_outpost(self, board, square, color):
        """
        Check if a square is an outpost for a knight of the specified color.
        An outpost is a square that cannot be attacked by enemy pawns.
        
        Args:
            board: A chess.Board object
            square: The square to check
            color: The color of the knight
            
        Returns:
            True if the square is an outpost, False otherwise
        """
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        
        # Knights are most effective as outposts in enemy territory
        if color == chess.WHITE and rank < 4:
            return False
        if color == chess.BLACK and rank > 3:
            return False
        
        # Check if the square can be attacked by enemy pawns
        enemy_color = not color
        
        # For white knight, check if black pawns can attack the square
        if color == chess.WHITE:
            for attack_file in [file - 1, file + 1]:
                if 0 <= attack_file < 8:
                    attack_rank = rank - 1
                    if 0 <= attack_rank < 8:
                        attack_square = chess.square(attack_file, attack_rank)
                        if board.piece_at(attack_square) == chess.Piece(chess.PAWN, chess.BLACK):
                            return False
        
        # For black knight, check if white pawns can attack the square
        else:
            for attack_file in [file - 1, file + 1]:
                if 0 <= attack_file < 8:
                    attack_rank = rank + 1
                    if 0 <= attack_rank < 8:
                        attack_square = chess.square(attack_file, attack_rank)
                        if board.piece_at(attack_square) == chess.Piece(chess.PAWN, chess.WHITE):
                            return False
        
        # Check if the square is supported by a friendly pawn
        if color == chess.WHITE:
            for support_file in [file - 1, file + 1]:
                if 0 <= support_file < 8:
                    support_rank = rank - 1
                    if 0 <= support_rank < 8:
                        support_square = chess.square(support_file, support_rank)
                        if board.piece_at(support_square) == chess.Piece(chess.PAWN, chess.WHITE):
                            return True
        else:
            for support_file in [file - 1, file + 1]:
                if 0 <= support_file < 8:
                    support_rank = rank + 1
                    if 0 <= support_rank < 8:
                        support_square = chess.square(support_file, support_rank)
                        if board.piece_at(support_square) == chess.Piece(chess.PAWN, chess.BLACK):
                            return True
        
        return False
