from PySide6.QtWidgets import QApplication, QHBoxLayout, QWidget, QPushButton
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag, QPixmap

from components.data_panel import DataPanel


class DraggableContainer(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.setAcceptDrops(True)

        self.setStyleSheet("background-color: red;")

        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignTop)
        
        self.setLayout(self.layout)

    def dragEnterEvent(self, e) -> None:
        e.accept()

    def dropEvent(self, e) -> None:
        pos = e.position().toPoint()
        widget = e.source()

        for n in range(self.layout.count()):
            # TODO add functionality for outside widgets
            # Get the widget at each index in turn.
            w = self.layout.itemAt(n).widget()
            print(pos.x())
            print(w.x() + w.size().width() / 2)
            if pos.x() < w.x() + w.size().width() / 2:
                # We didn't drag past this widget.
                # insert to the left of it.
                self.layout.insertWidget(n, widget)
                break

        e.accept()

    def add_data_panel(self) -> None:  # , dataset, datatype, subtype, data) -> None:
        panel = DataPanel(self, self.geometry().height())  # dataset, datatype, subtype, data)
        self.insert_panel(panel)


    def insert_panel(self, panel: DataPanel) -> None:
        if self.layout.count() == 0:
            self.layout.addWidget(panel)
            self.layout.addStretch()
        else:
            self.layout.insertWidget(
                self.layout.count() - 1, panel
            )