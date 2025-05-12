import os
import json
import datetime
from collections import defaultdict
import requests
import yadisk
import math
import random
import numpy as np
from config import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN

def get_token():
    url = "https://oauth.yandex.ru/token"
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': REFRESH_TOKEN,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    r = requests.post(url, data=data)
    return r.json().get('access_token') if r.status_code == 200 else None

def get_disk():
    token = get_token()
    if not token:
        raise RuntimeError("Не удалось получить токен")
    y = yadisk.YaDisk(token=token)
    if not y.check_token():
        raise RuntimeError("Токен недействителен")
    return y

def read_data(user):
    y = get_disk()
    remote = f"/Proj/{user}.json"
    local = f"{user}.json"
    if not y.exists(remote):
        return {'income':[], 'expenses':[], 'budgets':{}, 'goals':[],
                'savings':0.0, 'reminders':[], 'plans':[]}
    y.download(remote, local, overwrite=True)
    with open(local, encoding='utf-8') as f:
        data = json.load(f)
    os.remove(local)
    return data

def save_data(user, data):
    y = get_disk()
    remote_dir = "/Proj"
    remote = f"{remote_dir}/{user}.json"
    local = f"{user}.json"
    with open(local, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    if not y.exists(remote_dir):
        y.mkdir(remote_dir)
    y.upload(local, remote, overwrite=True)
    os.remove(local)

def add_income(dt, date, amount, source):
    dt.setdefault('income', []).append({'date': date, 'amount': amount, 'source': source})
    return dt

def add_expense(dt, date, amount, category):
    dt.setdefault('expenses', []).append({'date': date, 'amount': amount, 'category': category})
    return dt

def total_income(dt):
    return sum(i['amount'] for i in dt.get('income', []))

def total_expenses(dt):
    return sum(e['amount'] for e in dt.get('expenses', []))

def remaining_balance(dt):
    return total_income(dt) - total_expenses(dt)

def income_expense_stats(dt):
    inc = total_income(dt)
    exp = total_expenses(dt)
    return {'total_income': inc, 'total_expenses': exp, 'balance': inc - exp}

def add_reminder(dt, text, date):
    dt.setdefault('reminders', []).append({'text': text, 'date': date})
    return dt

def list_reminders(dt):
    return dt.get('reminders', [])

def get_next_russian_holidays(n=5):
    """Возвращает список из n ближайших праздников (date ISO, name, days_left)."""
    holidays = [
        (1,1,"Новый Год"),(1,7,"Рождество"),(2,23,"День защитника Отечества"),
        (3,8,"Международный женский день"),(5,1,"Праздник Весны и Труда"),
        (5,9,"День Победы"),(6,12,"День России"),(9,1,"День знаний"),
        (10,5,"День учителя"),(11,4,"День народного единства"),
        (12,31,"Старый Новый Год")
    ]
    today = datetime.date.today()
    upcoming = []
    for m,d,name in holidays*2:
        if isinstance(m, tuple): 
            m,d,name = m
        try:
            hol = datetime.date(today.year if (m,d)>(today.month,today.day) else today.year+1, m, d)
        except:
            continue
        delta = (hol - today).days
        upcoming.append((hol.isoformat(), name, delta))
    upcoming.sort(key=lambda x: x[2])
    return upcoming[:n]
