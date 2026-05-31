from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal


class BaseStageWidget(QWidget):

    next_stage = pyqtSignal()

    def __init__(self, stage_id: str, title: str, description: str, button_text: str = "进入下一阶段"):
        super().__init__()
        self.stage_id = stage_id
        self._title = title
        self._description = description
        self._button_text = button_text
        self._init_ui()

    def _init_ui(self):
        self.setStyleSheet("background-color: #F5F0E3;")
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel(self._title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2C2C2C;
            margin-bottom: 16px;
        """)

        desc_label = QLabel(self._description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setMaximumWidth(600)
        desc_label.setStyleSheet("""
            font-size: 16px;
            color: #2C2C2C;
            line-height: 1.6;
            margin-bottom: 32px;
        """)

        btn = QPushButton(self._button_text)
        btn.setFixedSize(200, 48)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #2C2C2C;
                color: #F5F0E3;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
            QPushButton:pressed {
                background-color: #1A1A1A;
            }
        """)
        btn.clicked.connect(self._on_button_clicked)

        layout.addStretch()
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(btn, alignment=Qt.AlignCenter)
        layout.addStretch()
        self.setLayout(layout)

    def _on_button_clicked(self):
        self.next_stage.emit()

    def on_enter(self):
        """Called when this stage becomes active."""

    def on_leave(self):
        """Called when this stage is about to be left."""
