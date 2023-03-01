from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QWidget,
)


class Drawer(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)

        self._expanded = True

        self.content_panel = QWidget(self)
        self.content_panel.setFixedWidth(300)

        self.add_dataset_button = QPushButton("Add Data")
        self.add_dataset_button.setStyleSheet("background-color: green;")

        content_panel_layout = QVBoxLayout(self.content_panel)
        content_panel_layout.setContentsMargins(5, 20, 5, 20)
        content_panel_layout.addWidget(self.add_dataset_button)
        content_panel_layout.addStretch()

        self.button_panel = QWidget(self)
        self.button_panel.setFixedWidth(30)

        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.setFixedSize(20, 20)
        self.zoom_in_button.setStyleSheet(
            "background-color: grey; font: bold 12pt"
        )
        self.zoom_out_button = QPushButton("-")
        self.zoom_out_button.setStyleSheet(
            "background-color: grey; font: bold 12pt"
        )
        self.zoom_out_button.setFixedSize(20, 20)

        # create button to toggle drawer
        self.drawer_button = QPushButton(self.button_panel)
        self.drawer_button.setText("⟨")
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
            self.drawer_button.setText("⟩")
            self._expanded = False
        else:
            self.content_panel.show()
            self.drawer_button.setText("⟨")
            self._expanded = True
