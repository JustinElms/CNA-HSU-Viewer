from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QWidget,
    QLabel,
)

from components.mineral_legend import MineralLegend


class Drawer(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)

        self._expanded = True

        self.content_panel = QWidget(self)
        self.content_panel.setFixedWidth(300)

        self.add_dataset_button = QPushButton("Add Data")
        self.add_dataset_button.setStyleSheet("background-color: green;")

        self.mineral_legend = MineralLegend(self)

        content_panel_layout = QVBoxLayout(self.content_panel)
        content_panel_layout.setContentsMargins(5, 20, 5, 20)
        content_panel_layout.addWidget(self.add_dataset_button)
        content_panel_layout.addStretch()
        content_panel_layout.addWidget(self.mineral_legend)
        content_panel_layout.addStretch()

        self.button_panel = QWidget(self)
        self.button_panel.setFixedWidth(30)

        self.zoom_in_button = QPushButton(self.button_panel)
        self.zoom_in_button.setIcon(QIcon(QPixmap(":/plus.svg")))
        self.zoom_in_button.setFixedSize(20, 20)
        self.zoom_in_button.setStyleSheet(
            "background-color: grey; font: bold 12pt"
        )
        self.zoom_out_button = QPushButton(self.button_panel)
        self.zoom_out_button.setIcon(QIcon(QPixmap(":/minus.svg")))
        self.zoom_out_button.setStyleSheet(
            "background-color: grey; font: bold 12pt"
        )
        self.zoom_out_button.setFixedSize(20, 20)

        # create button to toggle drawer
        self.drawer_button = QPushButton(self.button_panel)
        self.drawer_button.setIcon(
            QIcon(QPixmap(":/caret_left.svg").scaledToWidth(12))
        )
        self.drawer_button.setStyleSheet(
            "background-color: grey; font: bold 12pt"
        )
        self.drawer_button.setFixedSize(15, 500)
        self.drawer_button.clicked.connect(lambda: self._toggle_drawer())

        self.button_panel_layout = QVBoxLayout(self.button_panel)
        self.button_panel_layout.setContentsMargins(5, 20, 5, 20)
        self.button_panel_layout.addWidget(self.zoom_in_button)
        self.button_panel_layout.addWidget(self.zoom_out_button)
        self.button_panel_layout.addStretch()
        self.button_panel_layout.addWidget(self.drawer_button)
        self.button_panel_layout.addStretch()

        layout = QHBoxLayout(self)
        layout.addWidget(self.content_panel)
        layout.addWidget(self.button_panel)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

        self.setMaximumWidth(320)

    def _toggle_drawer(self):
        """
        when called toggleDrawer chanegs the size of the options drawer
        """
        if self._expanded:
            self.content_panel.hide()
            self.drawer_button.setIcon(
                QIcon(QPixmap(":/caret_right.svg").scaledToWidth(12))
            )
            self._expanded = False
        else:
            self.content_panel.show()
            self.drawer_button.setIcon(
                QIcon(QPixmap(":/caret_left.svg").scaledToWidth(12))
            )
            self._expanded = True

    def appendToLegend(self, idx) -> None:
        """
        creates entries for the mineral legend in the options drawer including
        color swatch buttons.
        keep as seperate function so that signals remain unique
        idx is the index of the mineral in minList
        """
        colorButton = QPushButton()
        colorButton.setStyleSheet(
            "background-color:"
            + self.plotColorDict[self.minList[idx]]
            + "; border: 1 px solid"
        )
        colorButton.setFixedSize(10, 10)
        colorButton.clicked.connect(lambda: self.changeMinColor(idx))
        legendLabel = QLabel(self.legendArea)
        legendLabel.setText(self.minList[idx])
        self.legendAreaLayout.addWidget(colorButton, idx, 0)
        self.legendAreaLayout.addWidget(legendLabel, idx, 1)
        self.minColorButtonGroup.addButton(colorButton)
        self.minColorButtonGroup.setId(colorButton, idx)
