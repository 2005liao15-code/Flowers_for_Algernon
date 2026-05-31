import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

from core.scene_manager import SceneManager


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("献给阿尔吉侬的花束")
        self.setFixedSize(1280, 720)
        self.setStyleSheet("background-color: #F5F0E3;")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        central.setLayout(layout)

        self.scene_manager = SceneManager()
        layout.addWidget(self.scene_manager.widget)


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
