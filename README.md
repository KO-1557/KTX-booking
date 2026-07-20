# KTX 예매 앱 — 실행 / 접속 방법

PySide6(클라이언트) + FastAPI(서버) + MySQL(DB) 구조의 KTX 기차표 예매 데스크톱 앱.
프로젝트 배경·설계 결정은 [`DESIGN.md`](./DESIGN.md) 참고.

---

## 1. 사전 준비

### MySQL 실행 확인
DB는 서버만 접근한다. `KTX_BOOKING` 데이터베이스가 떠 있어야 한다.

```bash
systemctl is-active mysql        # active 여야 함
mysql -u root -p KTX_BOOKING -e "SHOW TABLES;"   # 7개 테이블 확인
```

- 접속 정보는 `.env`에 있음 (`DB_HOST=localhost`, `DB_PORT=3306`, `DB_USER=root`, `DB_NAME=KTX_BOOKING`).
- DB가 비어 있으면 `schema.sql`로 테이블 생성 후 시드 데이터를 넣는다.
  ```bash
  mysql -u root -p KTX_BOOKING < schema.sql
  ```

### 가상환경(venv)
의존성은 `venv/`에 이미 설치돼 있다 (`requirements.txt` 참고).

> **참고:** venv를 다른 PC/경로에서 복사해 왔다면 `venv/bin`의 python 심볼릭 링크가
> 깨져 `허가 거부`가 날 수 있다. 그럴 땐 링크만 다시 걸면 된다.
> ```bash
> cd venv/bin && rm -f python python3 python3.12
> ln -s /usr/bin/python3.12 python3.12 && ln -s python3.12 python && ln -s python3.12 python3
> ```
> 새 PC에서 처음부터 만들려면:
> ```bash
> python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
> ```

---

## 2. 실행 방법

**터미널 2개**가 필요하다 (서버 + 클라이언트).

### ① 서버 (FastAPI)
```bash
cd my_project
./venv/bin/python -m uvicorn main:app --port 8000
```
- 다른 노트북에서 접속하게 하려면 host를 열어 준다: `--host 0.0.0.0` 추가.

### ② 클라이언트 (PySide6 GUI)
```bash
cd my_project
./venv/bin/python app.py
```
- 다른 PC의 서버에 붙으려면 `api.py`의 `BASE_URL`을 서버 IP로 바꾼다.
  예: `BASE_URL = "http://192.168.0.10:8000"`

---

## 3. 접속 방법

### GUI 클라이언트
1. 앱을 실행하면 **로그인 화면**이 뜬다.
2. 계정이 없으면 **"계정이 없으신가요? 회원가입"** → 아이디/비밀번호/이름 입력 후 가입.
3. 로그인하면 하단 3탭(**예매 / 예매확인 / 정기권**)이 나온다.
   - **예매:** 노선 → 스케줄 선택 → 초록색(예매 가능) 좌석 클릭 → 결제까지 진행. 좌석 상태는 3초마다 자동 갱신(폴링).
   - **예매확인:** 티켓 번호로 예매 내역 조회.
   - **정기권:** 시작일/종료일 선택 후 발급.

### 서버 (FastAPI)
- Base URL: `http://127.0.0.1:8000`
- 자동 생성 API 문서(Swagger): `http://127.0.0.1:8000/docs`
- 헬스 체크 예:
  ```bash
  curl http://127.0.0.1:8000/routes
  ```

### 테스트 계정
| 아이디 | 비밀번호 |
|--------|----------|
| `test` | `1234`   |
| `hong` | `1234`   |

> 계정이 없으면 GUI의 회원가입으로 만들거나 API로 직접 생성:
> ```bash
> curl -X POST http://127.0.0.1:8000/signup \
>   -H "Content-Type: application/json" \
>   -d '{"username":"test","password":"1234","name":"테스터","phone":"010-0000-0000"}'
> ```

---

## 4. 종료

- 각 터미널에서 `Ctrl+C` (서버), GUI는 창을 닫으면 종료된다.
