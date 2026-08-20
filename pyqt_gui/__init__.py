# REFERENCES:
# https://medium.com/@jasonyang.algo/getting-started-with-pyqt6-a-beginner-friendly-guide-to-modern-gui-development-79924151440f
# https://pyqtgraph.readthedocs.io/en/latest/getting_started/plotting.html
# https://www.pythonguis.com/tutorials/pyqt6-layouts/#qgridlayout-widgets-arranged-in-a-grid
# https://github.com/domarm-comat/pglive
# https://medium.com/@pysquad/explore-pyserial-serial-communication-libraries-e79b32a6dfe7
# https://www.pythontutorial.net/pyqt/pyqt-qpushbutton/
# https://www.pyserial.com/docs/getting-started
# https://realpython.com/python-pyqt-qthread/
# https://www.atlassian.com/data/charts/heatmap-complete-guide
# https://www.pythonguis.com/faq/clean-up-on-exit-application/

import sys, time, csv, io, serial, pyqtgraph as pg
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from pyqtgraph import *
from pglive.sources.data_connector import *
from pglive.sources.live_plot import *
from pglive.sources.live_plot_widget import *
from pglive.sources.live_HeatMap import *
from pglive.kwargs import *
