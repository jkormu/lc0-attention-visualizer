#Author: https://github.com/Arcturai

import chess
import numpy as np
import re


WPAWN = chess.Piece(chess.PAWN, chess.WHITE)
WKNIGHT = chess.Piece(chess.KNIGHT, chess.WHITE)
WBISHOP = chess.Piece(chess.BISHOP, chess.WHITE)
WROOK = chess.Piece(chess.ROOK, chess.WHITE)
WQUEEN = chess.Piece(chess.QUEEN, chess.WHITE)
WKING = chess.Piece(chess.KING, chess.WHITE)
BPAWN = chess.Piece(chess.PAWN, chess.BLACK)
BKNIGHT = chess.Piece(chess.KNIGHT, chess.BLACK)
BBISHOP = chess.Piece(chess.BISHOP, chess.BLACK)
BROOK = chess.Piece(chess.ROOK, chess.BLACK)
BQUEEN = chess.Piece(chess.QUEEN, chess.BLACK)
BKING = chess.Piece(chess.KING, chess.BLACK)


def assign_piece2(planes, piece_step, row, col):
    planes[piece_step][row][col] = 1


DISPATCH2 = {}

DISPATCH2[str(WPAWN)] = lambda retval, row, col: assign_piece2(retval, 0, row, col)
DISPATCH2[str(WKNIGHT)] = lambda retval, row, col: assign_piece2(retval, 1, row, col)
DISPATCH2[str(WBISHOP)] = lambda retval, row, col: assign_piece2(retval, 2, row, col)
DISPATCH2[str(WROOK)] = lambda retval, row, col: assign_piece2(retval, 3, row, col)
DISPATCH2[str(WQUEEN)] = lambda retval, row, col: assign_piece2(retval, 4, row, col)
DISPATCH2[str(WKING)] = lambda retval, row, col: assign_piece2(retval, 5, row, col)
DISPATCH2[str(BPAWN)] = lambda retval, row, col: assign_piece2(retval, 6, row, col)
DISPATCH2[str(BKNIGHT)] = lambda retval, row, col: assign_piece2(retval, 7, row, col)
DISPATCH2[str(BBISHOP)] = lambda retval, row, col: assign_piece2(retval, 8, row, col)
DISPATCH2[str(BROOK)] = lambda retval, row, col: assign_piece2(retval, 9, row, col)
DISPATCH2[str(BQUEEN)] = lambda retval, row, col: assign_piece2(retval, 10, row, col)
DISPATCH2[str(BKING)] = lambda retval, row, col: assign_piece2(retval, 11, row, col)


def append_plane(planes, ones):
    if ones:
        return np.append(planes, np.ones((1, 8, 8), dtype=np.float), axis=0)
    else:
        return np.append(planes, np.zeros((1, 8, 8), dtype=np.float), axis=0)


def fill_planes(board):
    planes = np.zeros((12, 8, 8), dtype=np.float)
    for row in range(8):
        for col in range(8):
            piece = str(board.piece_at(chess.SQUARES[row * 8 + col]))
            if piece != "None":
                DISPATCH2[piece](planes, row, col)
    planes = append_plane(planes, board.is_repetition(2))
    return planes


def board2planes(board_):
    if not board_.turn:
        board = board_.mirror()
    else:
        board = board_

    retval = fill_planes(board)

    s_board = board_.copy()
    for i in range(7):
        if s_board.move_stack.__len__() > 0:
            s_board.pop()
            b = s_board.mirror() if not board_.turn else s_board.copy()
            retval = np.append(retval, fill_planes(b), axis=0)
        else:
            retval = np.append(retval, np.zeros((13, 8, 8), dtype=np.float), axis=0)

    retval = append_plane(retval, bool(board.castling_rights & chess.BB_H1))
    retval = append_plane(retval, bool(board.castling_rights & chess.BB_A1))
    retval = append_plane(retval, bool(board.castling_rights & chess.BB_H8))
    retval = append_plane(retval, bool(board.castling_rights & chess.BB_A8))
    retval = append_plane(retval, not board_.turn)
    retval = np.append(retval, np.full((1, 8, 8), fill_value=board_.halfmove_clock/99., dtype=np.float), axis=0)
    retval = append_plane(retval, False)
    retval = append_plane(retval, True)

    return np.expand_dims(retval, axis=0)


def bulk_board2planes(boards):
    planes = []
    for b in boards:
        temp = board2planes(b)
        planes.append(temp)
    pl = tuple(planes)
    retval = np.concatenate(pl, axis=0)
    return retval

