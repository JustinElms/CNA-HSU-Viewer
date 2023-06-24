from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)


class LoadingPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)

        spinner = QMovie(":/loading.gif")

        loading_label = QLabel(self)
        loading_label.setText("Loading...")

        spinner.start()

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.addStretch()
        self.layout.addWidget(loading_label)
        self.layout.addStretch()
        self.setLayout(self.layout)

    @Slot(int, int)
    def resize_panel(self, width: int, height: int) -> None:
        self.setFixedSize(width, height)
