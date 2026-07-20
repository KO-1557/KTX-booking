import sys

from PySide6.QtCore import QDate, QTimer, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QDateEdit,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import api


# ============================================================
# 전역 스타일 (QSS) — 앱 전체에 한 번만 적용
# ============================================================
STYLESHEET = """
QWidget {
    background-color: #f4f6fa;
    color: #1f2937;
    font-family: 'Segoe UI', 'Noto Sans KR', 'Malgun Gothic', sans-serif;
    font-size: 14px;
}

/* 카드 (로그인/회원가입 등 흰 패널) */
QFrame#Card {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
}

/* 상단 헤더 바 */
QFrame#Header {
    background-color: #0052a4;
    border: none;
}
QLabel#HeaderTitle {
    color: #ffffff;
    font-size: 18px;
    font-weight: 700;
    background: transparent;
}

/* 텍스트 계층 */
QLabel#Title    { font-size: 24px; font-weight: 700; color: #0b2e59; }
QLabel#Subtitle { font-size: 13px; color: #6b7280; }
QLabel#Section  { font-size: 13px; font-weight: 700; color: #374151; }
QLabel#Field    { font-size: 12px; font-weight: 600; color: #6b7280; }
QLabel#Result {
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 14px;
    font-size: 13px;
    color: #111827;
}

/* 입력 위젯 */
QLineEdit, QComboBox, QDateEdit {
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    padding: 10px 12px;
    font-size: 14px;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 1px solid #0052a4;
}
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    selection-background-color: #0052a4;
    selection-color: #ffffff;
    outline: none;
}

/* 기본(주요) 버튼 */
QPushButton#Primary {
    background-color: #0052a4;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 12px;
    font-size: 15px;
    font-weight: 700;
}
QPushButton#Primary:hover  { background-color: #0060c0; }
QPushButton#Primary:pressed { background-color: #003f80; }

/* 보조(외곽선) 버튼 */
QPushButton#Ghost {
    background-color: transparent;
    color: #0052a4;
    border: none;
    font-size: 13px;
    font-weight: 600;
    padding: 6px;
}
QPushButton#Ghost:hover { color: #0060c0; }

/* 하단 탭 네비게이션 */
QFrame#NavBar {
    background-color: #ffffff;
    border-top: 1px solid #e5e7eb;
}
QPushButton#NavTab {
    background-color: transparent;
    color: #9ca3af;
    border: none;
    border-top: 3px solid transparent;
    padding: 12px 0;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#NavTab:hover   { color: #4b5563; }
QPushButton#NavTab:checked {
    color: #0052a4;
    border-top: 3px solid #0052a4;
}
"""


def add_shadow(widget):
    """카드에 부드러운 그림자를 준다."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(28)
    shadow.setXOffset(0)
    shadow.setYOffset(6)
    shadow.setColor(QColor(15, 46, 89, 40))
    widget.setGraphicsEffect(shadow)


def make_card():
    """흰색 카드 프레임 하나 생성 (내부 레이아웃은 호출부에서)."""
    card = QFrame()
    card.setObjectName("Card")
    add_shadow(card)
    return card


# ============================================================
# 로그인 화면
# ============================================================
class LoginWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.id_edit = QLineEdit()
        self.id_edit.setPlaceholderText("아이디")

        self.pw_edit = QLineEdit()
        self.pw_edit.setPlaceholderText("비밀번호")
        self.pw_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw_edit.returnPressed.connect(self.on_login)

        self.login_btn = QPushButton("로그인")
        self.login_btn.setObjectName("Primary")

        self.signup_btn = QPushButton("계정이 없으신가요?  회원가입")
        self.signup_btn.setObjectName("Ghost")
        self.signup_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        title = QLabel("KTX 예매")
        title.setObjectName("Title")
        subtitle = QLabel("로그인하고 열차를 예매하세요")
        subtitle.setObjectName("Subtitle")

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(32, 36, 32, 28)
        card_layout.setSpacing(14)
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(12)
        card_layout.addWidget(QLabel("아이디", objectName="Field"))
        card_layout.addWidget(self.id_edit)
        card_layout.addWidget(QLabel("비밀번호", objectName="Field"))
        card_layout.addWidget(self.pw_edit)
        card_layout.addSpacing(8)
        card_layout.addWidget(self.login_btn)
        card_layout.addWidget(self.signup_btn)

        card = make_card()
        card.setLayout(card_layout)
        card.setFixedWidth(340)

        outer = QVBoxLayout()
        outer.addStretch()
        outer.addWidget(card, alignment=Qt.AlignmentFlag.AlignHCenter)
        outer.addStretch()
        self.setLayout(outer)

        self.login_btn.clicked.connect(self.on_login)
        self.signup_btn.clicked.connect(self.main_window.show_signup)

    def on_login(self):
        user = api.login(self.id_edit.text(), self.pw_edit.text())
        if user is None:
            QMessageBox.warning(self, "로그인 실패", "아이디 또는 비밀번호가 올바르지 않습니다.")
            return

        self.main_window.current_user_id = user["users_id"]
        self.pw_edit.clear()
        self.main_window.on_login_success()

    def prefill_username(self, username):
        self.id_edit.setText(username)
        self.pw_edit.clear()
        self.pw_edit.setFocus()


# ============================================================
# 회원가입 화면
# ============================================================
class SignupWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.id_edit = QLineEdit()
        self.id_edit.setPlaceholderText("아이디")

        self.pw_edit = QLineEdit()
        self.pw_edit.setPlaceholderText("비밀번호")
        self.pw_edit.setEchoMode(QLineEdit.EchoMode.Password)

        self.pw_confirm_edit = QLineEdit()
        self.pw_confirm_edit.setPlaceholderText("비밀번호 확인")
        self.pw_confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("이름")

        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("전화번호 (선택)")

        self.signup_btn = QPushButton("회원가입")
        self.signup_btn.setObjectName("Primary")

        self.back_btn = QPushButton("이미 계정이 있으신가요?  로그인")
        self.back_btn.setObjectName("Ghost")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        title = QLabel("회원가입")
        title.setObjectName("Title")
        subtitle = QLabel("KTX 예매 계정을 만드세요")
        subtitle.setObjectName("Subtitle")

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(32, 32, 32, 24)
        card_layout.setSpacing(10)
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(8)
        for label, widget in (
            ("아이디", self.id_edit),
            ("비밀번호", self.pw_edit),
            ("비밀번호 확인", self.pw_confirm_edit),
            ("이름", self.name_edit),
            ("전화번호 (선택)", self.phone_edit),
        ):
            card_layout.addWidget(QLabel(label, objectName="Field"))
            card_layout.addWidget(widget)
        card_layout.addSpacing(6)
        card_layout.addWidget(self.signup_btn)
        card_layout.addWidget(self.back_btn)

        card = make_card()
        card.setLayout(card_layout)
        card.setFixedWidth(340)

        outer = QVBoxLayout()
        outer.addStretch()
        outer.addWidget(card, alignment=Qt.AlignmentFlag.AlignHCenter)
        outer.addStretch()
        self.setLayout(outer)

        self.signup_btn.clicked.connect(self.on_signup)
        self.back_btn.clicked.connect(self.main_window.show_login)

    def on_signup(self):
        username = self.id_edit.text().strip()
        password = self.pw_edit.text()
        password_confirm = self.pw_confirm_edit.text()
        name = self.name_edit.text().strip()
        phone = self.phone_edit.text().strip() or None

        if not username or not password or not name:
            QMessageBox.warning(self, "입력 오류", "아이디, 비밀번호, 이름은 필수입니다.")
            return
        if password != password_confirm:
            QMessageBox.warning(self, "입력 오류", "비밀번호가 일치하지 않습니다.")
            return

        result = api.register(username, password, name, phone)
        if result is None:
            QMessageBox.warning(self, "회원가입 실패", "이미 존재하는 아이디이거나 요청이 잘못되었습니다.")
            return

        QMessageBox.information(self, "회원가입 완료", "회원가입이 완료되었습니다. 로그인해 주세요.")
        self._clear()
        self.main_window.show_login(prefill_username=username)

    def _clear(self):
        for edit in (self.id_edit, self.pw_edit, self.pw_confirm_edit, self.name_edit, self.phone_edit):
            edit.clear()


# ============================================================
# 예매 화면 (노선 → 스케줄 → 좌석)
# ============================================================
class BookingWidget(QWidget):
    SEAT_GRID_COLS = 4

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_schedule_id = None
        self.seat_buttons = {}  # seats_id -> QPushButton

        self.route_combo = QComboBox()
        self.schedule_combo = QComboBox()

        self.seat_grid_widget = QWidget()
        self.seat_grid_layout = QGridLayout()
        self.seat_grid_layout.setSpacing(8)
        self.seat_grid_widget.setLayout(self.seat_grid_layout)

        # 좌석 영역은 스크롤 가능하게 (좌석 많아져도 대응)
        seat_scroll = QScrollArea()
        seat_scroll.setWidgetResizable(True)
        seat_scroll.setWidget(self.seat_grid_widget)
        seat_scroll.setFrameShape(QFrame.Shape.NoFrame)

        legend = QLabel("초록 = 예매 가능  ·  회색 = 예매 완료")
        legend.setObjectName("Subtitle")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        layout.addWidget(QLabel("노선", objectName="Section"))
        layout.addWidget(self.route_combo)
        layout.addWidget(QLabel("스케줄", objectName="Section"))
        layout.addWidget(self.schedule_combo)
        layout.addSpacing(6)
        layout.addWidget(QLabel("좌석 선택", objectName="Section"))
        layout.addWidget(legend)
        layout.addWidget(seat_scroll, stretch=1)
        self.setLayout(layout)

        self.route_combo.currentIndexChanged.connect(self.on_route_changed)
        self.schedule_combo.currentIndexChanged.connect(self.on_schedule_changed)

        # 좌석 상태 폴링: 화면 열려있는 동안 3초마다 최신 좌석 상태로 갱신
        self.poll_timer = QTimer()
        self.poll_timer.setInterval(3000)
        self.poll_timer.timeout.connect(self.refresh_seats)

    def load_routes(self):
        routes = api.get_routes()
        self.route_combo.clear()
        for route in routes:
            label = f'{route["DEPARTURE_STATION"]} → {route["ARRIVE_STATION"]}'
            self.route_combo.addItem(label, route["ROUTES_ID"])

    def on_route_changed(self, index):
        self.poll_timer.stop()
        self.current_schedule_id = None
        self._clear_seat_grid()
        if index < 0:
            return

        route_id = self.route_combo.currentData()
        schedules = api.get_schedules(route_id)
        self.schedule_combo.clear()
        for schedule in schedules:
            label = f'{schedule["TRAIN_NUMBER"]} ({schedule["DEPARTURE_TIME"]} → {schedule["ARRIVE_TIME"]})'
            self.schedule_combo.addItem(label, schedule["SCHEDULES_ID"])

    def on_schedule_changed(self, index):
        self.poll_timer.stop()
        self.current_schedule_id = None
        self._clear_seat_grid()
        if index < 0:
            return

        self.current_schedule_id = self.schedule_combo.currentData()
        self.build_seat_grid()   # 좌석 버튼은 스케줄이 바뀔 때 한 번만 생성
        self.poll_timer.start()  # 이후엔 폴링으로 색만 갱신

    def _clear_seat_grid(self):
        for btn in self.seat_buttons.values():
            self.seat_grid_layout.removeWidget(btn)
            btn.deleteLater()
        self.seat_buttons.clear()

    def build_seat_grid(self):
        """스케줄 선택 시 좌석 버튼을 새로 생성한다 (1회)."""
        self._clear_seat_grid()
        seats = api.get_seats(self.current_schedule_id)
        if seats is None:
            return

        for i, seat in enumerate(seats):
            btn = QPushButton(seat["SEAT_NUMBER"])
            btn.setFixedHeight(48)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            seats_id = seat["SEATS_ID"]
            btn.clicked.connect(lambda checked=False, sid=seats_id: self.on_seat_clicked(sid))
            self.seat_grid_layout.addWidget(btn, i // self.SEAT_GRID_COLS, i % self.SEAT_GRID_COLS)
            self.seat_buttons[seats_id] = btn
            self._apply_seat_state(btn, seat["STATUS"])

    def refresh_seats(self):
        """폴링(3초): 기존 버튼을 지우지 않고 색/활성 상태만 다시 칠한다."""
        if self.current_schedule_id is None:
            return

        seats = api.get_seats(self.current_schedule_id)
        if seats is None:
            return

        # 좌석 구성 자체가 달라졌으면(드묾) 다시 생성
        if len(seats) != len(self.seat_buttons):
            self.build_seat_grid()
            return

        for seat in seats:
            btn = self.seat_buttons.get(seat["SEATS_ID"])
            if btn is not None:
                self._apply_seat_state(btn, seat["STATUS"])

    @staticmethod
    def _apply_seat_state(btn, status):
        available = status == "AVAILABLE"
        btn.setEnabled(available)
        if available:
            btn.setStyleSheet(
                "QPushButton {"
                "  background-color: #e7f6ec; color: #128a3f;"
                "  border: 1px solid #7bcf9a; border-radius: 8px;"
                "  font-weight: 600;"
                "}"
                "QPushButton:hover { background-color: #128a3f; color: #ffffff; }"
            )
        else:
            btn.setStyleSheet(
                "QPushButton {"
                "  background-color: #f3f4f6; color: #9ca3af;"
                "  border: 1px solid #e5e7eb; border-radius: 8px;"
                "}"
            )

    def on_seat_clicked(self, seats_id):
        answer = QMessageBox.question(self, "예매 확인", "이 좌석을 예매하시겠습니까?")
        if answer != QMessageBox.StandardButton.Yes:
            return

        ticket = api.create_ticket(self.main_window.current_user_id, self.current_schedule_id, seats_id)
        if ticket is None:
            QMessageBox.warning(self, "예매 실패", "이미 예매된 좌석이거나 잘못된 요청입니다.")
            self.refresh_seats()
            return

        payment = api.create_payment(ticket["tickets_id"], 10000, "CARD")
        if payment is None:
            QMessageBox.warning(self, "결제 실패", "결제 처리 중 오류가 발생했습니다.")
            return

        QMessageBox.information(
            self, "예매 완료",
            f'예매가 완료되었습니다.\n티켓 번호: {ticket["tickets_id"]}\n바코드: {ticket["barcode"]}'
        )
        self.refresh_seats()


# ============================================================
# 예매확인 화면
# ============================================================
class TicketCheckWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.tickets_id_edit = QLineEdit()
        self.tickets_id_edit.setPlaceholderText("티켓 번호")

        self.search_btn = QPushButton("조회")
        self.search_btn.setObjectName("Primary")

        self.result_label = QLabel("티켓 번호를 입력하고 조회하세요.")
        self.result_label.setObjectName("Result")
        self.result_label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(QLabel("예매 확인", objectName="Section"))
        layout.addWidget(self.tickets_id_edit)
        layout.addWidget(self.search_btn)
        layout.addSpacing(6)
        layout.addWidget(self.result_label)
        layout.addStretch()
        self.setLayout(layout)

        self.search_btn.clicked.connect(self.on_search)
        self.tickets_id_edit.returnPressed.connect(self.on_search)

    def on_search(self):
        text = self.tickets_id_edit.text()
        if not text.isdigit():
            QMessageBox.warning(self, "입력 오류", "티켓 번호는 숫자여야 합니다.")
            return

        ticket = api.get_ticket(int(text))
        if ticket is None:
            self.result_label.setText("존재하지 않는 티켓입니다.")
            return

        self.result_label.setText(
            f'예매자: {ticket["NAME"]}\n'
            f'구간: {ticket["DEPARTURE_STATION"]} → {ticket["ARRIVE_STATION"]}\n'
            f'열차: {ticket["TRAIN_NUMBER"]}\n'
            f'출발: {ticket["DEPARTURE_TIME"]} / 도착: {ticket["ARRIVE_TIME"]}\n'
            f'좌석: {ticket["SEAT_NUMBER"]}\n'
            f'바코드: {ticket["BARCODE"]}'
        )


# ============================================================
# 정기권 화면
# ============================================================
class SeasonPassWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.start_edit = QDateEdit(QDate.currentDate())
        self.start_edit.setCalendarPopup(True)

        self.end_edit = QDateEdit(QDate.currentDate().addMonths(1))
        self.end_edit.setCalendarPopup(True)

        self.create_btn = QPushButton("정기권 발급")
        self.create_btn.setObjectName("Primary")

        self.status_label = QLabel("전 노선 정기권을 발급합니다.")
        self.status_label.setObjectName("Result")
        self.status_label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(QLabel("정기권 발급", objectName="Section"))
        layout.addWidget(QLabel("시작일", objectName="Field"))
        layout.addWidget(self.start_edit)
        layout.addWidget(QLabel("종료일", objectName="Field"))
        layout.addWidget(self.end_edit)
        layout.addSpacing(6)
        layout.addWidget(self.create_btn)
        layout.addSpacing(6)
        layout.addWidget(self.status_label)
        layout.addStretch()
        self.setLayout(layout)

        self.create_btn.clicked.connect(self.on_create)

    def on_create(self):
        start_date = self.start_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_edit.date().toString("yyyy-MM-dd")

        season_pass = api.create_season_pass(self.main_window.current_user_id, start_date, end_date)
        if season_pass is None:
            QMessageBox.warning(self, "발급 실패", "정기권 발급에 실패했습니다.")
            return

        self.status_label.setText(f'정기권이 발급되었습니다. (번호: {season_pass["passes_id"]})')


# ============================================================
# 로그인 이후 화면: 헤더 + 콘텐츠 + 하단 3탭 네비게이션
# ============================================================
class MainAppWidget(QWidget):
    TABS = ("예매", "예매확인", "정기권")

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.booking_widget = BookingWidget(main_window)
        self.ticket_check_widget = TicketCheckWidget(main_window)
        self.season_pass_widget = SeasonPassWidget(main_window)

        self.tab_stack = QStackedWidget()
        self.tab_stack.addWidget(self.booking_widget)       # index 0
        self.tab_stack.addWidget(self.ticket_check_widget)  # index 1
        self.tab_stack.addWidget(self.season_pass_widget)   # index 2

        # 헤더 바
        header_title = QLabel("KTX 예매")
        header_title.setObjectName("HeaderTitle")
        logout_btn = QPushButton("로그아웃")
        logout_btn.setObjectName("Ghost")
        logout_btn.setStyleSheet("QPushButton#Ghost { color: #ffffff; }")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self.main_window.logout)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 0, 16, 0)
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addWidget(logout_btn)
        header = QFrame()
        header.setObjectName("Header")
        header.setFixedHeight(56)
        header.setLayout(header_layout)

        # 하단 탭 네비게이션 (세그먼트형)
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        for index, name in enumerate(self.TABS):
            tab_btn = QPushButton(name)
            tab_btn.setObjectName("NavTab")
            tab_btn.setCheckable(True)
            tab_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            tab_btn.clicked.connect(lambda checked=False, i=index: self.tab_stack.setCurrentIndex(i))
            self.nav_group.addButton(tab_btn, index)
            nav_layout.addWidget(tab_btn)
        self.nav_group.button(0).setChecked(True)
        nav_bar = QFrame()
        nav_bar.setObjectName("NavBar")
        nav_bar.setLayout(nav_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(header)
        layout.addWidget(self.tab_stack, stretch=1)
        layout.addWidget(nav_bar)
        self.setLayout(layout)

    def refresh(self):
        self.tab_stack.setCurrentIndex(0)
        self.nav_group.button(0).setChecked(True)
        self.booking_widget.load_routes()


# ============================================================
# 최상위 창: 로그인 ↔ 회원가입 ↔ 로그인 이후 화면 전환
# ============================================================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KTX 예매")
        self.resize(420, 640)

        self.current_user_id = None

        self.login_widget = LoginWidget(self)
        self.signup_widget = SignupWidget(self)
        self.main_app_widget = MainAppWidget(self)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.login_widget)      # index 0
        self.stack.addWidget(self.signup_widget)     # index 1
        self.stack.addWidget(self.main_app_widget)   # index 2

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)
        self.setLayout(layout)

    def show_login(self, prefill_username=None):
        if prefill_username:
            self.login_widget.prefill_username(prefill_username)
        self.stack.setCurrentIndex(0)

    def show_signup(self):
        self.stack.setCurrentIndex(1)

    def on_login_success(self):
        self.main_app_widget.refresh()
        self.stack.setCurrentIndex(2)

    def logout(self):
        self.current_user_id = None
        self.booking_widget_poll_stop()
        self.show_login()

    def booking_widget_poll_stop(self):
        self.main_app_widget.booking_widget.poll_timer.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
