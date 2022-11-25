from typing import Callable

from PySide6.QtCore import QModelIndex, QSortFilterProxyModel, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QLineEdit, QTreeView, QVBoxLayout, QWidget


class FilterList(QWidget):
    def __init__(
        self, parent: QWidget = None, set_selected: Callable[[str], None] = None
    ) -> None:
        super().__init__(parent=parent)

        self.setStyleSheet("background-color: rgb(0,0,0)")
        self.setFixedWidth(parent.width() / 3)

        self.options = None

        self.filter_field = QLineEdit(self)
        self.filter_field.setPlaceholderText("Filter items")
        self.filter_field.textChanged.connect(self._on_filter)

        self.options_list = QTreeView(self)
        self.options_list.setHeaderHidden(True)
        self.model = QStandardItemModel()
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

    def _on_changed(self, index: QModelIndex) -> None:
        item = self.model.itemFromIndex(self.proxyModel.mapToSource(index))
        if item.parent():
            self.set_selected(item.parent().text(), item.text())
        else:
            self.set_selected(item.text())

    def set_items(self, items: list | dict, filter_text: str = None) -> None:
        self.model_root = self.model.invisibleRootItem()
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
                        sub_item = QStandardItem(value)
                        if not filter_text or filter_text in value.lower():
                            item.appendRow(sub_item)
                    self.model_root.appendRow(item)

                self.options_list.expandAll()

    def clear_list(self) -> None:
        if self.model.item(0):
            self.model.clear()
