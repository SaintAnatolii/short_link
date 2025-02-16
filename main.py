# save this as app.py
from flask import Flask, redirect, render_template, request, url_for
import sqlite3
import random
import qrcode
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_url TEXT NOT NULL,
        short_code TEXT UNIQUE NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# ! функция для генерации коткого кода сайта
def generate_short_code():
    a = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    short_code = ''
    for _ in range(6):
        short_code  += random.choice(a)
    return short_code


def generate_qr_code(short_code):
    qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
    )
    qr.add_data(short_code)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    qr_path = f'static/qr_codes/{short_code.split("/")[-1]}.png'
    img.save(qr_path)
    return qr_path
@app.route("/", methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        original_url = request.form['original_url']
        short_code = generate_short_code()
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO urls (original_url, short_code) VALUES (?, ?)", (original_url, short_code))
            conn.commit()
            short_link = request.host_url + short_code
            qr_path = generate_qr_code(short_link)
        except:
            short_link = 'Произошла ошибка сервера'
            qr_path = None
        finally:
            conn.close()
        return render_template('index.html', short_link=short_link, qr_path=qr_path)
    return render_template('index.html', short_link='short_link')

@app.route('/<short_link>')
def redirect_to_url(short_link):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor() 
    cursor.execute('select * from urls where short_code = ?', [short_link])
    result = cursor.fetchone()
    conn.close()

    if result:
        return redirect(result[1])
    else:
        return '404\nКод не найден'


if  __name__ == "__main__":
    if not os.path.exists('static/qr_codes'):
        os.makedirs('static/qr_codes')
    init_db()
    app.run(debug=True)


