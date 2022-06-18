import os
import requests

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def send_telegram(text: str):
    method = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    r = requests.get(method, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    })

    if r.status_code != 200:
        raise Exception(r)
