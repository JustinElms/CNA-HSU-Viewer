
import sys

from PySide6.QtWidgets import  QApplication

from hsu_viewer import HSUViewer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = HSUViewer()
    app.exec_()