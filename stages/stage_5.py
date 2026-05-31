from core.base_stage import BaseStageWidget


class Stage5Flowers(BaseStageWidget):

    def __init__(self):
        super().__init__(
            stage_id="stage_5_flowers",
            title="第五阶段：献花",
            description="我比以前更差了。我不会写东西了，也看不太懂了。"
                        "但还记得一些事情。记得阿尔吉侬，记得那些变聪明的日子。"
                        "如果你有机会，请在我的墓碑——不，阿尔吉侬的墓碑前，放一束花。"
                        "谢谢你。",
            button_text="查看记录",
        )

    def on_enter(self):
        pass

    def _on_button_clicked(self):
        print("[记录] 查理·高登的进步报告已完成。感谢阅读《献给阿尔吉侬的花束》。")
