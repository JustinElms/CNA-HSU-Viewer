import numpy as np
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget
from PySide6.QtGui import QResizeEvent
from PySide6.QtCore import Qt, Signal, Slot

from components.data_panel import DataPanel
from components.data_header import DataHeader


class DraggableContainer(QWidget):
    """Displays data panels and headers and enables drag and drop
    functionality.

    Signals:
        widget_dragged(int, int): Begings drag action.
    """

    widget_dragged = Signal(int, int)

    def __init__(self, parent=None, header=False) -> None:
        """Initialize component

        Args:
            parent(None/QWidget): The parent widget.
            header(bool): True if this component contains DataHeaders.
        """
        super().__init__(parent=parent)
        self.setAcceptDrops(True)

        self.show_depth_marker = False

        self.depth_marker = QLabel(self)
        self.depth_marker.setFixedSize(self.width(), 2)
        self.depth_marker.setStyleSheet("background-color: rgba(255,0,0,125)")
        self.depth_marker.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.depth_marker.raise_()
        self.depth_marker.hide()

        self.layout = QHBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignTop)
        self.header = header

        self.setLayout(self.layout)

    def resizeEvent(self, event: QResizeEvent) -> None:
        if self.show_depth_marker:
            self.update_depth_marker(self.depth_marker.y())
            self.depth_marker.setFixedWidth(self.width())
        return super().resizeEvent(event)

    def dragEnterEvent(self, e) -> None:
        """Event to signal that the drag action has begun."""
        e.accept()

    def dropEvent(self, e) -> None:
        """Event to signal that the drag action has ended and to drop the
        widget in the current position.
        """
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

    def insert_panel(self, panel: DataPanel) -> None:
        """Inserts a datapanel or header at the end of the layout.

        Args:
            panel(DataPanel): The panel to be added.
        """
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
    def insert_dragged_widget(self, start_index: int, end_index: int) -> None:
        """Inserts a data panel or header at in the position given by
        end_index.

        Args:
            start_index(int): The starting position of the dragged element.
            end_index(int): The ending position of the dragged element.
        """
        widget = self.layout.itemAt(start_index).widget()
        self.layout.insertWidget(end_index, widget)

    def max_panel_depth(self) -> int:
        """Determines the maximum depth of the displayed data panels."""
        depths = []
        for i in range(self.layout.count() - 2):
            depths.append(self.layout.itemAt(i).widget().depth)
        if not depths:
            return 0
        return np.max(depths)

    def get_current_minerals(self) -> list:
        """Returns a list of unique currently displayed minerals."""
        mineral_list = []
        for i in range(self.layout.count() - 2):
            minerals = self.layout.itemAt(i).widget().data_name
            if not isinstance(minerals, list):
                mineral_list.append(minerals)
            else:
                for mineral in minerals:
                    mineral_list.append(mineral)

        return mineral_list

    @Slot(bool, int)
    def toggle_depth_marker(self, show_depth_marker: bool, y: int) -> None:
        """Toggles display of depth marker on dashboard."""
        if show_depth_marker:
            self.update_depth_marker(y)
        else:
            self.show_depth_marker = False
            self.depth_marker.hide()

    def update_depth_marker(self, y: int) -> None:
        """Updates the depth marker's position as needed.

        Args:
            y (int): The marker's new vertical position.
        """
        self.depth_marker.move(0, y)
        self.depth_marker.setFixedWidth(self.width())
        self.show_depth_marker = True
        self.depth_marker.raise_()
        self.depth_marker.show()

    def update_mineral_colors(self, mineral: str, color: str) -> None:
        """Updates the colormap ofeach panel.

        Args:
            mineral(str): The name of the mineral to be updated.
            color(str): The new color (hex).
        """        
        for i in range(self.layout.count() - 2):
            panel = self.layout.itemAt(i).widget()
            panel.update_plot_colors(mineral, color)
