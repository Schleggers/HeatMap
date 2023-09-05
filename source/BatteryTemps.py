from PyQt5.QtWidgets import QApplication
from interface import HeatmapApp
import sys

# TODO:
# - make sure that every csv file hase the same structure (same column and rows for the data)
# - figure out why some columns doesn't follow the right order cuz it's kinda weird tbh

if __name__ == '__main__':
    app = QApplication([])
    ex = HeatmapApp()
    ex.show()
    sys.exit(app.exec_())