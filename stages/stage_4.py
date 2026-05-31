from core.base_stage import BaseStageWidget


class Stage4Archive(BaseStageWidget):

    def __init__(self):
        super().__init__(
            stage_id="stage_4_archive",
            title="第四阶段：阿尔吉侬档案",
            description="阿尔吉侬死了。它走完了从聪明到衰退的全部路程。"
                        "我知道我也会一样。在能力还在的时候，我要把所有研究整理归档，"
                        "留下完整的记录。这不只是为了科学，也是为了证明我们存在过。"
                        "阿尔吉侬的生命有意义，我的也一样。",
            button_text="进入下一阶段",
        )
