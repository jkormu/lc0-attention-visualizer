import chess.engine
#from test_array import activations_array

from board2planes import board2planes

#turn off tensorflow importing and gerenerate random data to speed up development
SIMULATE_TF = True
SIMULATED_LAYERS = 6
SIMULATED_HEADS = 14
FIXED_ROW = None #1 #None to disable
FIXED_COL = None #5 #None to disable
if SIMULATE_TF:
    import numpy as np

# class to hold data, state and configurations
# Dash is stateless and in general it is very bad idea to store data in global variables on server side
# However, this application is ment to be run by single user on local machine so it is safe to store data and state
# information on global object
class GlobalData:
    def __init__(self):
        import os
        if not SIMULATE_TF:
            import tensorflow as tf
            os.environ["CUDA_VISIBLE_DEVICES"] = "0"

            from tensorflow.compat.v1 import ConfigProto
            from tensorflow.compat.v1 import InteractiveSession
            # import chess
            # import matplotlib.patheffects as path_effects

            config = ConfigProto()
            config.gpu_options.allow_growth = True
            session = InteractiveSession(config=config)
            tf.keras.backend.clear_session()


        self.fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'#'2kr3r/ppp2b2/2n4p/4p3/Q2Pq1pP/2P1N3/PP3PP1/R1B1KB1R w KQ - 3 18'#'6n1/1p1k4/3p4/pNp5/P1P4p/7P/1P4KP/r7 w - - 2 121'#
        self.board = chess.Board(fen=self.fen)
        self.focused_square_ind = 0

        self.activations = None#activations_array
        self.visualization_mode = 'ROW'
        self.visualization_mode_is_64x64 = False
        self.subplot_mode = 'fit'#big'#'fit'#, 'big'
        self.subplot_cols = 0
        self.subplot_rows = 0
        self.number_of_heads = 8
        self.figure_container_height = '100%'#'100%'
        self.update_grid_shape()


        self.pgn_data = [] #list of boards

        self.selected_layer = 0
        self.nr_of_layers_in_body = -1

        self.model_path = '/home/jusufe/PycharmProjects/lc0-attention-visualizer/T12_saved_model_1M'
        self.model = None
        if not SIMULATE_TF:
            self.load_model()
        self.activations_data = None
        self.update_activations_data()
        self.set_layer(self.selected_layer)

    def get_side_to_move(self):
        return ['Black', 'White'][self.board.turn]

    def load_model(self):
        self.model = tf.saved_model.load(self.model_path)  # tf.keras.models.load_model(root)

    def update_activations_data(self):
        if not SIMULATE_TF:
            inputs = board2planes(self.board)
            inputs = tf.reshape(tf.convert_to_tensor(inputs, dtype=tf.float32), [-1, 112, 8, 8])
            _, _, _, self.activations_data = self.model(inputs)
        else:
            layers = SIMULATED_LAYERS
            heads = SIMULATED_HEADS
            self.activations_data = [np.random.rand(1, heads, 64, 64) for i in range(layers)]

        self.update_layers_in_body_count()
        #self.update_selected_activation_data()
        #self.activations = self.activations_data[self.selected_layer]

    def update_grid_shape(self):
        #TODO: add client side callback triggered by Interval component to save window or precise container dimensions to Div
        #TODO: Trigger server side figure update callback when dimensions are recorded and store in global_data
        #TODO: If needed, recalculate subplot rows and cols and container scaler based on the changed dimension

        def calc_cols(heads, rows):
            if heads % rows == 0:
                cols = int(heads / rows)
            else:
                cols = int(1 + heads / rows)
            return cols
        if FIXED_ROW and FIXED_COL:
            self.subplot_cols = FIXED_COL
            self.subplot_rows = FIXED_ROW
            return None

        heads = self.number_of_heads
        if self.subplot_mode == 'fit':
            max_rows_in_screen = 4
            if heads <= 4:
                rows = 1
            elif heads <= 8:
                rows = 2
            else:
                rows = heads // 8 + int(heads % 8 !=0)

        elif self.subplot_mode == 'big':
            max_rows_in_screen = 2
            rows = heads // 4 + int(heads % 4 != 0)

        if rows > max_rows_in_screen:
            container_heigth = f'{int((rows / max_rows_in_screen)*100)}%'
        else:
            container_heigth = '100%'

        cols = calc_cols(heads, rows)
        self.subplot_cols = cols
        self.subplot_rows = rows
        self.figure_container_height = container_heigth


        #if self.number_of_heads <= 8:
        #    if self.number_of_heads > 4 and self.number_of_heads in (4, 8):
        #        self.subplot_cols = min(self.number_of_heads, 4)
        #    else:
        #        self.subplot_cols = self.number_of_heads
        #else:
        #    self.subplot_cols = 8
        #self.subplot_rows = self.number_of_heads // self.subplot_cols

        #if self.number_of_heads == 12:
        #    self.subplot_rows = 3#2
        #    self.subplot_cols = 4#6

    def update_selected_activation_data(self):
        #import numpy as np
        #self.activations = activations_array + np.random.rand(8, 64, 64)
        if not SIMULATE_TF:
            self.activations = tf.squeeze(self.activations_data[self.selected_layer], axis=0).numpy()
        else:
            self.activations = np.squeeze(self.activations_data[self.selected_layer], axis=0)

    def set_visualization_mode(self, mode):
        self.visualization_mode = mode
        self.visualization_mode_is_64x64 = mode == '64x64'

    def set_layer(self, layer):
        #TODO
        self.selected_layer = layer
        self.update_selected_activation_data()
        #self.activations = layer * activations_array
        #self.activations = self.activations_data[self.layer]
        self.number_of_heads = self.activations_data[self.selected_layer].shape[1]
        print('NUMBER OF HEADS', self.number_of_heads)
        self.update_grid_shape()

    def update_layers_in_body_count(self):
        #TODO: figure out robust way to separate attention layers in body from the rest.
        heads = self.activations_data[0].shape[1]
        for ind, layer in enumerate(self.activations_data):
            if layer.shape[1] != heads:
                ind = ind - 1
                break
        self.nr_of_layers_in_body = ind + 1

    def get_head_data(self, head):

        if self.activations.shape[0] <= head:
            return None

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