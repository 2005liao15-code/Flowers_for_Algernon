from PyQt5.QtWidgets import QStackedWidget

from stages.stage_1 import Stage1Consent
from stages.stage_2 import Stage2Maze
from stages.stage_3 import Stage3Isolation
from stages.stage_4 import Stage4Archive
from stages.stage_5 import Stage5Flowers


class SceneManager:

    STAGES = [
        ("stage_1_consent", Stage1Consent),
        ("stage_2_maze", Stage2Maze),
        ("stage_3_isolation", Stage3Isolation),
        ("stage_4_archive", Stage4Archive),
        ("stage_5_flowers", Stage5Flowers),
    ]

    def __init__(self, parent=None):
        self._stack = QStackedWidget(parent)
        self._stage_widgets = {}
        self._current_index = 0

        for stage_id, stage_class in self.STAGES:
            widget = stage_class()
            widget.next_stage.connect(self.go_next)
            self._stage_widgets[stage_id] = widget
            self._stack.addWidget(widget)

        self._stack.setCurrentIndex(0)
        self._current_widget().on_enter()

    @property
    def widget(self):
        return self._stack

    def go_next(self):
        current = self._current_widget()
        current.on_leave()

        self._current_index += 1
        if self._current_index >= len(self.STAGES):
            self._current_index = len(self.STAGES) - 1
            return

        self._stack.setCurrentIndex(self._current_index)
        self._current_widget().on_enter()

    def switch_to(self, stage_id: str):
        if stage_id not in self._stage_widgets:
            return
        self._current_widget().on_leave()
        self._current_index = [s[0] for s in self.STAGES].index(stage_id)
        self._stack.setCurrentIndex(self._current_index)
        self._current_widget().on_enter()

    def _current_widget(self):
        return self._stack.currentWidget()
