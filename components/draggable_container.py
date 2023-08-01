import numpy as np
from PySide6.QtWidgets import QHBoxLayout, QWidget
from PySide6.QtCore import Qt, Signal, Slot

from components.data_panel import DataPanel
from components.data_header import DataHeader


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

        self.setLayout(self.layout)

    def dragEnterEvent(self, e) -> None:
        e.accept()

    def dropEvent(self, e) -> None:
        pos = e.position().toPoint()
        widget = e.source()
        start_index = None
        end_index = None

        for n in range(self.layout.count()):
            w = self.layout.itemAt(n).widget()
            if isinstance(w, DataHeader):
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
        if self.layout.count() == 0:
            self.layout.addWidget(panel)
            self.layout.addStretch()
            if self.header:
                self.layout.addSpacing(117)
            else:
                self.layout.addSpacing(100)
        else:
            self.layout.insertWidget(self.layout.count() - 2, panel)

    @Slot(int, int)
    def insert_dragged_widget(self, start_index, end_index):
        widget = self.layout.itemAt(start_index).widget()
        self.layout.insertWidget(end_index, widget)

    def max_panel_depth(self) -> int:
        depths = []
        for i in range(self.layout.count() - 2):
            depths.append(self.layout.itemAt(i).widget().depth)
        if not depths:
            return 0
        return np.max(depths)

    def get_current_minerals(self) -> list:
        mineral_list = []
        for i in range(self.layout.count() - 2):
            minerals = self.layout.itemAt(i).widget().data_name
            if not isinstance(minerals, list):
                mineral_list.append(minerals)
            else:
                for mineral in minerals:
                    mineral_list.append(mineral)

        return mineral_list
