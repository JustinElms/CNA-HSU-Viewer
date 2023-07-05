from PySide6.QtCore import Qt, QMimeData, QPoint, Signal, Slot
from PySide6.QtGui import (
    QAction,
    QDrag,
    QPixmap,
    QIcon,
    QColor,
    QPainter,
    QFont,
    QFontMetrics,
)
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
        self.data_type = kwargs.get("data_type")
        self.data_subtype = kwargs.get("data_subtype")
        self.data_name = kwargs.get("data_name")

        self.dataset_info = dataset.data(
            self.data_type, self.data_subtype, self.data_name
        )

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
        if width > 40:
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
        datatype_label.setText(f"{self.data_type}: {self.data_subtype}")
        datatype_label.setToolTip(f"{self.data_type}: {self.data_subtype}")
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
        if isinstance(self.data_name, str):
            dataname_label.setText(self.data_name)
            dataname_label.setToolTip(self.data_name)
        elif isinstance(self.data_name, list):
            label_text = " ".join(self.data_name)
            dataname_label.setText(label_text)
            dataname_label.setToolTip(label_text)

        self.axis_limits = self.get_axis_limits()
        self.axis_unit = self.get_axis_unit()
        self.axis_limits_label = QLabel(self)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.layout.addWidget(title_container)
        self.layout.addWidget(datatype_label)
        self.layout.addWidget(dataname_label)
        self.layout.addWidget(self.axis_limits_label)

        self.setFixedSize(width, 80)

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
        self.draw_axis_scale(width)
        self.context_menu.setFixedWidth(width)

    def panel_closed(self) -> None:
        self.close_panel.emit()
        self.deleteLater()

    def get_axis_limits(self) -> list:
        try:
            axis_min = float(self.dataset_info.get("min_value"))
            axis_max = float(self.dataset_info.get("max_value"))
            if (
                self.data_subtype == "Mineral Percent"
                or self.data_subtype == "Chemistry"
            ):
                axis_min = axis_min * 100
                axis_max = axis_max * 100
        except TypeError:
            axis_min = None
            axis_max = None

        return [axis_min, axis_max]

    def get_axis_unit(self) -> str:
        unit = self.dataset_info.get("unit")

        if unit == "percent" or self.data_subtype == "Composite Plot":
            unit = "%"
            if self.axis_limits[0] and self.axis_limits[1]:
                self.axis_limits = [
                    float(limit) * 100 for limit in self.axis_limits
                ]
        elif unit == "nanometer":
            unit = "nm"

        return unit

    def update_axis_limits(self, new_axis_limits: list) -> None:
        self.axis_limits = new_axis_limits
        if self.axis_unit == "%" or self.data_subtype == "Composite Plot":
            self.axis_limits = [limit * 100 for limit in self.axis_limits]
        self.draw_axis_scale(self.width())

    def show_menu(self):
        self.context_menu.popup(
            self.menu_button.mapToGlobal(QPoint(40 - self.width(), 20))
        )

    def save_panel_image(self) -> None:
        self.save_image.emit()

    def draw_axis_scale(self, width: int) -> None:
        pixmap = QPixmap(width, 20)

        qp = QPainter(pixmap)  # initiate painter
        qp.setBrush(QColor(0, 0, 0))  # paint meter background black
        qp.drawRect(0, 0, width, 20)
        qp.setBrush(QColor(222, 222, 222))  # set color for ticks and text
        qp.setPen(QColor(222, 222, 222))
        qp.drawRect(0, 0, 1, 20)
        qp.drawRect(width - 2, 0, 1, 20)
        qp.drawRect(int(width / 2), 10, 0.5, 10)

        if self.axis_limits[0] is not None and self.axis_limits[1] is not None:
            font_metric = QFontMetrics(QFont())
            axis_limit_str = [
                f"{limit:.2f} {self.axis_unit}" for limit in self.axis_limits
            ]
            right_label_width = font_metric.size(
                Qt.TextSingleLine, axis_limit_str[1]
            ).width()

            qp.drawText(5, 15, axis_limit_str[0])
            qp.drawText(width - right_label_width - 5, 15, axis_limit_str[1])

        qp.end()

        self.axis_limits_label.setPixmap(pixmap)
