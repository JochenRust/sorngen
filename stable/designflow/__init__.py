import os

def is_standalone():
    return os.getenv('standalone', False) == 'true'