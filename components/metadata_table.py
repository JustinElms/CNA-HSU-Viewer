from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
)


class MetadataTable(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)

        layout = QVBoxLayout(self)

        self.selected_dataset = None
        self.selected_datatype = None
        self.selected_subtype = None
        self.selected_dataname = None
        self.multi_data = False

        self.dataset_label = QLabel(self)
        self.dataset_label.setFont(QFont("Arial", 18))
        self.dataset_label.setWordWrap(True)
        self.options_label = QLabel(self)
        self.options_label.setFont(QFont("Arial", 12))
        self.options_label.setWordWrap(True)
        self.name_label = QLabel(self)
        self.name_label.setFont(QFont("Arial", 12))
        self.name_label.setWordWrap(True)

        self.table = QTableWidget(5, 2, self)
        self.table.setColumnCount(2)
        self.table.setWordWrap(True)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        self.table.horizontalHeader().setMaximumSectionSize(50)
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.Stretch
        )
        self.table.horizontalHeader().hide()
        self.table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.table.verticalHeader().hide()

        self.warning_container = QWidget(self)
        self.warning_container.setStyleSheet("border: 1px solid red;")
        warning_container_layer = QHBoxLayout(self.warning_container)
        exclamation_label = QLabel("!", self.warning_container)
        exclamation_label.setFont(QFont("Times", 32))
        exclamation_label.setStyleSheet("border: none; color: red;")
        warning_label = QLabel(
            "This dataset does not contain valid meter data. Assuming depth of 1m per row.",
            self.warning_container,
        )
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet("border: none; color: red;")
        warning_container_layer.addWidget(exclamation_label)
        warning_container_layer.addStretch()
        warning_container_layer.addWidget(warning_label)
        warning_container_layer.addStretch()

        layout.addWidget(self.dataset_label)
        layout.addWidget(self.options_label)
        layout.addWidget(self.name_label)
        layout.addWidget(self.warning_container)
        layout.addWidget(self.table)

    def set_label(
        self, dataset: str, data_type: str, data_subtype: str, data_name: str
    ) -> None:
        self.selected_dataset = dataset
        self.selected_datatype = data_type
        self.selected_subtype = data_subtype
        self.selected_dataname = data_name

        self.dataset_label.setText(dataset)
        self.options_label.setText(
            f"{data_type}:\
                {data_subtype}"
        )
        if not self.multi_data:
            self.name_label.setText(data_name)

    def add_items(self, config: dict, items: list = None) -> None:
        if self.multi_data:
            self.add_multi_data(config, items)
        else:
            self.add_single_data(config)

    def add_single_data(self, config: dict) -> None:
        self.table.setRowCount(5)
        self.table.setItem(0, 0, QTableWidgetItem("Dataset Path"))
        self.table.setItem(0, 1, QTableWidgetItem(config["path"]))
        self.table.setItem(1, 0, QTableWidgetItem("Data Path"))
        if self.selected_datatype == "Spectral Data":
            self.table.setItem(
                1, 1, QTableWidgetItem(config["csv_data"]["path"])
            )
        else:
            self.table.setItem(
                1,
                1,
                QTableWidgetItem(
                    config[self.selected_datatype][self.selected_subtype][
                        self.selected_dataname
                    ]["path"]
                ),
            )
        self.table.setItem(2, 0, QTableWidgetItem("Starting Depth"))
        self.table.setItem(
            2, 1, QTableWidgetItem(str(config["csv_data"]["meter_start"]))
        )
        self.table.setItem(3, 0, QTableWidgetItem("Ending Depth"))
        self.table.setItem(
            3, 1, QTableWidgetItem(str(config["csv_data"]["meter_end"]))
        )

        self.table.resizeRowsToContents()

        if config["csv_data"].get("meter_missing"):
            self.warning_container.show()
        else:
            self.warning_container.hide()

    def add_multi_data(self, config: dict, items: list) -> None:
        self.table.setRowCount(3)
        self.table.setItem(0, 0, QTableWidgetItem("Dataset Path"))
        self.table.setItem(0, 1, QTableWidgetItem(config["path"]))
        self.table.setItem(1, 0, QTableWidgetItem("Starting Depth"))
        self.table.setItem(
            1, 1, QTableWidgetItem(str(config["csv_data"]["meter_start"]))
        )
        self.table.setItem(2, 0, QTableWidgetItem("Ending Depth"))
        self.table.setItem(
            2, 1, QTableWidgetItem(str(config["csv_data"]["meter_end"]))
        )
        if items:
            items.sort()
            row_idx = 3
            for item in items:
                self.table.setRowCount(self.table.rowCount() + 2)
                data = config[self.selected_datatype][self.selected_subtype][
                    item
                ]
                mineral_item = QTableWidgetItem(data["name"])
                mineral_item.setBackground(QColor("blue"))
                self.table.setItem(row_idx, 0, mineral_item)
                self.table.setSpan(row_idx, 0, 1, 2)
                if data.get("path"):
                    self.table.setItem(
                        row_idx + 1, 0, QTableWidgetItem("Data Path")
                    )
                    self.table.setItem(
                        row_idx + 1, 1, QTableWidgetItem(data["path"])
                    )
                    row_idx = row_idx + 2
                else:
                    row_idx = row_idx + 1

    def set_multi_data(self, enabled: bool) -> None:
        self.multi_data = enabled
        if enabled:
            self.name_label.hide()
        else:
            self.name_label.show()
