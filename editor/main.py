from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class FinAsisEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FinAsis Editor")
        self.setGeometry(100, 100, 1280, 720)
        
        # Araç kutusu
        self.toolbox = QToolBox()
        self.setCentralWidget(self.toolbox)
        
        # Bileşenler
        self.components = {
            "Temel": ["NPC", "Market", "Banka", "Borsa"],
            "Görevler": ["AlımSatım", "Yatırım", "Bütçe"],
            "Arayüz": ["Panel", "Grafik", "Tablo"]
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        # Araç kutusu kategorileri
        for category, items in self.components.items():
            category_widget = QWidget()
            category_layout = QVBoxLayout()
            
            for item in items:
                btn = QPushButton(item)
                btn.setDragEnabled(True)
                category_layout.addWidget(btn)
            
            category_widget.setLayout(category_layout)
            self.toolbox.addItem(category_widget, category)

if __name__ == "__main__":
    app = QApplication([])
    editor = FinAsisEditor()
    editor.show()
    app.exec()
