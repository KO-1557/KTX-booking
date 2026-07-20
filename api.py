import requests


BASE_URL = "http://127.0.0.1:8000"

def login(username, password):
    response = requests.post(f"{BASE_URL}/login",
                             json={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()
    return None

def register(username, password, name, phone):
    response = requests.post(f"{BASE_URL}/signup",
                             json={"username": username, "password": password,
                                   "name" :name, "phone": phone})
    if response.status_code == 200:
        return response.json()
    return None

def get_routes():
    response = requests.get(f"{BASE_URL}/routes")
    return response.json()

def get_schedules(route_id):
    response = requests.get(f"{BASE_URL}/schedules",
                            {"route_id": route_id})
    return response.json()

def get_seats(schedules_id):
    response = requests.get(f"{BASE_URL}/schedules/{schedules_id}/seats")
    if response.status_code == 200:
        return response.json()
    return None

def create_ticket(users_id, schedules_id, seats_id):
    response = requests.post(f"{BASE_URL}/tickets",
                             json={"users_id": users_id, "schedules_id": schedules_id,
                                   "seats_id": seats_id})
    if response.status_code == 200:
        return response.json()
    return None

def create_payment(tickets_id, amount, method):
    response = requests.post(f"{BASE_URL}/payments",
                             json={"tickets_id": tickets_id, "amount": amount,
                                   "method": method})
    if response.status_code == 200:
        return response.json()
    return None

def get_ticket(tickets_id):
    response = requests.get(f"{BASE_URL}/tickets/{tickets_id}")
    if response.status_code == 200:
        return response.json()
    return None

def create_season_pass(users_id, start_date, end_date):
    response = requests.post(f"{BASE_URL}/season-passes",
                             json={"users_id": users_id, "start_date": start_date,
                                   "end_date": end_date})
    if response.status_code == 200:
        return response.json()
    return None