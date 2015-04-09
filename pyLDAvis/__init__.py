# -*- coding: utf-8 -*-
"""
Topic Models (LDA) visualization using D3
=============================================

Functions: General Use
----------------------
:func:`prepare`
    transform and prepare a LDA model's data for visualization

:func:`prepared_data_to_html`
    convert prepared data to a html string

:func:`show`
    launch a web server to view the d3/html visualization

:func:`save_html`
    save a visualization to a standalone html file

:func:`save_json`
    save a JSON representation of a figure to file


Functions: IPython Notebook
---------------------------
:func:`display`
    display a figure in an IPython notebook

:func:`enable_notebook`
    enable automatic D3 display of prepared model data in the IPython notebook.

:func:`disable_notebook`
    disable automatic D3 display of prepared model data in the IPython notebook.
"""

__all__ = ["__version__",
           "prepare", "prepared_data_to_html",
           "display", "show", #"save_html", "save_json",
           "enable_notebook", "disable_notebook"]

__version__ = '0.1.0-git'

from ._display import *
from .prepare import prepare
