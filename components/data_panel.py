from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QMimeData, Slot
from PySide6.QtGui import QDrag, QPixmap

from hsu_viewer.dataset_config import DatasetConfig


class DataPanel(QWidget):
    def __init__(self, parent=None, height=500, text=None, **kwargs) -> None:  # self, dataset, datatype, subtype, data, parent=None, **kwargs) -> None:
        super().__init__(parent=parent)

        self.setFixedHeight(height)
        self.setFixedWidth(120)

        self.setStyleSheet("background-color: blue;")

        self.text = text
        label = QLabel(self)
        label.setText(text)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.layout.addWidget(label)

    def plot(self):
        return

    def load_data(self):
        return
