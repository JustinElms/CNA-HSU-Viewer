from pathlib import Path

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QCheckBox,
    QFileDialog,
)

from components.modal import Modal


class SavePanelWindow(Modal):
    def __init__(
        self,
        parent: QWidget,
        panel_image: QPixmap,
        meter_image: QPixmap,
        image_name: str,
    ) -> None:
        super().__init__(parent=parent, text="Save Panel Image", size="sm")

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

        self.default_image_path = (
            f"{Path().absolute().as_posix()}/{image_name}"
        )
        self.meter_image = meter_image
        self.panel_image = panel_image

        fname_container = QWidget(self)
        fname_container_layout = QHBoxLayout(fname_container)

        self.image_name_label = QLineEdit(
            self.default_image_path, fname_container
        )
        browse_button = QPushButton("Browse", fname_container)
        browse_button.clicked.connect(self.set_path)
        browse_button.setFixedWidth(50)
        browse_button.setStyleSheet("border: 1px solid white;")

        fname_container_layout.addWidget(self.image_name_label)
        fname_container_layout.addWidget(browse_button)

        button_container = QWidget(self)
        button_container_layout = QHBoxLayout(button_container)

        save_button = QPushButton("Save", button_container)
        save_button.clicked.connect(self.save_image)
        save_button.setFixedWidth(50)
        save_button.setStyleSheet(
            "background-color: green;  border: 1px solid white;"
        )
        close_button = QPushButton("Close", button_container)
        close_button.clicked.connect(self._close)
        close_button.setStyleSheet("border: 1px solid white;")
        close_button.setFixedWidth(50)

        self.meter_checkbox = QCheckBox(button_container)
        meter_label = QLabel("Include Meter", button_container)

        button_container_layout.addWidget(self.meter_checkbox)
        button_container_layout.addWidget(meter_label)
        button_container_layout.addStretch()
        button_container_layout.addWidget(save_button)
        button_container_layout.addWidget(close_button)

        layout.addWidget(fname_container)
        layout.addWidget(button_container)

        super().add_content(self)

    def set_path(self) -> None:
        new_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save As",
            self.default_image_path,
            "Images (*.png *.bmp *.jpg *.jpeg)",
        )

        if new_path:
            self.image_name_label.setText(new_path)

    def save_image(self) -> None:
        if self.meter_checkbox.isChecked():
            temp_widget = QWidget()
            temp_layout = QHBoxLayout(temp_widget)
            meter_label = QLabel(temp_widget)
            meter_label.setPixmap(self.meter_image)
            panel_label = QLabel(temp_widget)
            panel_label.setPixmap(self.panel_image)
            temp_layout.addWidget(meter_label)
            temp_layout.addWidget(panel_label)

            temp_widget.setFixedWidth(
                self.meter_image.width() + self.panel_image.width()
            )
            temp_widget.setFixedHeight(self.panel_image.height())
            temp_layout.setSpacing(0)
            temp_layout.setContentsMargins(0, 0, 0, 0)
            temp_widget.grab(temp_widget.rect()).save(
                self.image_name_label.text()
            )
        else:
            self.panel_image.save(self.image_name_label.text())

        self._close()

    def _close(self) -> None:
        super()._close()
