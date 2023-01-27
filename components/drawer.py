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
        self.content_panel.setStyleSheet("background-color: red;")

        self.add_dataset_button = QPushButton("Add Dataset")

        content_panel_layout = QHBoxLayout(self.content_panel)
        content_panel_layout.addWidget(self.add_dataset_button)

        self.button_panel = QWidget(self)
        self.button_panel.setStyleSheet("background-color: blue;")
        self.button_panel.setFixedWidth(20)

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
        self.drawer_button.setText("<")
        self.drawer_button.setFixedSize(10, 500)
        self.drawer_button.clicked.connect(lambda: self._toggle_drawer())

        self.button_panel_layout = QVBoxLayout(self.button_panel)
        self.button_panel_layout.setSpacing(5)
        self.button_panel_layout.setContentsMargins(0, 20, 0, 0)
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
            # self.setFixedWidth(20)
            self.drawer_button.setText(">")
            self._expanded = False
        else:
            self.content_panel.show()
            # self.setFixedWidth(320)
            self.drawer_button.setText("<")
            self._expanded = True
