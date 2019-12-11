"""
Autor: Ismael Marín Molina
This is a collection of utils methods and attributes
"""
import re
from os import path as pt
"""
Map of colors to use
"""
_COLORS_ = {
    "BLACK": [0.05, 0.05, 0.05],
    "WHITE": [0.85, 0.85, 0.85],
    "GRAY": [0.19, 0.19, 0.19]
}


def givePath(obj, home_path='./objs/'):
    """
    This method give the path of the object model that you passed as a 
    parameter
    
    Parameters
    ----------
    obj : str
        The object name or the path to use
    home_path : str, optional
        The directory to search when a name is passed, by default './objs/'
    
    Returns
    -------
    str
        The path of the object
    
    Raises
    ------
    Exception
        NotValidInput
    Exception
        FileNotExists
    """
    complete_path = re.compile('\w/+\.obj$')
    only_name = re.compile('\w*\.obj$')
    path = None

    if complete_path.match(obj):
        path = obj
    elif only_name.match(obj):
        path = home_path + obj

    if path is None:
        raise Exception("Not a valid input")
    elif not pt.exists(path):
        raise Exception("File not exists")

    return path