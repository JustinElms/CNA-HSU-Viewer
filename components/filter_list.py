from typing import Callable

from PySide6.QtCore import (
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
    QItemSelectionModel,
)
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QLineEdit,
    QTreeView,
    QVBoxLayout,
    QWidget,
)


class FilterList(QWidget):
    def __init__(
        self,
        parent: QWidget = None,
        set_selected: Callable[[str], None] = None,
    ) -> None:
        super().__init__(parent=parent)

        self.setMinimumWidth(100)

        self.options = None
        self.multi_level = False
        self.multi_select = False

        self.filter_field = QLineEdit(self)
        self.filter_field.setPlaceholderText("Filter items")
        self.filter_field.textChanged.connect(self._on_filter)

        self.model_view = QTreeView(self)
        self.model_view.setHeaderHidden(True)
        self.model = QStandardItemModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setRecursiveFilteringEnabled(True)
        self.proxy_model.setSourceModel(self.model)
        self.model_view.setModel(self.proxy_model)
        self.model_view.clicked[QModelIndex].connect(
            lambda index: self._on_changed(index)
        )
        self.selection_model = self.model_view.selectionModel()
        self.set_selected = set_selected

        self.selected = []

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.addWidget(self.filter_field)
        layout.addWidget(self.model_view)

    def _on_filter(self, filter_text: str) -> None:
        self.proxy_model.setFilterRegularExpression(filter_text)

    def _on_changed(self, index: QModelIndex) -> None:
        item = self.model.itemFromIndex(self.proxy_model.mapToSource(index))
        if not self.multi_select:
            for selected in self.selected:
                selected.setBackground(Qt.NoBrush)
        if self.multi_level and item.parent():
            item.setBackground(Qt.blue)
            self.set_selected(item.parent().text(), item.text())
            self.selected = [item]
        elif not self.multi_level:
            item.setBackground(Qt.blue)
            if self.multi_select:
                if item in self.selected:
                    item.setBackground(Qt.NoBrush)
                    self.selected.remove(item)
                else:
                    self.selected.append(item)
                self.set_selected(
                    [selected.text() for selected in self.selected]
                )
            else:
                self.set_selected(item.text())
                self.selected = [item]

    def set_items(self, items: list | dict, filter_text: str = None) -> None:
        self.model_root = self.model.invisibleRootItem()
        if items:
            self.options = items
            if isinstance(items, list):
                for item in items:
                    if not filter_text or filter_text in item.lower():
                        newItem = QStandardItem(item)
                        newItem.setEditable(False)
                        self.model.appendRow(newItem)

            elif isinstance(items, dict):
                self.multi_level = True
                for key in items.keys():
                    item = QStandardItem(key)
                    item.setSelectable(False)
                    item.setEditable(False)
                    for value in items[key]:
                        sub_item = QStandardItem(value)
                        if not filter_text or filter_text in value.lower():
                            item.appendRow(sub_item)
                    self.model_root.appendRow(item)

                self.model_view.expandAll()

    def select(self, index: int | list) -> None:
        if isinstance(self.options, list):
            item = self.model.item(index)
            item.setBackground(Qt.blue)
            self.selection_model.setCurrentIndex(
                self.model.indexFromItem(item),
                QItemSelectionModel.Select,
            )
            self.selected.append(item)
            self.set_selected(item.text())

        elif isinstance(self.options, dict) and isinstance(index, list):
            idx = index[0]
            while not self.model.item(idx).hasChildren():
                idx = idx + 1
            parent_item = self.model.item(idx)
            child_item = parent_item.child(idx, index[1])
            child_item.setBackground(Qt.blue)

            self.selection_model.select(
                self.model.indexFromItem(child_item),
                QItemSelectionModel.Select,
            )
            self.selected.append(child_item)
            self.set_selected(parent_item.text(), child_item.text())

    def clear_list(self) -> None:
        if self.model.item(0):
            self.model.clear()

    def enable_multi(self) -> None:
        for selected in self.selected:
            selected.setBackground(Qt.NoBrush)
        self.selected = []
        self.multi_select = True

    def disable_multi(self) -> None:
        for selected in self.selected:
            selected.setBackground(Qt.NoBrush)
        self.selected = []
        self.multi_select = False
