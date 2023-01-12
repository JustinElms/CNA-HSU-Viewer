from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag, QPixmap


class DataHeader(QWidget):


    def __init__(self, parent=None, text=None) -> None:
        super().__init__(parent=parent)

        self.setFixedHeight(60)
        self.setFixedWidth(120)

        self.setStyleSheet("background-color: blue;")

        label = QLabel(self)
        label.setText(text)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.layout.addWidget(label)

    def mouseMoveEvent(self, e) -> None:

        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.exec(Qt.MoveAction)

