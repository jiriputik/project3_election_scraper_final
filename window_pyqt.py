"""
window_pyqt.py: doplňující soubor pro vizualizaci stažených dat skriptem scraper.py

author: Jiri Putik s dopomocí MS Copilot
email: j.putik@gmail.com
discord: peen_cz
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QSplitter, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Hlavní třída pro naši aplikaci
class MainWindow(QMainWindow):
    def __init__(self, locations_data):
        super().__init__()
        self.setWindowTitle("Elections Basic Visulisation")
        self.setGeometry(100,100,1200,800)

        self.showMaximized()

        self.data = locations_data
        self.locations = [item['location'] for item in locations_data]

    # Vytvoření hlavního widgetu
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
    
    # Vytvoření QSplitter pro horizontální rozdělení
        splitter = QSplitter(Qt.Horizontal)

    # Levé okno: QListWidget s městy a nadpis (label)
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        
        label = QLabel("Choose area here:")
        font = QFont()
        font.setPointSize(12)  # Nastavení velikosti písma v nadpisu 
        font.setBold(True)     # Nastavení písma v nadpisu na tučné
        label.setFont(font)

        self.left_widget = QListWidget()
        self.left_widget.addItems(self.locations)
        self.left_widget.currentRowChanged.connect(self.update_plot)

        left_layout.addWidget(label)
        left_layout.addWidget(self.left_widget)

    # Pravé okno: Graf

        self.right_widget = QWidget()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.right_widget.setLayout(layout)

    # Přidání widgetů do splitteru
        #splitter.addWidget(self.left_widget)
        splitter.addWidget(left_container)
        splitter.addWidget(self.right_widget)

    # Nastavení poměru velikosti
        splitter.setStretchFactor(0, 1)  # Levé okno (25 %)
        splitter.setStretchFactor(1, 3)  # Pravé okno (75 %)

    # Vytvoření layoutu pro hlavní widget
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        main_widget.setLayout(layout)
    
    # update grafu na základě výběru
    def update_plot(self, index):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        location_data = self.data[index]
        location = location_data['location']
        votes = location_data['votes']
        
        parties = list(votes.keys())
        counts = list(votes.values())
        
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow', 'black', 'pink']

        bars = ax.bar(parties, counts, color=colors[:len(parties)])  
        ax.set_title(f"Election results data visualize for area {location} (for the parties where votes > 0)")
        ax.set_xlabel("Parties")
        ax.set_ylabel("Votes")

        ax.set_xticklabels([])      # bez popisků na ose x

        ax.legend(bars, parties, loc='upper right', bbox_to_anchor=(1, 1))

        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval+.2, int(yval), ha='center', va='bottom', rotation=0)

        self.canvas.draw()

def run_app_window(locations_data):

    # aktivace okna

    app = QApplication([])  
    window = MainWindow(locations_data)
    window.show()
    window.raise_()
    window.activateWindow()
    sys.exit(app.exec_())

# Ochrana pro přímé spuštění skriptu
if __name__ == "__main__":

    # demo data
    locations_data = [
        {'location': 'Praha', 'votes': {'strana1': 10, 'strana2': 20, 'strana3': 30}},
        {'location': 'Brno', 'votes': {'strana1': 15, 'strana2': 25, 'strana3': 35}},
        {'location': 'Ostrava', 'votes': {'strana1': 5, 'strana2': 15, 'strana3': 25, 'ddd':12}},
        {'location': 'Plzeň', 'votes': {'strana1': 20, 'strana2': 30, 'strana3': 40}},
        {'location': 'Liberec', 'votes': {'strana1': 25, 'strana2': 35, 'strana3': 45}}
    ]
    run_app_window(locations_data)



