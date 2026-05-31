import math
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QScrollArea, QPushButton, QLabel, QTextBrowser,
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPointF, QRectF, QMargins
from PyQt5.QtGui import (
    QPainter, QPainterPath, QFont, QColor, QPen,
    QBrush, QLinearGradient, QRadialGradient,
)


# ── helpers ──────────────────────────────────────────────────────────

def _system_font(size: int, bold: bool = False) -> QFont:
    candidates = ["Courier New", "Consolas", "DejaVu Sans Mono", "Ubuntu Mono", "monospace"]
    font = QFont(candidates[0], size)
    for fam in candidates[1:]:
        font.setFamily(fam)
    font.setStyleHint(QFont.Monospace)
    font.setBold(bold)
    return font


def _handwriting_font(size: int) -> QFont:
    candidates = [
        "Segoe Script", "Caveat", "Comic Sans MS",
        "URW Chancery L", "Bradley Hand ITC", "Lucida Handwriting",
    ]
    font = QFont(candidates[0], size)
    for fam in candidates[1:]:
        font.setFamily(fam)
    font.setStyleHint(QFont.Cursive)
    font.setItalic(True)
    return font


def _serif_font(size: int, bold: bool = False) -> QFont:
    candidates = ["Times New Roman", "Georgia", "DejaVu Serif", "serif"]
    font = QFont(candidates[0], size)
    for fam in candidates[1:]:
        font.setFamily(fam)
    font.setStyleHint(QFont.Times)
    font.setBold(bold)
    return font


# ── Screen 1: Boot terminal ──────────────────────────────────────────

_BOOT_LINES = [
    ("warm", "贝克曼大学医学中心"),
    ("warm", "实验心理学部"),
    ("warm", "案例档案：CG-1965-037"),
    ("warm", "受试者记录：Charlie Gordon"),
    ("warm", "记录状态：待确认"),
    ("warm", "正在初始化记录系统……"),
    ("warm", ""),
    ("ok",    "记忆模块已加载"),
    ("ok",    "感官数据处理单元已连接"),
    ("ok",    "认知基线已建立"),
    ("warm", ""),
    ("warm", "> 准备开始术前记录。"),
    ("warm", "> 受试者：查理·戈登"),
    ("warm", "> 状态：术前观察"),
]

_BOOT_TEXT = "\n".join(line for _, line in _BOOT_LINES)

_BOOT_CURSOR = "█"

_BOOT_DELAYS = {
    "/": 180, "\n": 200, ".": 120, ":": 100, "……": 320,
    "[": 80, "]": 60, ">": 100,
}


class _BootScreen(QWidget):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setAutoFillBackground(True)
        self.setStyleSheet("background-color: #17140F; border: none;")
        self._char_index = 0
        self._cursor_visible = True
        self._text_browser = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._blink = QTimer(self)
        self._blink.timeout.connect(self._on_blink)
        self._init_ui()

    def _init_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(70, 60, 70, 50)
        outer.setSpacing(0)

        self._text_browser = QTextBrowser()
        self._text_browser.setOpenExternalLinks(False)
        self._text_browser.setOpenLinks(False)
        self._text_browser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._text_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._text_browser.setFrameShape(QTextBrowser.NoFrame)
        self._text_browser.setStyleSheet(
            "background-color: transparent; border: none;"
        )
        outer.addWidget(self._text_browser)
        self._render_text("")

    def _render_text(self, visible: str):
        cursor = _BOOT_CURSOR if self._cursor_visible else " "
        lines = (visible + cursor).split("\n")

        warm = "#E8E0C8"
        green = "#9BAF8A"

        html_lines = []
        for idx, line in enumerate(lines):
            safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            safe = safe.replace(" ", "&nbsp;")

            # colour the "[ OK ]" prefix
            if safe.startswith("[&nbsp;OK&nbsp;]"):
                safe = (
                    '<span style="color:' + green + ';">[&nbsp;OK&nbsp;]</span>'
                    + safe[20:]
                )
            # colour ">" prompt slightly brighter
            elif safe.startswith("&gt;"):
                safe = (
                    '<span style="color:' + green + ';">&gt;</span>'
                    + safe[4:]
                )

            html_lines.append(f"<span style='color:{warm};'>{safe}</span>")

        body = "<br>".join(html_lines)

        html = f"""<!DOCTYPE html>
<html><head><style>
body {{
    background-color: #17140F; color: {warm};
    margin: 0; padding: 0;
    font-family: 'Courier New', Consolas, 'DejaVu Sans Mono', monospace;
    font-size: 22px; line-height: 1.5;
}}
</style></head><body>{body}</body></html>"""
        self._text_browser.setHtml(html)

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#17140F"))
        p.end()

    def start(self):
        self._char_index = 0
        self._cursor_visible = True
        self._render_text("")
        self._timer.start(60)
        self._blink.start(530)

    def stop(self):
        self._timer.stop()
        self._blink.stop()

    def _delay_for(self, ch: str) -> int:
        for key, ms in _BOOT_DELAYS.items():
            if ch == key:
                return ms
        return 0

    def _on_tick(self):
        if self._char_index >= len(_BOOT_TEXT):
            self._timer.stop()
            self._cursor_visible = False
            self._render_text(_BOOT_TEXT)
            QTimer.singleShot(900, self.finished.emit)
            return
        self._char_index += 1
        visible = _BOOT_TEXT[:self._char_index]
        self._render_text(visible)
        if self._char_index < len(_BOOT_TEXT):
            ch = _BOOT_TEXT[self._char_index]
            extra = self._delay_for(ch)
            self._timer.setInterval(max(40, 60 if extra == 0 else extra))

    def _on_blink(self):
        self._cursor_visible = not self._cursor_visible
        if self._timer.isActive():
            visible = _BOOT_TEXT[:self._char_index]
            self._render_text(visible)


# ── Screen 2: First progress report ──────────────────────────────────

_REPORT_HEADER_HTML = (
    '<div style="font-size:19px; color:#7A7060; line-height:1.55;'
    ' margin-bottom:38px; font-family:serif; font-style:normal;">'
    "受试者：查理·戈登　|　案例编号：CG-1965-037<br>"
    "进步报告 1　|　日期：3月3日"
    "</div>"
)

_REPORT_PARAGRAPHS = [
    "施特劳斯博士说我应该把我想到的和记住的都写下来，"
    "还有每天发生的事情。",

    "我不知道为什么但他说这很重要这样他们就能看看能不能用我。",

    "我希望他们能用我因为金尼安小姐说也许他们可以让我变聪明。",

    "我想变聪明。",
]

_REPORT_SEQ = []
for _pi, _pp in enumerate(_REPORT_PARAGRAPHS):
    for _ch in _pp:
        _REPORT_SEQ.append(_ch)
    if _pi < len(_REPORT_PARAGRAPHS) - 1:
        _REPORT_SEQ.append("\n\n")


class _ReportScreen(QWidget):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._char_index = 0
        self._text_browser = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._init_ui()

    def _init_ui(self):
        self.setStyleSheet("background-color: #D8C9A8;")
        self._text_browser = QTextBrowser()
        self._text_browser.setOpenExternalLinks(False)
        self._text_browser.setOpenLinks(False)
        self._text_browser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._text_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._text_browser.setFrameShape(QTextBrowser.NoFrame)
        self._text_browser.setStyleSheet(
            "background-color: transparent; border: none;"
        )

        # 940px paper centred in 1280px window
        side = (1280 - 940) // 2
        hbox = QHBoxLayout()
        hbox.setContentsMargins(side, 100, side, 80)
        hbox.addWidget(self._text_browser)
        self.setLayout(hbox)
        self._render_text("")

    def _render_text(self, visible_raw: str):
        color_css = "#2C2C2C"
        font_css = (
            "font-family: 'Segoe Script', Caveat, 'Comic Sans MS',"
            " 'URW Chancery L', cursive;"
            " font-size: 30px; font-style: italic;"
        )
        para_css = (
            f"line-height: 1.7; margin-bottom: 24px; {font_css} color: {color_css};"
        )
        empty_css = (
            f"line-height: 1.7; margin-bottom: 24px; {font_css} color: transparent;"
        )

        paras = visible_raw.split("\n\n") if visible_raw else []
        rendered = [_REPORT_HEADER_HTML]
        for p in paras:
            safe = p.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            cls = para_css if safe else empty_css
            content = safe if safe else "&nbsp;"
            rendered.append(f'<p style="{cls}">{content}</p>')

        html = f"""<!DOCTYPE html>
<html><head><style>
body {{
    background-color: transparent; color: {color_css};
    margin: 0; padding: 0;
    {font_css}
}}
</style></head><body>{"".join(rendered)}</body></html>"""
        self._text_browser.setHtml(html)

    def start(self):
        self._char_index = 0
        self._render_text("")
        self._timer.start(80)

    def stop(self):
        self._timer.stop()

    def _on_tick(self):
        if self._char_index >= len(_REPORT_SEQ):
            self._timer.stop()
            QTimer.singleShot(1200, self.finished.emit)
            return
        self._char_index += 1
        visible = "".join(_REPORT_SEQ[:self._char_index])
        self._render_text(visible)
        if self._char_index < len(_REPORT_SEQ):
            ch = _REPORT_SEQ[self._char_index]
            extra = 200 if ch == "\n" else 80 if ch in "。，" else 0
            self._timer.setInterval(max(55, 80 + extra // 3))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # outer background
        p.fillRect(self.rect(), QColor("#D8C9A8"))

        # paper area — centred 940 px wide
        paper_w = 940
        paper_x = (w - paper_w) // 2
        paper_rect = QRectF(paper_x, 40, paper_w, h - 80)

        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#F1E6C8"))
        p.drawRect(paper_rect)

        # paper stack shadow
        for offset in range(4, 0, -1):
            shadow = QColor(0, 0, 0, 14 - offset * 2)
            p.setPen(Qt.NoPen)
            p.setBrush(shadow)
            p.drawRect(paper_rect.adjusted(offset * 1.2, offset * 1.2,
                                           offset * 1.2, offset * 1.2))

        p.setBrush(QColor("#F1E6C8"))
        p.drawRect(paper_rect)

        # faint ruled lines within paper
        line_spacing = 48
        p.setPen(QPen(QColor(180, 160, 130, 50), 0.5))
        for r in range(14):
            y = paper_rect.top() + 90 + r * line_spacing
            p.drawLine(QPointF(paper_rect.left() + 60, y),
                       QPointF(paper_rect.right() - 40, y))

        # red margin
        p.setPen(QPen(QColor(160, 90, 80, 90), 1.4))
        margin_x = paper_rect.left() + 76
        p.drawLine(QPointF(margin_x, paper_rect.top() + 20),
                   QPointF(margin_x, paper_rect.bottom() - 16))

        # vignette at edges
        vig = QRadialGradient(w * 0.5, h * 0.45, w * 0.6)
        vig.setColorAt(0, QColor(0, 0, 0, 0))
        vig.setColorAt(1, QColor(0, 0, 0, 32))
        p.setBrush(vig)
        p.setPen(Qt.NoPen)
        p.drawRect(self.rect())

        p.end()


# ── Screen 3: Consent form ───────────────────────────────────────────

_CONSENT_CLAUSES = [
    ("第一条", "受试者经完整告知实验目的、方法、预期效果及可能之后遗症与危险后，自愿参与本项实验。"),
    ("第二条", "实验中所涉手术干预方式，其性质及风险均已向受试者充分说明，受试者已签署手术知情同意书。"),
    ("第三条", "受试者理解并接受：术后认知能力之持续性不构成实验方任何形式之承诺事项。"),
    ("第四条", "受试者同意在实验期间配合完成所有指定测验、访谈、生理指标采集及行为观察记录。"),
    ("第五条", "实验过程中所取得之一切资料，包括但不限于测验数据、影像记录、书面报告与生物样本，实验方拥有完整研究使用权。"),
    ("第六条", "受试者之姓名及身份信息将以代号取代，并在发表时予以匿名化处理，但实验方不保证受试者身份绝不被外界推知。"),
    ("第七条", "实验方仅对观察期内记录之完整性负责，不对受试者长期认知适应结果作任何形式之保证。"),
    ("第八条", "受试者于实验期间有权随时退出，因退出所导致之数据不完整不构成受试者之违约责任。"),
    ("第九条", "如实验过程中发生与实验直接相关之严重不良反应，实验方将提供必要之紧急处置，后续治疗费用由受试者自行承担。"),
    ("第十条", "本同意书之解释与履行以贝克曼大学医学中心所在地法律为准据，因本同意书所生之一切争议由双方先行协商解决。"),
    ("第十一条", "受试者理解：术后能力变化可能存在不可逆或反向发展之风险，实验方不承担相应责任。"),
    ("第十二条", "本同意书一式三份，分别交由受试者、实验主持单位及医学伦理委员会保存。"),
]

_SIGNATURE_STROKES = None


def _build_signature_strokes() -> list:
    strokes = []

    def _stroke(*pts):
        path = QPainterPath()
        path.moveTo(pts[0], pts[1])
        for i in range(2, len(pts), 2):
            path.lineTo(pts[i], pts[i + 1])
        strokes.append(path)

    def _curve(x0, y0, cx1, cy1, cx2, cy2, x1, y1):
        path = QPainterPath()
        path.moveTo(x0, y0)
        path.cubicTo(cx1, cy1, cx2, cy2, x1, y1)
        strokes.append(path)

    # ── 查 ──
    _stroke(30, 20, 110, 22)
    _curve(70, 24, 68, 50, 72, 75, 62, 118)
    _curve(70, 42, 58, 62, 34, 90, 18, 112)
    _curve(70, 42, 88, 68, 112, 90, 124, 112)
    _stroke(28, 108, 110, 112)
    _curve(70, 118, 70, 98, 66, 80, 68, 68)
    _stroke(40, 88, 100, 90)
    _stroke(26, 128, 112, 130)

    # ── 理 ──
    _stroke(140, 26, 138, 118)
    _stroke(160, 28, 200, 32)
    _stroke(150, 68, 206, 72)
    _stroke(148, 112, 204, 116)
    _stroke(210, 24, 270, 28)
    _curve(236, 28, 232, 56, 240, 84, 234, 118)
    _stroke(212, 60, 270, 64)
    _stroke(212, 88, 270, 92)
    _stroke(212, 120, 270, 124)

    # ── · ──
    _curve(296, 100, 298, 96, 300, 96, 298, 100)

    # ── 戈 ──
    _stroke(310, 26, 372, 30)
    _curve(356, 26, 380, 48, 396, 82, 388, 118)
    _curve(340, 34, 320, 54, 308, 78, 298, 98)
    _curve(374, 68, 394, 60, 406, 54, 414, 50)

    # ── 登 ──
    _curve(430, 24, 460, 36, 482, 50, 500, 60)
    _curve(464, 24, 462, 48, 468, 72, 462, 100)
    _curve(464, 42, 484, 56, 498, 66, 506, 72)
    _stroke(432, 66, 476, 68)
    _stroke(436, 86, 478, 88)
    _stroke(432, 106, 504, 108)
    _curve(466, 68, 468, 76, 464, 82, 468, 92)

    return strokes


def _signature_strokes() -> list:
    global _SIGNATURE_STROKES
    if _SIGNATURE_STROKES is None:
        _SIGNATURE_STROKES = _build_signature_strokes()
    return _SIGNATURE_STROKES


class _ConsentFormScreen(QWidget):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setAutoFillBackground(True)
        self.setObjectName("consentFormScreen")
        self.setStyleSheet(
            "#consentFormScreen { background-color: #D8C9A8; border: none; }"
        )
        self._scroll = None
        self._sign_btn = None
        self._sig_overlay = None
        self._stage = "scroll"
        self._init_ui()

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#D8C9A8"))
        p.end()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background-color: #D8C9A8; }"
        )
        scroll.viewport().setStyleSheet("background-color: #D8C9A8;")
        scroll.verticalScrollBar().valueChanged.connect(self._on_scroll)

        doc = QWidget()
        doc.setStyleSheet("background-color: #F4EAD2;")
        doc_layout = QVBoxLayout(doc)
        doc_layout.setContentsMargins(160, 60, 160, 60)

        # header
        title = QLabel("贝克曼大学医学中心\n实验心理学部\n\n受试者知情同意书")
        title.setFont(_serif_font(34, bold=True))
        title.setStyleSheet("color: #1A1A1A; line-height: 1.5;")
        title.setAlignment(Qt.AlignCenter)

        doc_layout.addWidget(title)
        doc_layout.addSpacing(28)

        # identity info block
        identity_html = (
            '<div style="line-height:1.7; font-size:21px; color:#2C2C2C;'
            ' font-family:serif; margin-bottom:12px;">'
            "实验对象姓名：查理·戈登<br>"
            "实验对象编号：CG-1965-037<br>"
            "实验项目：认知能力提升术后观察<br>"
            "负责医生：Dr. J. Strauss / Dr. N. Nemur"
            "</div>"
        )
        identity = QLabel(identity_html)
        identity.setFont(_serif_font(21))
        identity.setTextFormat(Qt.RichText)
        doc_layout.addWidget(identity)
        doc_layout.addSpacing(38)

        # clauses
        for num, text in _CONSENT_CLAUSES:
            html = (
                f'<p style="line-height: 1.6; margin: 0 0 14px 0;'
                f' font-size: 20px; color: #2C2C2C;">'
                f'<b>{num}</b>　　{text}'
                f'</p>'
            )
            clause = QLabel(html)
            clause.setFont(_serif_font(20))
            clause.setWordWrap(True)
            clause.setTextFormat(Qt.RichText)
            doc_layout.addWidget(clause)

        doc_layout.addSpacing(52)

        # signature area
        sig_html = (
            '<div style="line-height:1.8; font-size:22px; color:#2C2C2C;'
            ' font-family:serif;">'
            "实验对象打印姓名：查理·戈登<br>"
            "实验对象签名：_______________<br>"
            "见证人：Dr. J. Strauss / Dr. N. Nemur<br>"
            "日期：March 4, 1965"
            "</div>"
        )
        sig_label = QLabel(sig_html)
        sig_label.setFont(_serif_font(22))
        sig_label.setTextFormat(Qt.RichText)
        doc_layout.addWidget(sig_label)

        doc_layout.addStretch()
        scroll.setWidget(doc)
        self._scroll = scroll
        layout.addWidget(scroll)

        # sign button
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(160, 14, 160, 24)
        btn_row.addStretch()
        self._sign_btn = QPushButton("签  名")
        self._sign_btn.setFixedSize(220, 52)
        self._sign_btn.setEnabled(False)
        self._sign_btn.setCursor(Qt.PointingHandCursor)
        self._sign_btn.setFont(_serif_font(18, bold=True))
        self._sign_btn.setStyleSheet("""
            QPushButton {
                background-color: #C0C0C0; color: #808080;
                border: 2px solid #A0A0A0; border-radius: 6px;
                font-size: 18px; font-weight: bold;
            }
            QPushButton:enabled {
                background-color: #2C2C2C; color: #F5F0E3;
                border: 2px solid #2C2C2C;
            }
            QPushButton:enabled:hover { background-color: #4A4A4A; }
        """)
        self._sign_btn.clicked.connect(self._start_signing)
        btn_row.addWidget(self._sign_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._sig_overlay = _SignatureOverlay(self)
        self._sig_overlay.hide()
        self._sig_overlay.finished.connect(self._on_sig_done)

    def start(self):
        self._stage = "scroll"
        self._sign_btn.setEnabled(False)
        self._sig_overlay.hide()

    def stop(self):
        if self._sig_overlay:
            self._sig_overlay.stop()

    def _on_scroll(self, value):
        if self._stage != "scroll":
            return
        bar = self._scroll.verticalScrollBar()
        if bar.maximum() > 0 and value >= bar.maximum() - 10:
            self._sign_btn.setEnabled(True)

    def _start_signing(self):
        self._stage = "signing"
        self._sign_btn.setEnabled(False)
        self._sign_btn.setText("签名中……")
        self._sig_overlay.show()
        self._sig_overlay.raise_()
        self._sig_overlay.start_animation()

    def _on_sig_done(self):
        self._stage = "done"
        self._sig_overlay.hide()
        self._sign_btn.setText("已签署")
        QTimer.singleShot(2400, self.finished.emit)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._sig_overlay:
            self._sig_overlay.setGeometry(self.rect())


# ── Signature overlay ────────────────────────────────────────────────

_SYSTEM_RECORD = (
    "同意书已归档\n"
    "案例档案：CG-1965-037\n"
    "受试者：查理·戈登\n"
    "Subject: Charlie Gordon\n"
    "当前状态：术前观察\n"
    "实验记录：已开始"
)


class _SignatureOverlay(QWidget):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self._strokes = _signature_strokes()
        self._current_stroke = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._anim_progress = 0.0
        self._phase = "idle"
        self._done_timer = 0

    def start_animation(self):
        self._current_stroke = 0
        self._phase = "drawing"
        self._anim_progress = 0.0
        self._timer.start(16)

    def stop(self):
        self._timer.stop()

    def _tick(self):
        if self._phase == "drawing":
            self._anim_progress += 0.045
            if self._anim_progress >= 1.0:
                self._anim_progress = 0.0
                self._current_stroke += 1
                if self._current_stroke >= len(self._strokes):
                    self._phase = "done"
                    self._done_timer = 0
                    self.update()
                    self._timer.stop()
                    QTimer.singleShot(1800, self._on_complete)
                    return
            self.update()

    def _on_complete(self):
        self._timer.stop()
        self.finished.emit()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        p.fillRect(self.rect(), QColor(216, 201, 168, 215))

        # signature box
        box_w, box_h = 580, 210
        box_x = (self.width() - box_w) // 2
        box_y = (self.height() - box_h) // 2 - 30

        p.setPen(QPen(QColor("#8A8A80"), 1.5))
        p.setBrush(QColor("#FEFCF5"))
        p.drawRoundedRect(QRectF(box_x, box_y, box_w, box_h), 6, 6)

        # signature line
        line_y = box_y + box_h - 58
        p.setPen(QPen(QColor("#AAAAA0"), 1))
        p.drawLine(QPointF(box_x + 40, line_y), QPointF(box_x + box_w - 40, line_y))
        p.setFont(_handwriting_font(11))
        p.setPen(QColor("#9A9A90"))
        p.drawText(int(box_x + 44), int(line_y + 20), "实验对象签名")

        p.setClipRect(QRectF(box_x + 30, box_y + 20, box_w - 60, box_h - 90))

        p.setPen(QPen(QColor("#1A1510"), 3.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        offset = QPointF(box_x + 20, box_y + 10)

        for i in range(self._current_stroke):
            path = QPainterPath(self._strokes[i])
            path.translate(offset)
            p.drawPath(path)

        if self._current_stroke < len(self._strokes) and self._phase == "drawing":
            full = QPainterPath(self._strokes[self._current_stroke])
            full.translate(offset)
            total_len = full.length()
            if total_len > 0:
                dash_len = total_len * self._anim_progress
                gap_len = total_len * 2
                pen = QPen(QColor("#1A1510"), 3.5,
                           Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                pen.setDashPattern([dash_len, gap_len])
                p.setPen(pen)
                p.drawPath(full)

        p.setClipping(False)

        if self._phase == "done":
            # red stamp
            p.setPen(QPen(QColor("#A93428"), 3))
            p.setFont(_serif_font(16, bold=True))
            stamp_x = box_x + box_w - 150
            stamp_y = box_y + box_h - 80
            p.save()
            p.translate(stamp_x, stamp_y)
            p.rotate(-14)
            p.drawText(-40, 0, "已签署")
            p.restore()

            # system record below the signature box
            record_y = box_y + box_h + 18
            p.setPen(QColor("#2C2C2C"))
            p.setFont(_serif_font(21))
            record_lines = _SYSTEM_RECORD.split("\n")
            for ri, rline in enumerate(record_lines):
                p.drawText(
                    QRectF(box_x, record_y + ri * 34, box_w, 34),
                    Qt.AlignCenter, rline,
                )

        p.end()


# ── Stage 1 ──────────────────────────────────────────────────────────

class Stage1Consent(QWidget):

    next_stage = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.stage_id = "stage_1_consent"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet(
            "QStackedWidget { border: none; background: transparent; }"
        )
        layout.addWidget(self._stack)

        self._boot = _BootScreen()
        self._report = _ReportScreen()
        self._consent = _ConsentFormScreen()

        self._stack.addWidget(self._boot)
        self._stack.addWidget(self._report)
        self._stack.addWidget(self._consent)

        self._boot.finished.connect(lambda: self._switch_to(1))
        self._report.finished.connect(lambda: self._switch_to(2))
        self._consent.finished.connect(lambda: self.next_stage.emit())

    def _switch_to(self, index):
        self._stack.setCurrentIndex(index)
        widget = self._stack.currentWidget()
        if hasattr(widget, "start"):
            widget.start()

    def on_enter(self):
        self._stack.setCurrentIndex(0)
        self._boot.start()

    def on_leave(self):
        self._boot.stop()
        self._report.stop()
        self._consent.stop()
