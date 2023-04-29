from PySide6.QtCore import Qt, QMimeData, QPoint, Signal, Slot
from PySide6.QtGui import QAction, QDrag, QPixmap, QIcon
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QPushButton,
    QMenu,
)

from data.dataset import Dataset


class DataHeader(QWidget):
    close_panel = Signal()
    save_image = Signal()

    def __init__(
        self, parent=None, width: int = None, dataset: Dataset = None, **kwargs
    ) -> None:
        super().__init__(parent=parent)

        dataset_name = kwargs.get("dataset_name")
        data_type = kwargs.get("data_type")
        data_subtype = kwargs.get("data_subtype")
        data_name = kwargs.get("data_name")

        self.csv_data = dataset.config.get("csv_data")

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
        dataset_label.setText(dataset_name)
        dataset_label.setStyleSheet(
            "background-color: transparent; \
                font: bold 10pt; border: transparent"
        )

        self.menu_button = QPushButton(title_container)
        self.menu_button.setIcon(
            QIcon(QPixmap(":/caret_down.svg").scaledToWidth(10))
        )
        self.menu_button.clicked.connect(self.show_menu)
        self.menu_button.setFixedSize(20, 20)
        self.menu_button.setStyleSheet(
            "background-color: transparent; \
                font: bold 6pt; border: transparent"
        )

        self.context_menu = QMenu(self)
        self.context_menu.setFixedWidth(width - 40)
        self.context_menu.setStyleSheet(
            "background-color: rgba(100,100,100,150)"
        )

        save_action = QAction("Save panel to image", self)
        save_action.triggered.connect(self.save_panel_image)

        self.context_menu.addAction(save_action)

        self.close_button = QPushButton(title_container)
        self.close_button.setIcon(QIcon(QPixmap(":/close.svg")))
        self.close_button.setFixedSize(20, 20)
        self.close_button.clicked.connect(self.panel_closed)
        self.close_button.setStyleSheet(
            "background-color: transparent; \
                font: bold 12pt; border: transparent"
        )

        title_container_layout.addStretch()
        title_container_layout.addWidget(dataset_label)
        title_container_layout.addStretch()
        title_container_layout.addWidget(self.menu_button)
        title_container_layout.addWidget(self.close_button)

        datatype_label = QLabel(title_container)
        datatype_label.setFixedHeight(20)
        datatype_label.setText(f"{data_type}: {data_subtype}")
        datatype_label.setToolTip(f"{data_type}: {data_subtype}")
        datatype_label.setStyleSheet(
            "background-color: transparent; \
                font: bold 10pt; border: transparent"
        )

        dataname_label = QLabel(self)
        dataname_label.setFixedHeight(20)

        dataname_label.setStyleSheet(
            "background-color: transparent; \
                font: bold 10pt; border: transparent"
        )
        if isinstance(data_name, str):
            dataname_label.setText(data_name)
            dataname_label.setToolTip(data_name)
        elif isinstance(data_name, list):
            label_text = " ".join(data_name)
            dataname_label.setText(label_text)
            dataname_label.setToolTip(label_text)

        axis_limits = self.axis_limits()
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
        axis_start_label.setText(axis_limits[0])

        # label for axis maximum
        axis_end_label = QLabel(axis_limits_container)
        axis_end_label.setFixedHeight(20)
        axis_end_label.setStyleSheet(
            "background-color: transparent; \
                font: bold 10pt; border: transparent"
        )
        axis_end_label.setText(axis_limits[1])

        axis_limits_layout.addWidget(axis_start_label)
        axis_limits_layout.addStretch()
        axis_limits_layout.addWidget(axis_end_label)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.layout.addWidget(title_container)
        self.layout.addWidget(datatype_label)
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
        self.context_menu.setFixedWidth(width)

    def panel_closed(self) -> None:
        self.close_panel.emit()
        self.deleteLater()

    def axis_limits(self) -> list:
        try:
            axis_min = self.csv_data.get("min_value")
            axis_max = self.csv_data.get("max_value")
        except ValueError:
            if self.datasubtype == "Position":
                [min, max] = self.dataname.split(" ")
                axis_min = min
                axis_max = max
            else:
                axis_min = ""
                axis_max = ""

        return [axis_min, axis_max]

    def show_menu(self):
        self.context_menu.popup(
            self.menu_button.mapToGlobal(QPoint(40 - self.width(), 20))
        )

    def save_panel_image(self) -> None:
        self.save_image.emit()
