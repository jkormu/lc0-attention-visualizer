import chess.engine
from constants import ROOT_DIR
#from test_array import activations_array

from copy import deepcopy

from board2planes import board2planes

#turn off tensorflow importing and gerenerate random data to speed up development
SIMULATE_TF = True
SIMULATED_LAYERS = 6
SIMULATED_HEADS = 8
FIXED_ROW = None #1 #None to disable
FIXED_COL = None #5 #None to disable
if SIMULATE_TF:
    import numpy as np
else:
    import tensorflow as tf
    from tensorflow.compat.v1 import ConfigProto
    from tensorflow.compat.v1 import InteractiveSession
# class to hold data, state and configurations
# Dash is stateless and in general it is very bad idea to store data in global variables on server side
# However, this application is ment to be run by single user on local machine so it is safe to store data and state
# information on global object
class GlobalData:
    def __init__(self):
        import os
        if not SIMULATE_TF:
            #import tensorflow as tf
            os.environ["CUDA_VISIBLE_DEVICES"] = "0"

            #from tensorflow.compat.v1 import ConfigProto
            #from tensorflow.compat.v1 import InteractiveSession
            # import chess
            # import matplotlib.patheffects as path_effects

            config = ConfigProto()
            config.gpu_options.allow_growth = True
            session = InteractiveSession(config=config)
            tf.keras.backend.clear_session()

        self.tmp = 0
        self.fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'#'2kr3r/ppp2b2/2n4p/4p3/Q2Pq1pP/2P1N3/PP3PP1/R1B1KB1R w KQ - 3 18'#'6n1/1p1k4/3p4/pNp5/P1P4p/7P/1P4KP/r7 w - - 2 121'#
        self.board = chess.Board(fen=self.fen)
        self.focused_square_ind = 0
        self.active_move_table_cell = None #tuple (row_ind, col_id), e.g. (12, 'White')

        self.activations = None#activations_array
        self.visualization_mode = 'ROW'
        self.visualization_mode_is_64x64 = False
        self.subplot_mode = 'fit'#big'#'fit'#, 'big'
        self.subplot_cols = 0
        self.subplot_rows = 0
        self.number_of_heads = 8
        self.figure_container_height = '100%'#'100%'

        self.running_counter = 0 #used to pass new values to hidden indicator elements which will trigger follow-up callback
        self.grid_has_changed = False

        #self.has_subplot_grid_changed = True
        #self.figure_layout_images = None #store layout and only recalculate when subplot grid has changed
        #self.figure_layout_annotations = None
        #self.need_update_axis = True

        self.figure_cache = {}

        self.update_grid_shape()


        self.pgn_data = [] #list of boards in pgn
        self.move_table_boards = {} #dict of boards in pgn, key is (move_table.row_ind, move_table.column_id)

        self.selected_layer = 0
        self.nr_of_layers_in_body = -1

        self.model_paths = []
        self.model_folders = []
        self.model_cache = {}
        self.find_models()
        self.model_path = self.model_paths[0] #'/home/jusufe/PycharmProjects/lc0-attention-visualizer/T12_saved_model_1M'
        self.model = None
        if not SIMULATE_TF:
            self.load_model()
        self.activations_data = None
        self.update_activations_data()
        self.set_layer(self.selected_layer)

        self.move_table_active_cell = None

    def cache_figure(self, fig):
        if not self.check_if_figure_is_cached():
            key = self.get_figure_cache_key()
            self.figure_cache[key] = fig

    def get_cached_figure(self):
        if self.check_if_figure_is_cached():
            key = self.get_figure_cache_key()
            fig = self.figure_cache[key]
        else:
            fig = None
        return fig

    def check_if_figure_is_cached(self):
        key = self.get_figure_cache_key()
        return key in self.figure_cache

    def get_figure_cache_key(self):
        return (self.subplot_rows, self.subplot_cols, self.visualization_mode_is_64x64)

    def get_side_to_move(self):
        return ['Black', 'White'][self.board.turn]

    def load_model(self):
        if self.model_path in self.model_cache:
            self.model = self.model_cache[self.model_path]
        else:
            self.model = tf.saved_model.load(self.model_path)  # tf.keras.models.load_model(root)


    def find_models(self):
        import os
        from os.path import isdir, join
        root = ROOT_DIR
        models_root_folder = os.path.join(root, 'models')
        model_folders = [f for f in os.listdir(models_root_folder) if isdir(join(models_root_folder, f))]
        model_paths = [os.path.relpath(join(models_root_folder, f)) for f in os.listdir(models_root_folder) if isdir(join(models_root_folder, f))]
        self.model_folders = model_folders
        self.model_paths = model_paths

        print('MODELS:')
        print(self.model_folders)
        print(self.model_paths)

    def update_activations_data(self):
        if not SIMULATE_TF:
            inputs = board2planes(self.board)
            inputs = tf.reshape(tf.convert_to_tensor(inputs, dtype=tf.float32), [-1, 112, 8, 8])
            _, _, _, self.activations_data = self.model(inputs)
        else:
            layers = SIMULATED_LAYERS
            heads = SIMULATED_HEADS
            self.activations_data = [np.random.rand(1, heads, 64, 64) for i in range(layers)]

        if self.model_path not in self.model_cache:
            self.model_cache[self.model_path] = self.model

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
            container_height = f'{int((rows / max_rows_in_screen)*100)}%'
        else:
            container_height = '100%'

        cols = calc_cols(heads, rows)

        if self.subplot_rows != rows or self.subplot_cols != cols:
            self.grid_has_changed = True

        self.subplot_cols = cols
        self.subplot_rows = rows
        self.figure_container_height = container_height

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
        self.selected_layer = layer
        self.update_selected_activation_data()
        #self.activations = layer * activations_array
        #self.activations = self.activations_data[self.layer]
        self.number_of_heads = self.activations_data[self.selected_layer].shape[1]
        print('NUMBER OF HEADS', self.number_of_heads)
        self.update_grid_shape()

    def set_model(self, model):
        if model != self.model_path:
            self.model_path = model
            self.load_model()
            self.update_activations_data()
            self.update_selected_activation_data()
            self.number_of_heads = self.activations_data[self.selected_layer].shape[1]
            self.update_grid_shape()

    def update_layers_in_body_count(self):
        #TODO: figure out robust way to separate attention layers in body from the rest.
        heads = self.activations_data[0].shape[1]
        for ind, layer in enumerate(self.activations_data):
            print(ind, layer.shape)
            if layer.shape[1] != heads or len(layer.shape) != 4:
                ind = ind - 1
                break
        self.nr_of_layers_in_body = ind + 1
        self.selected_layer = min(self.selected_layer, self.nr_of_layers_in_body - 1)

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
        self.update_activations_data()
        self.update_selected_activation_data()

    def set_board(self, board):
        self.board = deepcopy(board)
        #self.fen = board.fen()
        #self.set_fen(board.fen())
        self.update_activations_data()
        self.update_selected_activation_data()

global_data = GlobalData()
print('global data created')