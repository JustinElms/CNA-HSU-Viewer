from typing import Callable

from PySide6.QtCore import (
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
    QItemSelectionModel,
)
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView,
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
        multi_select: bool = False,
    ) -> None:
        super().__init__(parent=parent)

        # self.setFixedWidth(parent.width() / 5)

        self.setMinimumWidth(100)

        self.options = None

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
        if multi_select:
            self.model_view.setSelectionMode(QAbstractItemView.MultiSelection)
        self.model_view.clicked[QModelIndex].connect(
            lambda index: self._on_changed(index)
        )
        self.selection_model = self.model_view.selectionModel()
        self.set_selected = set_selected

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.addWidget(self.filter_field)
        layout.addWidget(self.model_view)

    def _on_filter(self, filter_text: str) -> None:
        self.proxy_model.setFilterRegularExpression(filter_text)

    def _on_changed(self, index: QModelIndex) -> None:
        item = self.model.itemFromIndex(self.proxy_model.mapToSource(index))
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

                self.model_view.expandAll()

    def select(self, index: int | list) -> None:
        if isinstance(self.options, list):
            selected = self.model.item(index)
            self.selection_model.setCurrentIndex(
                self.model.indexFromItem(selected),
                QItemSelectionModel.Select,
            )
            self.set_selected(selected.text())
        elif isinstance(self.options, dict) and isinstance(index, list):
            selected_category = self.model.item(index[0])
            selected_row = selected_category.child(index[0], index[1])

            self.selection_model.select(
                self.model.indexFromItem(selected_row),
                QItemSelectionModel.Select,
            )

            self.set_selected(selected_category.text(), selected_row.text())

    def clear_list(self) -> None:
        if self.model.item(0):
            self.model.clear()
