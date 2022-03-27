import chess.engine
from test_array import activations_array

# class to hold data, state and configurations
# Dash is stateless and in general it is very bad idea to store data in global variables on server side
# However, this application is ment to be run by single user on local machine so it is safe to store data and state
# information on global object
class GlobalData:
    def __init__(self):
        self.fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'#'2kr3r/ppp2b2/2n4p/4p3/Q2Pq1pP/2P1N3/PP3PP1/R1B1KB1R w KQ - 3 18'#'6n1/1p1k4/3p4/pNp5/P1P4p/7P/1P4KP/r7 w - - 2 121'#
        self.board = chess.Board(fen=self.fen)
        self.focused_square_ind = 0

        self.activations = activations_array
        self.visualization_mode = 'ROW'
        self.selected_layer = None
        self.visualization_mode_is_64x64 = False
        self.subplot_cols = 0
        self.subplot_rows = 0
        self.number_of_heads = 8
        self.update_grid_shape()

        self.pgn_data = [] #list of boards

    #    self.model_path = '...'
    #    self.load_model()
    #    self.activations_data = None
    #    self.update_activations_data()
    #    self.set_layer(self.selected_layer)

    def get_side_to_move(self):
        return ['Black', 'White'][self.board.turn]

    def load_model(self):
        self.model = tf.keras.models.load_model(self.model_path)

    def update_activations_data(self):
        inputs = board2planes(board)
        inputs = tf.reshape(tf.convert_to_tensor(inputs, dtype=tf.float32), [-1, 112, 8, 8])
        _, _, _, self.activations_data = self.model(inputs)
        #self.activations = self.activations_data[self.selected_layer]

    def update_grid_shape(self):
        if self.number_of_heads <= 8:
            if self.number_of_heads > 4 and self.number_of_heads in (4, 8):
                self.subplot_cols = min(self.number_of_heads, 4)
            else:
                self.subplot_cols = self.number_of_heads
        else:
            self.subplot_cols = 8
        self.subplot_rows = self.number_of_heads // self.subplot_cols

    def update_activation_data(self):
        import numpy as np
        self.activations = activations_array + np.random.rand(8, 64, 64)

    def set_visualization_mode(self, mode):
        self.visualization_mode = mode
        self.visualization_mode_is_64x64 = mode == '64x64'

    def set_layer(self, layer):
        #TODO
        self.selected_layer = layer
        self.activations = layer * activations_array
        #self.activations = self.activations_data[self.layer]
        self.number_of_heads = 8 #TODO update number of heads in the layer
        self.update_grid_shape()

    def get_head_data(self, head):

        if self.visualization_mode == '64x64':
            #print('64x64 selection')
            data = self.activations[head, :, :]

        elif self.visualization_mode == 'ROW':
            #print('ROW selection')
            data = self.activations[head, self.focused_square_ind, :].reshape((8, 8))
        else:
            #print('COL selection')
            data = self.activations[head, :, self.focused_square_ind].reshape((8, 8))

        #print('SHAPE', data.shape)
        return data

    def set_fen(self, fen):
        self.board.set_fen(fen)
        self.fen = fen

global_data = GlobalData()
print('global data created')