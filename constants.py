import sys
import os


def root_directory():
    if getattr(sys, 'frozen', False):
        # The application is frozen
        root = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        root = os.path.dirname(__file__)  # os.path.dirname(os.path.abspath(__file__))#os.path.dirname(__file__)
    return (root)


ROOT_DIR = root_directory()

LEFT_PANE_WIDTH = 90
RIGHT_PANE_WIDTH = 100 - LEFT_PANE_WIDTH
GRAPH_PANE_HEIGHT = 100
HEADER_HEIGHT = 11
CONTENT_HEIGHT = 100 - HEADER_HEIGHT

EXPORT_FORMAT = 'png' #one of png, svg, jpeg, webp
EXPORT_SCALE = 1.0 #When 1.0, the figure is exported as same size as currently in the browser. Use e.g. 0.5 to scale to half.