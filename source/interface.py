# from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, QCheckBox, QLineEdit, QGridLayout
# from PyQt5.QtCore import Qt, QTimer
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from PyQt5.QtWidgets import QTabWidget, QTextEdit  # New import for tabs
# import matplotlib.pyplot as plt
# from PyQt5.QtWidgets import QSizePolicy

# from heatmap import Heatmap

# class HeatmapApp(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         self.title = "Heatmap Viewer"
#         self.left = 10
#         self.top = 30
#         self.width = 1920
#         self.height = 1000
#         self.auto_advance = False

#         self.initUI()

#     def initUI(self):
#         self.setWindowTitle(self.title)
#         self.setGeometry(self.left, self.top, self.width, self.height)

#         self.central_widget = QWidget()
#         self.setCentralWidget(self.central_widget)

#         self.layout = QGridLayout()
#         self.central_widget.setLayout(self.layout)

#         self.heatmap = Heatmap()

#         self.fig, self.axs = self.heatmap.show_time(None, 1)
#         self.canvas = FigureCanvas(self.fig)
#         self.layout.addWidget(self.canvas, 0, 0, 1, 5)

#         self.time_slider = QSlider(Qt.Horizontal)
#         self.layout.addWidget(self.time_slider, 1, 0, 1, 1)

#         self.play_button = QPushButton("Play")
#         self.layout.addWidget(self.play_button, 1, 1, 1, 1)

#         self.avg_cb = QCheckBox("Show Average")
#         self.layout.addWidget(self.avg_cb, 1, 2, 1, 1)

#         # Replacing Auto-Advance with Show Numbers
#         self.show_numbers_cb = QCheckBox("Show Numbers")
#         self.layout.addWidget(self.show_numbers_cb, 1, 3, 1, 1)

#         self.go_to_frame_edit = QLineEdit()
#         self.go_to_frame_edit.setFixedWidth(50)
#         self.layout.addWidget(QLabel("Go to Frame:"), 1, 4)
#         self.layout.addWidget(self.go_to_frame_edit, 1, 5)

#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.advance_frame)

#         self.play_button.clicked.connect(self.toggle_play)
#         self.avg_cb.stateChanged.connect(self.show_average)
#         self.time_slider.valueChanged.connect(self.update_frame)
#         self.go_to_frame_edit.returnPressed.connect(self.jump_to_frame)
#         self.show_numbers_cb.stateChanged.connect(self.toggle_numbers)  # Connect to a new function to handle checkbox

#         self.show()

#     # New function to toggle numbers
#     def toggle_numbers(self):
#         self.heatmap.toggle_numbers(self.show_numbers_cb.isChecked())

#     def toggle_play(self):
#         if self.timer.isActive():
#             self.timer.stop()
#             self.play_button.setText("Play")
#             self.auto_advance = False
#         else:
#             self.timer.start(200)
#             self.play_button.setText("Pause")
#             self.auto_advance = True

#     def toggle_numbers(self):
#         self.heatmap.toggle_numbers(self.show_numbers_cb.isChecked())
#         self.update_frame()

#     def show_average(self):
#         self.update_frame()

#     def advance_frame(self):
#         if self.auto_advance:
#             current_value = self.time_slider.value()
#             if current_value < self.time_slider.maximum():
#                 self.time_slider.setValue(current_value + 1)

#     def update_frame(self):
#         frame_number = self.time_slider.value()

#         if self.avg_cb.isChecked():

#             self.heatmap.show_time(self.axs)
#         else:
#             self.heatmap.show_time(self.axs, frame_number)
#         self.canvas.draw_idle()

#     def jump_to_frame(self):
#         frame_number = int(self.go_to_frame_edit.text())
#         self.time_slider.setValue(frame_number)


from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, QCheckBox, QLineEdit, QGridLayout
from PyQt5.QtWidgets import QFileDialog, QPushButton, QStackedWidget, QVBoxLayout, QInputDialog
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QTabWidget, QTextEdit  # New import for tabs
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QSizePolicy

# TODO:
#   - ajouter l'option de modifier le scale (penser comment faire le layout) -> ouvre une fenetre OK
#   - ajouter un onglet statistique pour voir les stats OK
#       - faire un menu pour sélection quels groupe de donnée voir OK
#       - pour chaque groupe de donné, mettre les option de sélection nécessaire OK



from heatmap import Heatmap

class HeatmapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.title = "Heatmap Viewer"
        self.left = 10
        self.top = 30
        self.width = 1920
        self.height = 1000

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
    
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
    
        self.layout = QVBoxLayout()  # Changed to QVBoxLayout for easier management
        self.central_widget.setLayout(self.layout)
    
        # File Selection Button
        self.select_file_button = QPushButton("Select File")
        self.select_file_button.clicked.connect(self.select_file)
        self.layout.addWidget(self.select_file_button)
    
        # Stacked Widget to switch between Statistics and Heatmap
        self.stacked_widget = QStackedWidget()
    
        # Statistics UI
        self.statistics_text = QTextEdit()
        self.statistics_text.setReadOnly(True)
        self.stacked_widget.addWidget(self.statistics_text)
    
        # Heatmap UI
        self.heatmap_widget = QWidget()
        self.heatmap_layout = QGridLayout()  # The heatmap layout is grid-based
        self.heatmap_widget.setLayout(self.heatmap_layout)
    
        self.time_slider = QSlider(Qt.Horizontal)
        self.heatmap = Heatmap()
        self.select_file()
    
        self.fig, self.axs = self.heatmap.show_time(None, 0)
        self.canvas = FigureCanvas(self.fig)
        self.heatmap_layout.addWidget(self.canvas, 0, 0, 1, 5)
    
        self.heatmap_layout.addWidget(self.time_slider, 1, 0, 1, 1)
    
        self.play_button = QPushButton("Play")
        self.heatmap_layout.addWidget(self.play_button, 1, 1, 1, 1)
    
        self.avg_cb = QCheckBox("Show Average")
        self.heatmap_layout.addWidget(self.avg_cb, 1, 2, 1, 1)
    
        self.show_numbers_cb = QCheckBox("Show Numbers")
        self.heatmap_layout.addWidget(self.show_numbers_cb, 1, 3, 1, 1)
    
        self.go_to_frame_edit = QLineEdit()
        self.go_to_frame_edit.setFixedWidth(50)
        self.heatmap_layout.addWidget(QLabel("Go to Frame:"), 1, 4)
        self.heatmap_layout.addWidget(self.go_to_frame_edit, 1, 5)
    
        self.scale_button = QPushButton("Set Scale")
        self.scale_button.clicked.connect(self.set_scale)
        self.heatmap_layout.addWidget(self.scale_button, 2, 0, 1, 1)  # Added this line for scale button
    
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advance_frame)
        
        # Connect buttons and sliders to their slots
        self.play_button.clicked.connect(self.toggle_play)
        self.avg_cb.stateChanged.connect(self.show_average)
        self.time_slider.valueChanged.connect(self.update_frame)
        self.go_to_frame_edit.returnPressed.connect(self.jump_to_frame)
        self.show_numbers_cb.stateChanged.connect(self.toggle_numbers)
    
        self.stacked_widget.addWidget(self.heatmap_widget)
        self.layout.addWidget(self.stacked_widget)
    
        # Buttons to switch between Statistics and Heatmap
        self.statistics_button = QPushButton("Show Statistics")
        self.statistics_button.clicked.connect(self.show_statistics)
    
        self.heatmap_button = QPushButton("Show Heatmap")
        self.heatmap_button.clicked.connect(self.show_heatmap)
    
        self.layout.addWidget(self.statistics_button)
        self.layout.addWidget(self.heatmap_button)
    
        self.show()
    

    def select_file(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Select File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if fileName:
            self.heatmap.load_file(fileName)  # Assuming that the Heatmap class has a load_file method
            self.time_slider.setMaximum(self.heatmap.df.shape[0]-1)



    def show_statistics(self):
        stat, ok = QInputDialog.getItem(self, "Select Statistics", "Options:", ["Global Stats", "Time Stats", "Module Stats", "Sensor Stats"], 0, False)
        if ok:
            if stat == "Global Stats":
                self.statistics_text.setText(self.heatmap.show_global_stats())  # or handle this differently
            elif stat == "Time Stats":
                time, ok = QInputDialog.getInt(self, "Input", "Enter Time:", 0, 0, self.heatmap.df.shape[0]-1, 1)
                if ok:
                     self.statistics_text.setText(self.heatmap.show_time_stats(int(time)))
            elif stat == "Module Stats":
                module, ok = QInputDialog.getInt(self, "Input", "Enter Module:", 1, 1, 8, 1)
                if ok:
                     self.statistics_text.setText(self.heatmap.show_module_stats(int(module)))
            elif stat == "Sensor Stats":
                module, ok1 = QInputDialog.getInt(self, "Input", "Enter Module:", 1, 1, 8, 1)
                sensor, ok2 = QInputDialog.getInt(self, "Input", "Enter Sensor:", 1, 1, 32, 1)
                if ok1 and ok2:
                     self.statistics_text.setText(self.heatmap.show_sensor_stats(int(module), int(sensor)))
        
        self.stacked_widget.setCurrentIndex(0)  # Assuming the statistics UI is at index 0

    def show_heatmap(self): 
        self.stacked_widget.setCurrentIndex(1)  # Assuming the heatmap UI is at index 1
        
    def set_scale(self):
        scale, ok = QInputDialog.getItem(self, "Select Scale", "Options:", ["Custom Scale", "Scale to Time", "Scale to Avg"], 0, False)
        if ok:
            if scale == "Custom Scale":
                min_val, ok1 = QInputDialog.getInt(self, "Input", "Min Value:", 0, 0, 100, 1)
                max_val, ok2 = QInputDialog.getInt(self, "Input", "Max Value:", 100, 0, 100, 1)
                if ok1 and ok2:
                    self.heatmap.set_scale(int(min_val), int(max_val))
            elif scale == "Scale to Time":
                time, ok = QInputDialog.getInt(self, "Input", "Enter Time:", 0, 0, self.heatmap.df.shape[0]-1, 1)
                if ok:
                    self.heatmap.set_scale_to_data(int(time))
            elif scale == "Scale to Avg":
                offset, ok = QInputDialog.getInt(self, "Input", "Offset:", 0, 0, 100, 1)
                if ok:
                    self.heatmap.set_scale_to_avg(int(offset))
        self.update_frame()
    

    # New function to toggle numbers
    def toggle_numbers(self):
        self.heatmap.toggle_numbers(self.show_numbers_cb.isChecked())

    def toggle_play(self):
        if self.timer.isActive():
            self.timer.stop()
            self.play_button.setText("Play")
            self.auto_advance = False
        else:
            self.timer.start(200)
            self.play_button.setText("Pause")
            self.auto_advance = True

    def toggle_numbers(self):
        self.heatmap.toggle_numbers(self.show_numbers_cb.isChecked())
        self.update_frame()

    def show_average(self):
        self.update_frame()

    def advance_frame(self):
        if self.auto_advance:
            current_value = self.time_slider.value()
            if current_value < self.time_slider.maximum():
                self.time_slider.setValue(current_value + 1)

    def update_frame(self):
        frame_number = self.time_slider.value()

        if self.avg_cb.isChecked():

            self.heatmap.show_time(self.axs)
        else:
            self.heatmap.show_time(self.axs, frame_number)
        self.canvas.draw_idle()

    def jump_to_frame(self):
        frame_number = int(self.go_to_frame_edit.text())
        self.time_slider.setValue(frame_number)