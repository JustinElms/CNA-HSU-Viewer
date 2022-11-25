from PySide6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem


class MetadataTable(QTableWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)

        self.setColumnCount(2)

        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.horizontalHeader().hide()
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().hide()

    def add_items(self, items: dict) -> None:
        self.clear()
        self.setRowCount(len(items.values()))
        for idx, item in enumerate(items.items()):
            self.setItem(idx, 0, QTableWidgetItem(item[0]))
            self.setItem(idx, 1, QTableWidgetItem(item[1]))
