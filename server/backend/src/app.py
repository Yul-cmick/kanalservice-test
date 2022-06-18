from flask import Flask, jsonify, make_response
import os
import psycopg2

# Environment variables
POSTGRES_DB = os.environ['POSTGRES_DB']
POSTGRES_USER = os.environ['POSTGRES_USER']
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
POSTGRES_HOST = os.environ['POSTGRES_HOST']

conn = psycopg2.connect(
    dbname=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST)

# Create table if not exist
cur = conn.cursor()
cur.execute("select exists(select * from information_schema.tables where table_schema='public' and table_name=%s)", ('Orders',))
if not cur.fetchone()[0]:
    cur.execute('''
CREATE TABLE public."Orders" (
    id numeric NOT NULL,
    order_id numeric NOT NULL,
    cost_usd numeric NOT NULL,
    delivery_date date NOT NULL,
    cost_rub numeric NOT NULL
);
ALTER TABLE ONLY public."Orders"
    ADD CONSTRAINT "Orders_pkey" PRIMARY KEY (order_id);
    ''')
cur.close()
conn.commit()

app = Flask(__name__)


@app.route('/api/total_sum')
def total_sum():
    cursor = conn.cursor()
    sql = '''SELECT SUM("cost_rub") FROM public."Orders";'''
    cursor.execute(sql)
    row = cursor.fetchone()
    cursor.close()
    result = {
        'total_sum': float(row[0])
    }
    return jsonify(result)


@app.route('/api/all_orders')
def all_orders():
    cursor = conn.cursor()
    sql = '''SELECT * FROM public."Orders" LIMIT 25;'''
    cursor.execute(sql)
    orders = cursor.fetchall()
    cursor.close()
    result = {
        'orders': []
    }
    for order in orders:
        result['orders'].append({
            'id': int(order[0]),
            'order_id': int(order[1]),
            'delivery_date': order[3].strftime('%d.%m.%Y'),
            'usd_cost': float(order[2]),
            'rub_cost': float(order[4]),
        })
    return jsonify(result)
