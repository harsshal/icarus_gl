import sys
import os

def add_to_sys_path(path_str):
    # Get the parent directory and add it to sys.path
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), path_str))
    sys.path.insert(0, parent_dir)

add_to_sys_path('../ibapi')