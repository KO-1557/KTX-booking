# KTX 예매 앱 — 설계 근거

이 문서는 **"왜 이렇게 만들었나"**를 기록한다. (실행·접속 방법은 [`README.md`](./README.md) 참고)
포트폴리오 목적이며, 면접에서 기술 결정을 설명하는 것이 핵심이다.

---

## 1. 개요

KTX 기차표 예매 데스크톱 앱.

- **스택:** PySide6(클라이언트) + FastAPI(백엔드) + MySQL(DB)
- **구조 원칙:** 서버/클라이언트 분리 — **DB는 오직 서버만 접근**한다. 클라이언트는 서버 API로만
  데이터에 접근하므로, 다른 노트북에서 실행하려면 그 노트북엔 PySide6 + requests만 있으면 된다
  (`api.py`의 서버 주소만 바꿔서).

---

## 2. 면접용 핵심 기술 결정 3가지

구현 중 바꾸지 말 것. 이 앱 서사의 핵심이다.

### ① 동시 예매 방지 = DB UNIQUE 제약
- TICKETS 테이블에 `UNIQUE(SEATS_ID)`.
- async/await만으로는 "좌석 확인 → 예매 확정" 사이의 경합(check-then-confirm race)을 못 막는다.
- 동시 요청이 와도 DB 제약이 **하나만 성공**시키고, 나머지는 `IntegrityError(1062)` →
  `409 "이미 예매된 좌석"`으로 응답한다.
- 재현(면접용 장면): 같은 좌석에 `curl`을 두 번 동시에 → 하나만 200, 하나는 409.

### ② 비밀번호 = bcrypt (SHA-256 아님)
- bcrypt는 cost factor로 해시 계산을 의도적으로 느리게 만들어 무차별 대입을 방어한다.
- salt가 해시 문자열 안에 내장되어 별도 salt 컬럼이 필요 없다.
- 저장 시 `hashpw` 결과를 bytes → decode 후 저장, 검증 시 `checkpw`로 다시 encode해 비교.

### ③ 폴링 vs WebSocket = 폴링
- 실시간 push가 꼭 필요하진 않다 → 요청-응답으로 충분하고, WebSocket 재연결 복잡도를 회피.
- 좌석 상태는 클라이언트에서 `QTimer(3000ms)`로 폴링해 색만 다시 칠한다.

---

## 3. DB 스키마 (MySQL 8.0, `KTX_BOOKING`)

- 7개 테이블: `USERS`, `ROUTES`, `SCHEDULES`, `SEATS`, `TICKETS`, `PAYMENTS`, `SEASON_PASSES`
- 스키마 원본: [`schema.sql`](./schema.sql)
- 시드 데이터(임의값): ROUTES 3개(서울→부산/광주송정/강릉), SCHEDULES 3개(부산 노선),
  SEATS 48개(스케줄당 1A~4D 16석).
- **SEASON_PASSES는 의도적으로 ROUTES_ID가 없다** — 전 노선 정기권 개념으로 단순화(단독 포폴).

---

## 4. API 엔드포인트 (`main.py`)

**전부 sync `def`** (async 아님). pymysql이 블로킹 드라이버라 FastAPI가 스레드풀에서 처리하게 둔다.

| 엔드포인트 | 하는 일 |
|---|---|
| `POST /signup` | bcrypt 해싱 저장, 중복 아이디 → 409 |
| `POST /login` | checkpw 검증, 실패 → 401 (아이디/비번 메시지 통일 = 사용자 열거 방지) |
| `GET /routes` | 노선 목록 |
| `GET /schedules?route_id=` | 노선의 스케줄 (쿼리 파라미터) |
| `GET /schedules/{id}/seats` | 좌석 상태 (폴링 대상) |
| `POST /tickets` | 티켓 INSERT + 좌석 BOOKED UPDATE (한 트랜잭션). UNIQUE(SEATS_ID) 위반 1062 → 409 |
| `POST /payments` | mock 결제, STATUS='PAID' |
| `GET /tickets/{id}` | 4개 테이블 JOIN → 바코드/예매확인 정보 |
| `POST /season-passes` | 정기권 발급 |

---

## 5. 클라이언트 통신 계층 (`api.py`)

- `requests` 얇은 래퍼(클라이언트판 `db.py`). fastapi/db/bcrypt/SQL 없음.
- 패턴: `requests`로 보내고 → 200이면 `resp.json()`, 아니면 `None`.

### 네이밍 규칙 (중요)
- **보낼 때**(`json=` / `params=` 키) → **소문자**. `main.py` Pydantic 필드명과 일치
  (`users_id`, `route_id` 등).
- **받을 때**(`resp.json()` dict 키) → **대문자**. DictCursor가 DB 컬럼명을 그대로 반환
  (`ROUTES_ID`, `STATUS` 등).
- URL 경로에 값 박기(`/schedules/{id}/seats`) vs 쿼리(`params={"route_id":..}`) 구분:
  서버가 `{}`로 정의한 자리만 경로에 박는다.

---

## 6. 클라이언트 UI 구조 (`app.py`)

- `QStackedWidget`으로 화면 전환: 로그인 ↔ 회원가입 ↔ 로그인 이후 화면.
- 로그인 이후: 상단 헤더 바(로그아웃) + 하단 3탭 네비게이션(예매 / 예매확인 / 정기권).
- 좌석맵은 `QGridLayout` + `QPushButton` 그리드. 예매 가능=초록, 예매 완료=회색.
- 연결 패턴(모든 화면 동일): `버튼.clicked.connect(슬롯)` → 슬롯에서 `api.함수()` 호출 →
  돌아온 dict/list를 위젯에 반영.
- 전역 QSS 테마(KTX 블루 포인트, 카드형 레이아웃)를 `QApplication`에 한 번 적용.
