from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QPushButton,
)
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag, QPixmap


class DataHeader(QWidget):
    close_panel = Signal()

    def __init__(self, parent=None, width: int = None, **kwargs) -> None:
        super().__init__(parent=parent)

        dataset = kwargs.get("dataset")
        dataname = kwargs.get("dataname")

        title_container = QWidget(self)
        title_container.setFixedHeight(20)
        title_container.setStyleSheet(
            "Background-Color: rgba(100,100,100,150)"
        )
        title_container_layout = QHBoxLayout(title_container)
        title_container_layout.setSpacing(0)
        title_container_layout.setContentsMargins(0, 0, 0, 0)

        dataset_label = QLabel(title_container)
        dataset_label.setFixedHeight(20)
        dataset_label.setText(dataset)
        dataset_label.setStyleSheet(
            "background-color: transparent; \
                font: bold 10pt; border: transparent"
        )

        self.close_button = QPushButton(title_container)
        self.close_button.setText("×")
        self.close_button.setFixedSize(20, 20)
        self.close_button.clicked.connect(self.panel_closed)
        self.close_button.setStyleSheet(
            "background-color: transparent; \
                font: bold 12pt; border: transparent"
        )

        title_container_layout.addStretch()
        title_container_layout.addWidget(dataset_label)
        title_container_layout.addStretch()
        title_container_layout.addWidget(self.close_button)

        dataname_label = QLabel(self)
        dataname_label.setFixedHeight(20)
        dataname_label.setText(dataname)
        dataname_label.setStyleSheet(
            "background-color: transparent; \
                font: bold 10pt; border: transparent"
        )

        # area for axis limits
        axis_limits_container = QWidget(self)
        axis_limits_container.setFixedHeight(20)
        axis_limits_layout = QHBoxLayout(axis_limits_container)
        axis_limits_layout.setSpacing(0)
        axis_limits_layout.setContentsMargins(0, 0, 0, 0)

        # label for axis minimum
        axis_start_label = QLabel(axis_limits_container)
        axis_start_label.setFixedHeight(20)
        axis_start_label.setStyleSheet(
            "background-color: transparent; \
                font: bold 10pt; border: transparent"
        )
        axis_start_label.setText("0")  # str(axis_limits[0]))

        # label for axis maximum
        axis_end_label = QLabel(axis_limits_container)
        axis_end_label.setFixedHeight(20)
        axis_end_label.setStyleSheet(
            "background-color: transparent; \
                font: bold 10pt; border: transparent"
        )
        axis_end_label.setText("1")  # str(axis_limits[1]))

        axis_limits_layout.addWidget(axis_start_label)
        axis_limits_layout.addStretch()
        axis_limits_layout.addWidget(axis_end_label)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.layout.addWidget(title_container)
        self.layout.addWidget(dataname_label)
        self.layout.addWidget(axis_limits_container)

        self.setFixedSize(width, 60)

    def mouseMoveEvent(self, e) -> None:

        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.exec(Qt.MoveAction)

    @Slot(int)
    def resize_header(self, width: int) -> None:
        self.setFixedWidth(width)

    def panel_closed(self):
        self.close_panel.emit()
        self.deleteLater()
