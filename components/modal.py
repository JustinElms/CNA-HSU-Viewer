from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class Modal(QWidget):
    def __init__(self, parent: QWidget = None, text: str = None) -> None:
        super().__init__(parent=parent)

        self.background = QWidget(parent)
        self.background.setGeometry(0, 0, parent.width(), parent.height())
        self.background.setStyleSheet("background-Color: rgba(0,0,0,200)")

        self.content = QWidget(self.background)
        self.content.setStyleSheet("background-color: rgb(10,15,20)")
        self.content.setMaximumWidth(parent.width() * 0.7)
        self.content.setMaximumHeight(parent.width() * 0.7)

        button_bar = QWidget(self.content)
        button_bar.setMinimumWidth(self.content.width())
        button_bar.setMaximumHeight(40)
        button_bar.setStyleSheet("background-Color: rgb(51,51,51)")

        text_box = QLabel(text)
        text_box.setFont("24px")
        close_button = QPushButton("×")
        close_button.clicked.connect(self._close)
        close_button.setFlat(True)
        close_button.setMaximumWidth(20)
        close_button.setStyleSheet("font: 24px;")

        button_bar_layout = QHBoxLayout(button_bar)
        button_bar_layout.addWidget(text_box)
        button_bar_layout.addStretch()
        button_bar_layout.addWidget(close_button)

        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.addWidget(button_bar)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        self.background_layout = QHBoxLayout(self.background)
        self.background_layout.addWidget(self.content)
        self.background.show()

    def add_content(self, content: QWidget = None) -> None:
        self.content_layout.addWidget(content)

    def _close(self) -> None:
        self.background.deleteLater()
        self.content.deleteLater()
        self.deleteLater()