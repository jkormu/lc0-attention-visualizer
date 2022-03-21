import sys
import os

def root_directory():
    if getattr(sys, 'frozen', False):
        # The application is frozen
        root = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        root = os.path.dirname(__file__)#os.path.dirname(os.path.abspath(__file__))#os.path.dirname(__file__)
    return(root)

ROOT_DIR = root_directory()