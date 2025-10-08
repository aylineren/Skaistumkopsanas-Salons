from flask import Flask, render_template, redirect, url_for, request, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = '12345'

DATABASE = 'klienti.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            CREATE TABLE klienti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

init_db()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/pakalpojumi')
def pakalpojumi():
    return render_template('pakalpojumi.html')

@app.route('/klienti')
def klienti():
    return render_template('klienti.html')

class Skaistumkopsana:
    def __init__(
        self,
        pakalpojuma_kategorija,
        pakalpojuma_nosaukums,
        pakalpojuma_atlaide,
        pakalpojuma_cena,
        laiks_pieejams,
        klients_vards,
        klients_uzvards,
        klients_pk,
        klients_tel_numurs,
        pakalpojuma_datums
    ):
        self.pakalpojuma_kategorija = pakalpojuma_kategorija
        self.pakalpojuma_nosaukums = pakalpojuma_nosaukums
        self.pakalpojuma_atlaide = pakalpojuma_atlaide
        self.pakalpojuma_cena = pakalpojuma_cena
        self.laiks_pieejams = laiks_pieejams
        self.klients_vards = klients_vards
        self.klients_uzvards = klients_uzvards
        self.klients_pk = klients_pk
        self.klients_tel_numurs = klients_tel_numurs
        self.pakalpojuma_datums = pakalpojuma_datums


@app.route('/tiksanas')
def tiksanas():
    return render_template('tiksanas.html')

@app.route('/registreties', methods=['GET', 'POST'])
def registreties():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Lūdzu, ievadiet lietotājvārdu un paroli!', 'danger')
            return render_template('registreties.html')
        conn = get_db()
        c = conn.cursor()
        try:
            c.execute('INSERT INTO klienti (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            flash('Reģistrācija veiksmīga! Tagad vari pieteikties.', 'success')
            return redirect('/pieteikties')
        except sqlite3.IntegrityError:
            flash('Lietotājvārds jau eksistē!', 'danger')
        finally:
            conn.close()
    return render_template('/registreties')

@app.route('/pieteikties', methods=['GET', 'POST'])
def pieteikties():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Lūdzu, ievadiet lietotājvārdu un paroli!', 'danger')
            return render_template('/pieteikties')
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM klienti WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = username
            flash('Pieteikšanās veiksmīga!', 'success')
            return redirect('/')
        else:
            flash('Nepareizs lietotājvārds vai parole!', 'danger')
    return render_template('/pieteikties')

@app.route('/izrakstisanas')
def izrakstisanas():
    session.pop('username', None)
    flash('Izrakstīšanās veiksmīga!', 'success')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)