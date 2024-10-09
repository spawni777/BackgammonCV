import os
from flask import current_app

def get_full_path(relative_path):
    """Converts a relative path to a full path using the stored root path."""
    root_path = current_app.config['ROOT_PATH']
    full_path = os.path.join(root_path, relative_path)
    return full_path