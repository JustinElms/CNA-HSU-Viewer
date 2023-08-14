from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)


class LoadingPanel(QWidget):
    """An overlay that displays "Loading..." during a panel's async operation.
    """

    def __init__(self, parent=None) -> None:
        """Initialize component"""
        super().__init__(parent=parent)

        loading_label = QLabel(self)
        loading_label.setText("Loading...")

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.addStretch()
        self.layout.addWidget(loading_label)
        self.layout.addStretch()
        self.setLayout(self.layout)

    @Slot(int, int)
    def resize_panel(self, width: int, height: int) -> None:
        """Resizes the overlay."""
        self.setFixedSize(width, height)
