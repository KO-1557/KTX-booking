import uuid
from datetime import date
from typing import Optional

import bcrypt
import pymysql
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db import get_db

app = FastAPI()


# ---------- 요청 모델 ----------

class SignupRequest(BaseModel):
    username: str
    password: str
    name: str
    phone: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TicketRequest(BaseModel):
    users_id: int
    schedules_id: int
    seats_id: int


class PaymentRequest(BaseModel):
    tickets_id: int
    amount: int
    method: str


class SeasonPassRequest(BaseModel):
    users_id: int
    start_date: date
    end_date: date


# ---------- 회원 ----------

@app.post("/signup")
def signup(req: SignupRequest):
    password_hash = bcrypt.hashpw(req.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO USERS (USERNAME, PASSWORD_HASH, NAME, PHONE) VALUES (%s, %s, %s, %s)",
                (req.username, password_hash, req.name, req.phone),
            )
            new_id = cur.lastrowid
        conn.commit()
    except pymysql.err.IntegrityError:
        raise HTTPException(status_code=409, detail="이미 존재하는 아이디입니다.")
    finally:
        conn.close()

    return {"users_id": new_id, "username": req.username}


@app.post("/login")
def login(req: LoginRequest):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT USERS_ID, PASSWORD_HASH, NAME FROM USERS WHERE USERNAME = %s",
                (req.username,),
            )
            user = cur.fetchone()
    finally:
        conn.close()

    if user is None or not bcrypt.checkpw(
        req.password.encode("utf-8"), user["PASSWORD_HASH"].encode("utf-8")
    ):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")

    return {"users_id": user["USERS_ID"], "name": user["NAME"]}


# ---------- 노선 / 스케줄 / 좌석 ----------

@app.get("/routes")
def get_routes():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT ROUTES_ID, DEPARTURE_STATION, ARRIVE_STATION FROM ROUTES")
            rows = cur.fetchall()
    finally:
        conn.close()

    return rows


@app.get("/schedules")
def get_schedules(route_id: int):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT SCHEDULES_ID, TRAIN_NUMBER, DEPARTURE_TIME, ARRIVE_TIME"
                " FROM SCHEDULES WHERE ROUTES_ID = %s ORDER BY DEPARTURE_TIME",
                (route_id,),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    return rows


@app.get("/schedules/{schedules_id}/seats")
def get_seats(schedules_id: int):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT SEATS_ID, SEAT_NUMBER, STATUS FROM SEATS"
                " WHERE SCHEDULES_ID = %s ORDER BY SEAT_NUMBER",
                (schedules_id,),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    return rows


# ---------- 예매 / 결제 ----------

@app.post("/tickets")
def create_ticket(req: TicketRequest):
    barcode = uuid.uuid4().hex.upper()

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO TICKETS (USERS_ID, SCHEDULES_ID, SEATS_ID, BARCODE)"
                " VALUES (%s, %s, %s, %s)",
                (req.users_id, req.schedules_id, req.seats_id, barcode),
            )
            new_id = cur.lastrowid
            cur.execute(
                "UPDATE SEATS SET STATUS = 'BOOKED' WHERE SEATS_ID = %s",
                (req.seats_id,),
            )
        conn.commit()
    except pymysql.err.IntegrityError as e:
        conn.rollback()
        if e.args[0] == 1062:  # UNIQUE(SEATS_ID) 위반 → 이미 예매된 좌석
            raise HTTPException(status_code=409, detail="이미 예매된 좌석입니다.")
        raise HTTPException(status_code=400, detail="존재하지 않는 사용자/스케줄/좌석입니다.")
    finally:
        conn.close()

    return {"tickets_id": new_id, "barcode": barcode}


@app.post("/payments")
def create_payment(req: PaymentRequest):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO PAYMENTS (TICKETS_ID, AMOUNT, METHOD, STATUS)"
                " VALUES (%s, %s, %s, 'PAID')",
                (req.tickets_id, req.amount, req.method),
            )
            new_id = cur.lastrowid
        conn.commit()
    except pymysql.err.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="존재하지 않는 티켓입니다.")
    finally:
        conn.close()

    return {"payments_id": new_id, "status": "PAID"}


@app.get("/tickets/{tickets_id}")
def get_ticket(tickets_id: int):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT T.TICKETS_ID, T.BARCODE, T.CREATED_AT,"
                "       U.NAME, R.DEPARTURE_STATION, R.ARRIVE_STATION,"
                "       SC.TRAIN_NUMBER, SC.DEPARTURE_TIME, SC.ARRIVE_TIME,"
                "       SE.SEAT_NUMBER"
                " FROM TICKETS T"
                " JOIN USERS U ON T.USERS_ID = U.USERS_ID"
                " JOIN SCHEDULES SC ON T.SCHEDULES_ID = SC.SCHEDULES_ID"
                " JOIN SEATS SE ON T.SEATS_ID = SE.SEATS_ID"
                " JOIN ROUTES R ON SC.ROUTES_ID = R.ROUTES_ID"
                " WHERE T.TICKETS_ID = %s",
                (tickets_id,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 티켓입니다.")

    return row


# ---------- 정기권 ----------

@app.post("/season-passes")
def create_season_pass(req: SeasonPassRequest):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO SEASON_PASSES (USERS_ID, START_DATE, END_DATE)"
                " VALUES (%s, %s, %s)",
                (req.users_id, req.start_date, req.end_date),
            )
            new_id = cur.lastrowid
        conn.commit()
    except pymysql.err.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="존재하지 않는 사용자입니다.")
    finally:
        conn.close()

    return {"passes_id": new_id, "users_id": req.users_id}
