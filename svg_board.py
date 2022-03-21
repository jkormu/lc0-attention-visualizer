import python_chess_customized_svg as svg
import base64
from constants import SHOW_BOARD_COORDINATES

def svg_board_image(board, arrows, last_move):
    svg_str = str(svg.board(board, size=200, arrows=arrows, lastmove=last_move, coordinates=SHOW_BOARD_COORDINATES))
    svg_str = svg_str.replace('height="200"', 'height="100%"')
    svg_str = svg_str.replace('width="200"', 'width="100%"')
    svg_byte = svg_str.encode()
    encoded = base64.b64encode(svg_byte)
    svg_board = 'data:image/svg+xml;base64,{}'.format(encoded.decode())
    return svg_board