from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from components.filter_list import FilterList
from components.modal import Modal
from components.metadata_table import MetadataTable
from data.dataset import Dataset
from hsu_viewer.hsu_config import HSUConfig


class DatasetSelector(Modal):

    data_selected = Signal(dict)

    def __init__(
        self, parent: QWidget = None, config_path: Path | str = None
    ) -> None:
        super().__init__(parent=parent, text="Select Dataset")

        self.config_path = config_path

        layout = QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.hsu_config = HSUConfig(config_path)
        self.dataset = None

        self.selected_dataset = None
        self.selected_datatype = None
        self.selected_subtype = None
        self.selected_dataname = None

        info_panel = QWidget(self)
        add_dataset_button = QPushButton("Import Dataset", info_panel)
        add_dataset_button.setStyleSheet(
            "border: 1px solid rgb(222, 222, 222);"
        )
        add_dataset_button.clicked.connect(self._add_dataset)
        self.meta_table = MetadataTable(info_panel)

        button_panel = QWidget(info_panel)
        add_button = QPushButton("Add", button_panel)
        add_button.setStyleSheet(
            "background-color: green; border: 1px solid rgb(222, 222, 222);"
        )
        add_button.clicked.connect(self._add_data)
        close_button = QPushButton("Close", button_panel)
        close_button.setStyleSheet("border: 1px solid rgb(222, 222, 222);")
        close_button.clicked.connect(self._close)
        button_panel_layout = QHBoxLayout(button_panel)
        button_panel_layout.addWidget(close_button)
        button_panel_layout.addWidget(add_button)

        self.dataset_label = QLabel(info_panel)
        self.dataset_label.setFont(QFont("Arial", 18))
        self.dataset_label.setWordWrap(True)
        self.options_label = QLabel(info_panel)
        self.options_label.setFont(QFont("Arial", 12))
        self.options_label.setWordWrap(True)

        info_panel_layout = QVBoxLayout(info_panel)
        info_panel_layout.addWidget(add_dataset_button)
        info_panel_layout.addStretch()
        info_panel_layout.addWidget(self.dataset_label)
        info_panel_layout.addWidget(self.options_label)
        info_panel_layout.addWidget(self.meta_table)
        info_panel_layout.addStretch()
        info_panel_layout.addWidget(button_panel)

        self.dataset_list = FilterList(self, self._dataset_changed)
        self.datatypes_list = FilterList(self, self._datatype_changed)
        self.data_list = FilterList(
            self, self._dataname_changed, multi_select=True
        )

        self.dataset_list.set_items(self.hsu_config.datasets())

        self.dataset_list.select(0)
        self.datatypes_list.select([0, 0])
        self.data_list.select(0)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.dataset_list)
        layout.addWidget(self.datatypes_list)
        layout.addWidget(self.data_list)
        layout.addWidget(info_panel)

        self.setLayout(layout)

        super().add_content(self)

    def resize(self, width: int, height: int) -> None:
        self.background.setFixedSize(width, height)
        self.content.setMaximumWidth(width - 100)
        self.content.setMaximumHeight(height - 100)

    def _dataset_changed(self, selected: str) -> None:
        # self.selected_dataset = selected
        path = self.hsu_config.dataset_path(selected)
        self.dataset = Dataset(path)
        self.dataset_label.setText(self.selected_dataset)
        datatypes = self.dataset.data_types()
        self.datatypes_list.clear_list()
        self.datatypes_list.set_items(datatypes)
        self.datatypes_list.select([0, 0])

    def _datatype_changed(self, group: str, selected: str) -> None:
        self.selected_datatype = group
        self.selected_subtype = selected
        self.selected_data = None
        self._set_options_label()
        data = self.dataset.data_options(group, selected)
        self.data_list.clear_list()
        self.data_list.set_items(data)
        self.data_list.select(0)

    def _dataname_changed(self, selected: QListWidgetItem) -> None:
        self.selected_dataname = selected
        self._set_options_label()
        self._update_table()

    def _add_dataset(self) -> None:
        dataset_path = QFileDialog.getExistingDirectory(
            self, "Select Main Directory"
        )
        self.hsu_config.add_dataset(dataset_path)
        self.dataset_list.clear_list()
        self.dataset_list.set_items(self.hsu_config.datasets())

    def _set_options_label(self) -> None:
        self.options_label.setText(
            f"{self.selected_datatype}/\
                {self.selected_subtype}/\
                    {self.selected_dataname}"
        )

    def _update_table(self) -> None:
        if (
            self.selected_dataset
            and self.selected_datatype
            and self.selected_subtype
            and self.selected_dataname
        ):
            meta_data = self.dataset.data(
                self.selected_dataset,
                self.selected_datatype,
                self.selected_subtype,
                self.selected_dataname,
            )

            self.meta_table.add_items(meta_data)

    def _close(self) -> None:
        super()._close()

    def _add_data(self) -> None:
        meta_data = self.dataset.config
        args = {
            "dataset": self.selected_dataset,
            "datatype": self.selected_datatype,
            "datasubtype": self.selected_subtype,
            "dataname": self.selected_dataname,
            "meter_start": meta_data.get("meter_start"),
            "meter_end": meta_data.get("meter_end"),
        }
        self.data_selected.emit(args)
        super()._close()
