from typing import Callable

from PySide6.QtCore import Qt, QModelIndex, QSortFilterProxyModel
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QLineEdit,
    QListWidgetItem,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QTreeView,
)

from hsu_viewer.dataset_config import DatasetConfig


class FilterList(QWidget):
    def __init__(
        self, parent: QWidget = None, set_selected: Callable[[str], None] = None
    ) -> None:
        super().__init__(parent=parent)

        self.setFixedWidth(parent.width() / 4)
        self.setFixedHeight(parent.height() / 2)

        self.options = None

        self.filter_field = QLineEdit(self)
        self.filter_field.setPlaceholderText("Filter items")
        self.filter_field.textChanged.connect(self._on_filter)
        
        self.options_list = QTreeView(self)
        self.options_list.setHeaderHidden(True)
        self.model = QStandardItemModel()
        self.model_root = self.model.invisibleRootItem()
        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxyModel.setRecursiveFilteringEnabled(True)
        self.proxyModel.setSourceModel(self.model)
        self.options_list.setModel(self.proxyModel)
        self.options_list.clicked[QModelIndex].connect(
            lambda index: self._on_changed(index)
        )

        self.set_selected = set_selected

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.addWidget(self.filter_field)
        layout.addWidget(self.options_list)

    def _on_filter(self, filter_text: str) -> None:
        self.proxyModel.setFilterRegularExpression(filter_text)

    def _on_changed(self, index) -> None:
        item = self.model.itemFromIndex(self.proxyModel.mapToSource(index))
        if item.parent():
            self.set_selected(item.parent().text(), item.text())
        else:
            self.set_selected(item.text())        

    def set_items(self, items: list | dict, filter_text: str = None) -> None:
        if items:
            self.options = items
            if isinstance(items, list):
                for item in items:
                    if not filter_text or filter_text in item.lower():
                        self.model.appendRow(QStandardItem(item))    
            elif isinstance(items, dict):
                for key in items.keys():
                    item = QStandardItem(key)
                    item.setSelectable(False)
                    for value in items[key]:
                        if not filter_text or filter_text in value.lower():
                            item.appendRow(QStandardItem(value))
                    self.model_root.appendRow(item)
                self.options_list.expandAll()
                self.options_list.setCurrentIndex(QModelIndex(0))
        return

    def clear_list(self):
        if self.model.item(0):
            self.model.clear()


class DatasetSelector(QWidget):
    def __init__(self, parent: QWidget = None, config_path: str = None) -> None:
        super().__init__(parent=parent)

        # main widget layout
        layout = QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # self.setGeometry(50, 50, parent.width() - 100, parent.height() - 100)
        self.setGeometry(50, 50, 1000, 750)

        self.dataset_config = DatasetConfig(config_path)

        datasets = self.dataset_config.datasets()
        self.selected_dataset = None

        self.dataset_list = FilterList(self, self._dataset_changed)
        self.datatypes_list = FilterList(self, self._datatype_changed)
        self.data_list = FilterList(self, self._data_changed)

        self.dataset_list.set_items(datasets)

        layout.addStretch()
        layout.addWidget(self.dataset_list)
        layout.addWidget(self.datatypes_list)
        layout.addWidget(self.data_list)
        layout.addStretch()

        self.show()

    def _dataset_changed(self, selected: str) -> None:
        self.selected_dataset = selected
        datatypes = self.dataset_config.data_types(selected)
        self.datatypes_list.clear_list()
        self.datatypes_list.set_items(datatypes)

    def _datatype_changed(self, group: str, selected: str) -> None:
        self.selected_datatype = selected
        data = self.dataset_config.data_options(self.selected_dataset, group, selected)
        self.data_list.clear_list()
        self.data_list.set_items(data)

    def _data_changed(self, selected: QListWidgetItem) -> None:
        self.selected_data = selected
