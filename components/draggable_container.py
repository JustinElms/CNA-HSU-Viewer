from PySide6.QtWidgets import  QHBoxLayout, QWidget
from PySide6.QtCore import Qt, Signal, Slot

from components.data_panel import DataPanel


class DraggableContainer(QWidget):
    widget_dragged = Signal(int, int)

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
        start_index = None
        end_index = None

        for n in range(self.layout.count()-1):
            w = self.layout.itemAt(n).widget()
            if w == e.source():
                start_index = n
            if w.x() < pos.x() and pos.x() < w.x() + w.size().width():
                # We didn't drag past this widget.
                # Insert to the left of it.
                end_index = n

        self.layout.insertWidget(end_index, widget)
        self.widget_dragged.emit(start_index, end_index)
        e.accept()

    def add_data_panel(self) -> None:
        panel = DataPanel(self, self.geometry().height())
        self.insert_panel(panel)


    def insert_panel(self, panel: DataPanel) -> None:
        if self.layout.count() == 0:
            self.layout.addWidget(panel)
            self.layout.addStretch()
        else:
            self.layout.insertWidget(
                self.layout.count() - 1, panel
            )

    @Slot(int, int)
    def insert_dragged_widget(self, start_index, end_index):
        widget = self.layout.itemAt(start_index).widget()
        self.layout.insertWidget(end_index, widget)

