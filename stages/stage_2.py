from core.base_stage import BaseStageWidget


class Stage2Maze(BaseStageWidget):

    def __init__(self):
        super().__init__(
            stage_id="stage_2_maze",
            title="第二阶段：世界越来越清楚",
            description="手术后，世界一天比一天清晰。我能看懂以前看不懂的东西了。"
                        "阿尔吉侬和我在迷宫里比赛，我开始赢了。但我也开始注意到，"
                        "那些我以为在对我笑的人，其实是在嘲笑我。世界变得清楚，"
                        "但不一定变得更温暖。",
            button_text="进入下一阶段",
        )
