from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QGridLayout,
    QPushButton,
    QLabel,
)

from data.colormap import hsu_colormap


class MineralLegend(QWidget):
    """A legend that displays the assigned color of each mineral displayed in
    the applicaiton.

    Signals:
        color_clicked(dict): Opens the mineral color selection window.
    """

    color_clicked = Signal(str, dict)

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)

        title = QLabel("Mineral Legend", self)
        self.colormap = {}

        layout = QVBoxLayout(self)

        self.legend_container = QWidget(self)
        self.legend_container_layout = QGridLayout(self.legend_container)

        layout.addWidget(title)
        layout.addWidget(self.legend_container)

    def add_minerals(self, minerals: list | str) -> None:
        """Adds new minerals to the legend.

        Args:
            minerals(list|str): Minerals to be added to the legend.
        """
        if not isinstance(minerals, list):
            minerals = [minerals]

        current_minerals = list(self.colormap.keys())
        available_colors = self._available_colors()

        idx = 0
        for mineral in minerals:
            if mineral not in current_minerals:
                mineral_color = available_colors[idx]
                self.colormap[mineral] = mineral_color

                idx = idx + 1
                row_count = self.legend_container_layout.rowCount() + 1

                color_button = QPushButton(self.legend_container)
                color_button.setStyleSheet(
                    f"background-color: {mineral_color}; \
                        border: 1 px solid"
                )
                color_button.clicked.connect(
                    lambda chk=None, mineral=mineral: self.show_color_selector(
                        mineral
                    )
                )
                color_button.setFixedSize(10, 10)
                mineral_label = QLabel(self.legend_container)
                mineral_label.setText(mineral)
                self.legend_container_layout.addWidget(
                    color_button, row_count, 0
                )
                self.legend_container_layout.addWidget(
                    mineral_label, row_count, 1
                )

    def remove_mineral(self, mineral: str) -> None:
        """Removes a mineral from the legend.

        Args:
            minerals(str): Minerals to be removed from the legend.
        """
        self.colormap.pop(mineral)

        for idx in range(self.legend_container_layout.rowCount()):
            item = self.legend_container_layout.itemAtPosition(idx, 1)
            if item and item.widget().text() == mineral:
                self.legend_container_layout.itemAtPosition(
                    idx, 0
                ).widget().deleteLater()
                self.legend_container_layout.itemAtPosition(
                    idx, 1
                ).widget().deleteLater()

    def color(self, minerals: str | list) -> str:
        """Returns the color currently assigned to one or more minerals.

        Args:
            minerals(str|list): A list of minerals to fetch colors for.
        """
        if isinstance(minerals, str):
            minerals = [minerals]

        colors = {}
        for mineral in minerals:
            colors[mineral] = self.colormap.get(mineral)
        return colors

    def _available_colors(self) -> list:
        """Returns a list of colors that have not yet been assigned to a
        mineral.
        """
        current_colors = list(self.colormap.values())
        return [color for color in hsu_colormap if color not in current_colors]

    def show_color_selector(self, mineral: str) -> None:
        colors = self._available_colors()
        self.color_clicked.emit(mineral, colors)

    def update_mineral_colors(self, mineral: str, color: str) -> None:
        self.colormap[mineral] = color
        for row in range(self.legend_container_layout.rowCount()):
            label = self.legend_container_layout.itemAtPosition(row, 1)
            print(type(label))
            if label and label.widget().text() == mineral:
                button = self.legend_container_layout.itemAtPosition(
                    row, 0
                ).widget()
                button.setStyleSheet(
                    f"background-color: {color}; \
                        border: 1 px solid"
                )
