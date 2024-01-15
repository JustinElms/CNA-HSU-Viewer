from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QGridLayout,
    QPushButton,
)

from components.modal import Modal


class MineralColorSelector(Modal):
    """Mineral Color Selector window used to change the color assigned to a
    mineral.

    Signals:
        color_changed(str): Signals to update color to selected value.
    """

    update_color = Signal(str, str)

    def __init__(
        self, parent: QWidget = None, mineral: str = None, colors: list = None
    ) -> None:
        """Initialize component

        Args:
            parent(None/QWidget): The parent widget.
            colors(list): A list of colors that the user can select from.
        """
        super().__init__(parent=parent, text="Select Mineral Color", size="sm")

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.selected_color = None
        self.selected_pos = None
        self.mineral = mineral

        color_container = QWidget(self)
        self.color_container_layout = QGridLayout(color_container)

        for idx, color in enumerate(colors):
            row = int(idx / 12)
            col = int(idx % 12)
            color_button = QPushButton(color_container)
            color_button.setStyleSheet(f"background-color: {color};")
            color_button.clicked.connect(
                lambda chk=None, row=row, col=col, color=color: self.color_clicked(
                    row, col, color
                )
            )
            self.color_container_layout.addWidget(color_button, row, col)

        button_container = QWidget(self)

        apply_button = QPushButton("Apply", button_container)
        apply_button.setStyleSheet(
            "background-color: green; border: 1px solid rgb(222, 222, 222);"
        )
        apply_button.clicked.connect(self.apply_clicked)
        apply_button.setFixedWidth(40)

        cancel_button = QPushButton("Cancel", button_container)
        cancel_button.clicked.connect(self.cancel_clicked)
        cancel_button.setFixedWidth(40)

        button_container_layout = QHBoxLayout(button_container)
        button_container_layout.addStretch()
        button_container_layout.addWidget(apply_button)
        button_container_layout.addWidget(cancel_button)

        layout.addWidget(color_container)
        layout.addWidget(button_container)

        super().add_content(self)

    def color_clicked(self, row: int, col: int, color: str) -> None:
        """Highlights andupdates the currently selected color.

        Args:
            row(int): The row position of the selected color.
            co(int): The column positionof the selected color.
            color(str): The selected color'shex value.
        """
        if self.selected_color:
            button = self.color_container_layout.itemAtPosition(
                self.selected_pos[0], self.selected_pos[1]
            ).widget()
            button.setStyleSheet(
                f"background-color: {self.selected_color}; \
                border: None"
            )
        self.selected_color = color
        self.selected_pos = [row, col]
        button = self.color_container_layout.itemAtPosition(row, col).widget()
        button.setStyleSheet(
            f"background-color: {color}; \
            border: 2px solid white;"
        )

    def apply_clicked(self) -> None:
        """Emits update color signal and coloses color selector window."""
        self.update_color.emit(self.mineral, self.selected_color)
        super()._close()

    def cancel_clicked(self) -> None:
        """Closes the color selector window."""
        super()._close()
