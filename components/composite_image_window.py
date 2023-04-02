from pathlib import Path

import numpy as np
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from components.modal import Modal
from hsu_viewer.dataset_config import DatasetConfig


class CompositeImageWindow(Modal):

    # For composition images (mineral_) allow users to color minerals on their own, overlay them, and export them

    def __init__(
        self, parent: QWidget = None, config_path: Path = None
    ) -> None:
        super().__init__(parent)

        self.datasets = DatasetConfig(config_path).datasets()

        layout = QGridLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QWidget(self)
        toolbar.setStyleSheet("background-color: red;")
        toolbar.setFixedHeight(20)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setSpacing(0)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)

        dataset_combobox = QComboBox(toolbar)
        dataset_combobox.addItems(self.datasets)
        mineral_combobox = QComboBox(toolbar)
        add_button = QPushButton(toolbar)
        add_button.setText("Add")
        add_button.setStyleSheet("background-color: green;")

        toolbar_layout.addWidget(dataset_combobox)
        toolbar_layout.addWidget(mineral_combobox)
        toolbar_layout.addWidget(add_button)

        self.image_container = QWidget(self)
        self.image_container.setStyleSheet("background-color: blue;")
        self.selected_panel = QWidget(self)
        self.selected_panel.setMaximumWidth(100)
        self.selected_panel.setStyleSheet("background-color: green;")

        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(toolbar, 0, 0, 1, 2)
        layout.addWidget(self.image_container, 1, 0)
        layout.addWidget(self.selected_panel, 1, 1)

        self.setLayout(layout)

        super().add_content(self)

    def dataset_changed(self) -> None:
        return
    
    def mineral_changed(self) -> None:
        return
