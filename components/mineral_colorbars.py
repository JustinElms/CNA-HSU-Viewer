from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QLabel,
)


class MineralColorbars(QWidget):
    """Displays the various colorbars used for HSU minerals."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)

        title = QLabel("Mineral Colorbars (nm)", self)

        cmap_label_carb_mwir = QLabel("Carbonate MWIR", self)
        cmap_image_carb_mwir = QLabel(self)
        cmap_image_carb_mwir.setPixmap(
            QPixmap(":/colorbar_carbonate_mwir.png")
        )
        cmap_label_carb = QLabel("Carbonate", self)
        cmap_image_carb = QLabel(self)
        cmap_image_carb.setPixmap(QPixmap(":/colorbar_carbonate.png"))
        cmap_label_chlor = QLabel("Chlorite", self)
        cmap_image_chlor = QLabel(self)
        cmap_image_chlor.setPixmap(QPixmap(":/colorbar_chlorite.png"))
        cmap_label_w_mica = QLabel("White Mica", self)
        cmap_image_w_mica = QLabel(self)
        cmap_image_w_mica.setPixmap(QPixmap(":/colorbar_white_mica.png"))

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(cmap_label_carb_mwir)
        layout.addWidget(cmap_image_carb_mwir)
        layout.addWidget(cmap_label_carb)
        layout.addWidget(cmap_image_carb)
        layout.addWidget(cmap_label_chlor)
        layout.addWidget(cmap_image_chlor)
        layout.addWidget(cmap_label_w_mica)
        layout.addWidget(cmap_image_w_mica)
