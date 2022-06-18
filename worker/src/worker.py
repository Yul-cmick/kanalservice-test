import httplib2
import datetime
import os
import psycopg2
import time

import apiclient.discovery  # noqa
from oauth2client.service_account import ServiceAccountCredentials

from exchange_rate import get_usd_exchange_rate
from telegram_channel import send_telegram

# Environment variables
POSTGRES_DB = os.environ['POSTGRES_DB']
POSTGRES_USER = os.environ['POSTGRES_USER']
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
POSTGRES_HOST = os.environ['POSTGRES_HOST']
SPREADSHEET_ID = os.environ['SPREADSHEET_ID']
SPREADSHEET_SHEET = os.environ['SPREADSHEET_SHEET']
CREDENTIALS_FILE = os.environ['CREDENTIALS_FILE']
CREDENTIALS_FILE_PATH = f'/credentials/{CREDENTIALS_FILE}'

conn = psycopg2.connect(
    dbname=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST)
cursor = conn.cursor()

# Читаем ключи из файла
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE_PATH, [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'])

# Авторизуемся в системе
httpAuth = credentials.authorize(httplib2.Http())

# Выбираем работу с таблицами и 4 версию API
service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

all_outdated_order_ids = set()

while True:
    print('Scan spreadsheet')
    cursor.execute('''TRUNCATE public."Orders"''')
    conn.commit()

    scan_row_count = 50
    start_row = 2
    outdated_order_ids = set()

    while True:
        end_row = start_row + scan_row_count - 1

        ranges = [f'{SPREADSHEET_SHEET}!A{start_row}:D{end_row}']

        results = service \
            .spreadsheets() \
            .values() \
            .batchGet(
                spreadsheetId=SPREADSHEET_ID,
                ranges=ranges,
                valueRenderOption='FORMATTED_VALUE',
                dateTimeRenderOption='FORMATTED_STRING'
            ).execute()

        raw_data = results['valueRanges'][0].get('values', None)
        if raw_data is None:
            break

        for row in raw_data:
            id = int(row[0])
            order_id = int(row[1])
            cost_usd = round(float(row[2]), 2)
            delivery_date = datetime.datetime.strptime(row[3], '%d.%m.%Y')

            if datetime.datetime.now() > delivery_date:
                outdated_order_ids.add(order_id)

            usd_exchange_rate = get_usd_exchange_rate(delivery_date)
            cost_rub = round(cost_usd * usd_exchange_rate, 2)

            cursor.execute(
                '''INSERT INTO public."Orders" (id, order_id, cost_usd, delivery_date, cost_rub) VALUES (%s, %s, %s, %s, %s);''',
                (id, order_id, cost_usd, delivery_date, cost_rub))
            conn.commit()

        start_row = end_row + 1

    new_outdated_order_ids = outdated_order_ids - all_outdated_order_ids
    outdated_order_count = len(new_outdated_order_ids)
    
    if outdated_order_count > 0:
        noun = "новых заказов" if len(all_outdated_order_ids) > 0 else " заказов"
        send_telegram(f'Найдено {outdated_order_count} {noun} с несоблюденным сроком поставки')
    
    all_outdated_order_ids |= new_outdated_order_ids

    time.sleep(15)
