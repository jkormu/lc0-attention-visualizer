import chess.engine
from test_array import activations_array

class GlobalData:
    def __init__(self):
        self.fen = '2kr3r/ppp2b2/2n4p/4p3/Q2Pq1pP/2P1N3/PP3PP1/R1B1KB1R w KQ - 3 18'#'6n1/1p1k4/3p4/pNp5/P1P4p/7P/1P4KP/r7 w - - 2 121'#'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        self.board = chess.Board(fen=self.fen)
        self.focused_square_ind = 14
        self.number_of_heads = 8

        self.activations = activations_array
        self.mode = 'row'

        if self.number_of_heads <= 8:
            if self.number_of_heads > 4 and self.number_of_heads in (4, 8):
                self.subplot_cols = min(self.number_of_heads, 4)
            else:
                self.subplot_cols = self.number_of_heads
        else:
            self.subplot_cols = 8


        self.subplot_rows = self.number_of_heads // self.subplot_cols #+ (self.number_of_heads % self.subplot_cols != 0)

    def get_head_data(self, head):
        data = self.activations[head, self.focused_square_ind, :].reshape((8, 8))
        return data

    def set_fen(self, fen):
        self.board.set_fen(fen)
        self.fen = fen

global_data = GlobalData()
print('global data created')