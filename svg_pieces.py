from python_chess_customized_svg import piece
import python_chess_customized_svg as svg
import chess
import base64

#def get_svg_piece(symbol):
#    img = piece(chess.Piece.from_symbol(symbol))
#    svg_str = str(img)
#    svg_byte = svg_str.encode()
#    encoded = base64.b64encode(svg_byte)
#    svg_piece = 'data:image/svg+xml;base64,{}'.format(encoded.decode())
#    return svg_piece

def get_svg_board(board, focused_square_ind, only_pieces):
    svg_str = str(svg.board(board, squares=[focused_square_ind], arrows=[], lastmove=None, coordinates=False, only_pieces=only_pieces))
    svg_byte = svg_str.encode()
    encoded = base64.b64encode(svg_byte)
    svg_board = 'data:image/svg+xml;base64,{}'.format(encoded.decode())
    return svg_board

#SVG_PIECES = {piece: get_svg_piece(piece) for piece in ('b', 'k', 'n', 'p', 'q', 'r', 'B', 'K', 'N', 'P', 'Q', 'R')}