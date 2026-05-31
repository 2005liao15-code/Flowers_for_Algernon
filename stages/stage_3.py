from core.base_stage import BaseStageWidget


class Stage3Isolation(BaseStageWidget):

    def __init__(self):
        super().__init__(
            stage_id="stage_3_isolation",
            title="第三阶段：我还是进不去",
            description="我变得比所有人都聪明了，但我比任何时候都更孤独。"
                        "知识像一道墙，把我和别人隔开。我记得以前那种简单的快乐，"
                        "现在再也找不回来了。阿尔吉侬开始变得焦躁，"
                        "我也开始担心——我们会一直聪明下去吗？",
            button_text="进入下一阶段",
        )
