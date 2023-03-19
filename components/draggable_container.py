import numpy as np
from PySide6.QtWidgets import QHBoxLayout, QWidget
from PySide6.QtCore import Qt, Signal, Slot

from components.data_panel import DataPanel


class DraggableContainer(QWidget):
    widget_dragged = Signal(int, int)

    def __init__(self, parent=None, header=False) -> None:
        super().__init__(parent=parent)
        self.setAcceptDrops(True)

        self.layout = QHBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignTop)
        self.header = header
        self.start_idx = 0
        self.end_index = -1
        if header:
            self.start_idx = 1
            self.end_index  = -2
            start_spacer = QWidget()
            start_spacer.setFixedWidth(55)
            end_spacer = QWidget()
            end_spacer.setFixedWidth(17)
            self.layout.addWidget(start_spacer)
            self.layout.addWidget(end_spacer)

        self.setLayout(self.layout)

    def dragEnterEvent(self, e) -> None:
        e.accept()

    def dropEvent(self, e) -> None:
        pos = e.position().toPoint()
        widget = e.source()
        start_index = None
        end_index = None

        for n in range(self.layout.count() + self.end_index):
            w = self.layout.itemAt(n).widget()
            if w == e.source():
                start_index = n
            if w.x() < pos.x() and pos.x() < w.x() + w.size().width():
                end_index = n

        self.layout.insertWidget(end_index, widget)
        self.widget_dragged.emit(start_index, end_index)
        e.accept()

    def add_data_panel(self) -> None:
        panel = DataPanel(self, self.geometry().height())
        self.insert_panel(panel)

    def insert_panel(self, panel: DataPanel) -> None:
        if self.layout.count() == self.start_idx:
            self.layout.addWidget(panel)
            self.layout.addStretch()
        else:
            self.layout.insertWidget(self.layout.count() - 1, panel)

    @Slot(int, int)
    def insert_dragged_widget(self, start_index, end_index):
        widget = self.layout.itemAt(start_index).widget()
        self.layout.insertWidget(end_index, widget)

    def max_panel_depth(self) -> int:
        depths = []
        for i in range(self.layout.count() - 1):
            depths.append(self.layout.itemAt(i).widget().depth)
        if not depths:
            return 0
        return np.max(depths)
