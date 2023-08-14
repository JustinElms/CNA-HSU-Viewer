from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QCheckBox,
)

from components.filter_list import FilterList
from components.modal import Modal
from components.metadata_table import MetadataTable
from data.dataset import Dataset
from hsu_viewer.hsu_config import HSUConfig


class DatasetSelector(Modal):
    """Dataset Selector window used to display data in the app.

    Signals:
        data_selected(dict): Displays the selected data.
    """

    data_selected = Signal(dict)

    def __init__(
        self, parent: QWidget = None, config_path: Path | str = None
    ) -> None:
        """Initialize component

        Args:
            parent(None/QWidget): The parent widget.
            config_path(Path | str): The path of the HSU configuratin file.
        """
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
        self.composite_type = None

        info_panel = QWidget(self)
        import_dataset_button = QPushButton("Import Dataset", info_panel)
        import_dataset_button.setStyleSheet(
            "border: 1px solid rgb(222, 222, 222);"
        )
        import_dataset_button.clicked.connect(self._import_dataset)

        import_geochem_button = QPushButton(
            "Import Geochemistry Data", info_panel
        )
        import_geochem_button.setStyleSheet(
            "border: 1px solid rgb(222, 222, 222);"
        )
        import_geochem_button.clicked.connect(self._import_geochem)

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

        self.comp_image_button = QCheckBox("Composite Core Image", self)
        self.comp_image_button.stateChanged.connect(self.create_comp_image)
        self.comp_plot_button = QCheckBox("Composite Spectral Plot", self)
        self.comp_plot_button.stateChanged.connect(self.create_comp_plot)

        info_panel_layout = QVBoxLayout(info_panel)
        info_panel_layout.addWidget(import_dataset_button)
        info_panel_layout.addWidget(import_geochem_button)
        info_panel_layout.addStretch()
        info_panel_layout.addWidget(self.comp_image_button)
        info_panel_layout.addWidget(self.comp_plot_button)
        info_panel_layout.addStretch()
        info_panel_layout.addWidget(self.comp_image_button)
        info_panel_layout.addWidget(self.comp_plot_button)
        info_panel_layout.addStretch()
        info_panel_layout.addWidget(self.meta_table)
        info_panel_layout.addStretch()
        info_panel_layout.addWidget(button_panel)

        self.dataset_list = FilterList(self, self._dataset_changed)
        self.datatypes_list = FilterList(self, self._datatype_changed)
        self.data_list = FilterList(self, self._dataname_changed)

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
        """Resizes window and contents.

        Args:
            width(int): New width of window.
            height(int): New height of window.
        """
        self.background.setFixedSize(width, height)
        self.content.setMaximumWidth(width - 100)
        self.content.setMaximumHeight(height - 100)

    def _dataset_changed(self, selected: str) -> None:
        """Updates the datatype and mineral lists when a dataset is selected.

        Args:
            selected(str): the key of the selected dataset.

        """
        path = self.hsu_config.dataset_path(selected)
        self.dataset = Dataset(path)
        self.selected_dataset = selected
        datatypes = self.dataset.data_types()
        self.datatypes_list.clear_list()
        self.datatypes_list.set_items(datatypes)
        self.datatypes_list.select([0, 0])

    def _datatype_changed(self, group: str, selected: str) -> None:
        """Updates the mineral list when data type is changed.

        Args:
            group(str): The key of the data group selected (e.g. Spectral
                Images).
            selected(str): The key ofthe sub-group selected (e.g. Chemistry).
        """
        self.selected_datatype = group
        self.selected_subtype = selected
        self.selected_data = None
        data = self.dataset.data_options(group, selected)
        self.data_list.clear_list()
        if data:
            self.data_list.set_items(data)
            self.data_list.select(0)

    def _dataname_changed(self, selected: list | QListWidgetItem) -> None:
        """Updates the metadata table list when a mineral is selected.

        Args:
            selected(list | QListWidgetItem): Keys of one or more seleceted
                minerals.

        """
        self.selected_dataname = selected
        self._update_table()

    def _import_dataset(self) -> None:
        """Open the directory selection window for users to select a dataset
        to add.

        """
        dataset_path = QFileDialog.getExistingDirectory(
            self, "Select Main Directory"
        )
        dataset_name = self.hsu_config.add_dataset(dataset_path)
        self._clear_lists()
        self.dataset_list.set_items(self.hsu_config.datasets())
        self.dataset_list.select(dataset_name)

    def _import_geochem(self) -> None:
        """Imports geochemistry data from xlsx file and adds to hsu config
        and/or dataset config.

        """
        geochem_path = QFileDialog.getOpenFileName(
            self, "Select Geochemistry Data", filter="(*.xlsx)"
        )[0]

        dataset_name = self.hsu_config.add_geochem(geochem_path)
        self._clear_lists()
        self.dataset_list.set_items(self.hsu_config.datasets())
        self.dataset_list.select(dataset_name)

    def _clear_lists(self) -> None:
        """Clears all options in listview widgets."""
        self.dataset_list.clear_list()
        self.datatypes_list.clear_list()
        self.data_list.clear_list()

    def _update_table(self) -> None:
        """Updates metadata displated in metadata table."""
        self.meta_table.set_label(
            self.selected_dataset,
            self.selected_datatype,
            self.selected_subtype,
            self.selected_dataname,
        )

        if isinstance(self.selected_dataname, list):
            self.meta_table.add_items(
                self.dataset.config, self.selected_dataname
            )
        else:
            self.meta_table.add_items(self.dataset.config)

    def _close(self) -> None:
        """Closes the dataset selector window."""
        super()._close()

    def _add_data(self) -> None:
        """Adds the selected data to the dashboard and closes this window."""
        args = {
            "config": self.dataset,
            "dataset_name": self.selected_dataset,
            "data_type": self.selected_datatype,
            "data_subtype": self.selected_subtype,
            "data_name": self.selected_dataname,
        }

        if self.comp_plot_button.isChecked():
            args["comp"] = "composite_plot"
            args["data_subtype"] = "Composite Plot"
        elif self.comp_image_button.isChecked():
            args["comp"] = "composite_image"
            args["data_subtype"] = "Composite Images"

        self.data_selected.emit(args)
        super()._close()

    def create_comp_image(self) -> None:
        """Beings the process of adding a composite core image to the
        dashboard.
        """
        if self.comp_image_button.isChecked():
            self.comp_plot_button.setChecked(False)
            self.meta_table.set_multi_data(True)

            self.datatypes_list.clear_list()
            self.datatypes_list.set_items({"Spectral Images": ["Mineral"]})
            self.datatypes_list.select([0, 0])
            self.data_list.enable_multi()

        elif not self.comp_plot_button.isChecked():
            self._dataset_changed(self.selected_dataset)
            self.meta_table.set_multi_data(False)
            self.data_list.disable_multi()
            self.data_list.select(0)

    def create_comp_plot(self) -> None:
        """Beings the process of adding a composite plot to the dashboard."""
        if self.comp_plot_button.isChecked():
            self.comp_image_button.setChecked(False)
            self.meta_table.set_multi_data(True)

            self.datatypes_list.clear_list()
            self.datatypes_list.set_items(
                {"Spectral Data": ["Mineral Percent"]}
            )
            self.datatypes_list.select([0, 0])
            self.data_list.enable_multi()

        elif not self.comp_image_button.isChecked():
            self._dataset_changed(self.selected_dataset)
            self.meta_table.set_multi_data(False)
            self.data_list.disable_multi()
            self.data_list.select(0)
