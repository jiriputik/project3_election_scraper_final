"""
window_pyqt.py: additional file for election's data visualisation, 
data are scraped by the script scraper.py

author: Jiri Putik with MS Copilot help
email: j.putik@gmail.com
discord: peen_cz
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, \
QSplitter, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigCanvas


# Main class for the window

class MainWindow(QMainWindow):

    def __init__(self, locations_data):
        super().__init__()
        self.setWindowTitle("Elections Basic Visulisation")
        self.setGeometry(100,100,1200,800)

        self.showMaximized()

        self.data = locations_data
        self.locations = [item['location'] for item in locations_data]

    # Create main widget

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
    
    # Create QSplitter for horizontal split
    
        splitter = QSplitter(Qt.Horizontal)

    # Left window: QListWidget with a label and city names

        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        
        label = QLabel("Choose area here:")
        font = QFont()
        font.setPointSize(12)  # set font size in label
        font.setBold(True)     # set font bold in label
        label.setFont(font)

        self.left_widget = QListWidget()
        self.left_widget.addItems(self.locations)
        self.left_widget.currentRowChanged.connect(self.update_plot)

        left_layout.addWidget(label)
        left_layout.addWidget(self.left_widget)

    # Right window: Matplotlib canvas

        self.right_widget = QWidget()
        self.figure = Figure()
        self.canvas = FigCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.right_widget.setLayout(layout)

    # Adding widgets to the splitter
        
        splitter.addWidget(left_container)
        splitter.addWidget(self.right_widget)

    # Set stretch factors for the splitter

        splitter.setStretchFactor(0, 1)  # Left part (25 %)
        splitter.setStretchFactor(1, 3)  # Right part (75 %)

    # Set layout for the main widget

        layout = QVBoxLayout()
        layout.addWidget(splitter)
        main_widget.setLayout(layout)
    
    # Initial plot and plot update
        
    def update_plot(self, index):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        location_data = self.data[index]
        location = location_data['location']
        votes = location_data['votes']
        
        parties = list(votes.keys())
        counts = list(votes.values())
        
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan',
                 'magenta', 'yellow', 'black', 'pink']

        bars = ax.bar(parties, counts, color=colors[:len(parties)])  
        ax.set_title(f"Election results data visualize for area {location} \
(for the parties where votes > 0)")
        ax.set_xlabel("Parties")
        ax.set_ylabel("Votes")

        ax.set_xticklabels([])      # no x-axis labels

        ax.legend(bars, parties, loc='upper right', bbox_to_anchor=(1, 1))

        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, 
                    yval+.2, int(yval), ha='center', va='bottom', rotation=0)

        self.canvas.draw()


def run_app_window(locations_data):
    # window activation
    app = QApplication([])  
    window = MainWindow(locations_data)
    window.show()
    window.raise_()
    window.activateWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":

    # demo data
    locations_data = [
    {'location': 'Praha', 'votes': {'name1': 10, 'name2': 20, 'name3': 30}},
    {'location': 'Brno', 'votes': {'name1': 15, 'name2': 25, 'name3': 35}},
    {'location': 'Ostrava', 'votes': {'name1': 5, 'name2': 7, 'name3': 12}},
    {'location': 'Plzeň', 'votes': {'name1': 20, 'name2': 30, 'name3': 40}},
    {'location': 'Liberec', 'votes': {'name1': 25, 'name2': 35, 'name3': 45}}
    ]
    run_app_window(locations_data)



