from flask import Flask, render_template, redirect, url_for, request, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = '12345'

DATABASE = 'klienti.db'
ADMIN_USERNAME = "admin"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(force=False):
    if force or not os.path.exists(DATABASE):
        if os.path.exists(DATABASE) and force:
            os.remove(DATABASE)
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            CREATE TABLE klienti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                vards TEXT,
                uzvards TEXT,
                pk TEXT,
                tel_numurs TEXT,
                email TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE pakalpojumi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kategorija TEXT NOT NULL,
                nosaukums TEXT NOT NULL,
                cena REAL NOT NULL,
                atlaide REAL DEFAULT 0
            )
        ''')
        c.execute('''
            CREATE TABLE appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                klienta_id INTEGER NOT NULL,
                pakalpojuma_id INTEGER NOT NULL,
                datums TEXT NOT NULL,
                sakuma_laiks TEXT NOT NULL,
                beigu_laiks TEXT NOT NULL,
                FOREIGN KEY(klienta_id) REFERENCES klienti(id),
                FOREIGN KEY(pakalpojuma_id) REFERENCES pakalpojumi(id)
            )
        ''')
        conn.commit()
        conn.close()

try:
    init_db()
except Exception as e:
    print("DB init error:", e)

class Skaistumkopsana:
    def __init__(self, pakalpojuma_kategorija=None, pakalpojuma_nosaukums=None, pakalpojuma_atlaide=0, pakalpojuma_cena=0, laiks_pieejams=True, klients_vards=None, klients_uzvards=None, klients_pk=None, klients_tel_numurs=None, pakalpojuma_datums=None, pakalpojuma_sakuma_laiks=None, pakalpojuma_beigu_laiks=None):
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
        self.pakalpojuma_sakuma_laiks = pakalpojuma_sakuma_laiks
        self.pakalpojuma_beigu_laiks = pakalpojuma_beigu_laiks

    @classmethod
    def no_param(cls):
        return cls(laiks_pieejams=True)

    @classmethod
    def ar_parametriem(cls, pak_kategorija, pak_nosaukums, atlaide, cena, sakuma_laiks=None, beigu_laiks=None):
        return cls(
            pakalpojuma_kategorija=pak_kategorija,
            pakalpojuma_nosaukums=pak_nosaukums,
            pakalpojuma_atlaide=atlaide,
            pakalpojuma_cena=cena,
            laiks_pieejams=True,
            pakalpojuma_sakuma_laiks=sakuma_laiks,
            pakalpojuma_beigu_laiks=beigu_laiks
        )

    def pakalpojuma_ilgums(self):
        from datetime import datetime
        if self.pakalpojuma_sakuma_laiks and self.pakalpojuma_beigu_laiks:
            fmt = "%H:%M"
            start = datetime.strptime(self.pakalpojuma_sakuma_laiks, fmt)
            end = datetime.strptime(self.pakalpojuma_beigu_laiks, fmt)
            return int((end - start).total_seconds() // 60)
        return None

    def cena_kopa(self):
        if self.pakalpojuma_atlaide and self.pakalpojuma_cena:
            try:
                atlaide = float(str(self.pakalpojuma_atlaide).replace('%',''))
            except:
                atlaide = 0
            return round(float(self.pakalpojuma_cena) * (1 - atlaide/100), 2)
        return self.pakalpojuma_cena

    def pakalpojuma_info(self):
        return f"{self.pakalpojuma_kategorija} - {self.pakalpojuma_nosaukums}, Cena: {self.pakalpojuma_cena}, Atlaide: {self.pakalpojuma_atlaide}, Pieejams: {self.laiks_pieejams}, Ilgums: {self.pakalpojuma_ilgums()} min"

    def pakalpojuma_info_print(self, filename="pakalpojums.txt"):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.pakalpojuma_info())

    def klients_info(self):
        return f"{self.klients_vards} {self.klients_uzvards}, PK: {self.klients_pk}, Tel: {self.klients_tel_numurs}"

    def klients_info_print(self, filename="klients.txt"):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.klients_info())

def is_profile_complete(user_row):
    return all([user_row['vards'], user_row['uzvards'], user_row['pk'], user_row['tel_numurs']])

@app.route('/')
def home():
    return render_template('home.html', is_admin=(session.get('username') == ADMIN_USERNAME))

@app.route('/pakalpojumi', methods=['GET', 'POST'])
def pakalpojumi():
    conn = get_db()
    c = conn.cursor()
    if request.method == 'POST' and session.get('username') == ADMIN_USERNAME:
        kategorija = request.form['kategorija']
        nosaukums = request.form['nosaukums']
        cena = request.form['cena']
        atlaide = request.form.get('atlaide', 0)
        if kategorija and nosaukums and cena:
            c.execute('INSERT INTO pakalpojumi (kategorija, nosaukums, cena, atlaide) VALUES (?, ?, ?, ?)', (kategorija, nosaukums, cena, atlaide))
            conn.commit()
            flash('Pakalpojums pievienots!', 'success')
    c.execute('SELECT * FROM pakalpojumi')
    pakalpojumi = c.fetchall()
    conn.close()
    return render_template('pakalpojumi.html', pakalpojumi=pakalpojumi, is_admin=(session.get('username') == ADMIN_USERNAME))

@app.route('/klienti')
def klienti():
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute('SELECT vards, uzvards, pk, tel_numurs, email, username FROM klienti')
        klienti = c.fetchall()
    except Exception as e:
        klienti = []
        flash('Kļūda datubāzē: ' + str(e), 'danger')
    conn.close()
    return render_template('klienti.html', klienti=klienti, is_admin=(session.get('username') == ADMIN_USERNAME))

@app.route('/tiksanas')
def tiksanas():
    if 'username' not in session:
        return redirect(url_for('pieteikties'))
    conn = get_db()
    c = conn.cursor()
    is_admin = (session.get('username') == ADMIN_USERNAME)
    if is_admin:
        c.execute('''
            SELECT a.*, p.kategorija, p.nosaukums, p.cena, p.atlaide,
                   k.vards AS klienta_vards, k.uzvards AS klienta_uzvards, k.username AS klienta_username
            FROM appointments a
            JOIN pakalpojumi p ON a.pakalpojuma_id = p.id
            JOIN klienti k ON a.klienta_id = k.id
            ORDER BY a.datums DESC, a.sakuma_laiks DESC
        ''')
        appointments = c.fetchall()
    else:
        c.execute('SELECT * FROM klienti WHERE username=?', (session['username'],))
        user = c.fetchone()
        if not user:
            flash('Lietotājs nav atrasts!', 'danger')
            return redirect(url_for('home'))
        c.execute('''
            SELECT a.*, p.kategorija, p.nosaukums, p.cena, p.atlaide
            FROM appointments a
            JOIN pakalpojumi p ON a.pakalpojuma_id = p.id
            WHERE a.klienta_id=?
            ORDER BY a.datums DESC, a.sakuma_laiks DESC
        ''', (user['id'],))
        appointments = c.fetchall()
    # Calculate discounted price for each appointment
    appointments_list = []
    for pak in appointments:
        cena = pak['cena']
        atlaide = pak['atlaide'] if 'atlaide' in pak.keys() and pak['atlaide'] is not None else 0
        try:
            atlaide_val = float(str(atlaide).replace('%',''))
        except:
            atlaide_val = 0
        cena_kopa = round(float(cena) * (1 - atlaide_val/100), 2)
        pak_dict = dict(pak)
        pak_dict['cena_kopa'] = cena_kopa
        appointments_list.append(pak_dict)
    conn.close()
    return render_template('tiksanas.html', appointments=appointments_list, is_admin=is_admin)

@app.route('/rezervet/<int:pak_id>', methods=['GET', 'POST'])
def rezervet_appointment(pak_id):
    if 'username' not in session:
        return redirect(url_for('pieteikties'))
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM klienti WHERE username=?', (session['username'],))
    user = c.fetchone()
    if not user:
        flash('Lietotājs nav atrasts!', 'danger')
        return redirect(url_for('home'))
    if not is_profile_complete(user):
        flash('Lūdzu, aizpildiet savu profilu pirms rezervācijas!', 'danger')
        return redirect(url_for('profils'))
    c.execute('SELECT * FROM pakalpojumi WHERE id=?', (pak_id,))
    pak = c.fetchone()
    if not pak:
        flash('Pakalpojums nav atrasts!', 'danger')
        return redirect(url_for('pakalpojumi'))
    # Calculate discounted price
    cena = pak['cena']
    atlaide = pak['atlaide'] if 'atlaide' in pak.keys() and pak['atlaide'] is not None else 0
    try:
        atlaide_val = float(str(atlaide).replace('%',''))
    except:
        atlaide_val = 0
    cena_kopa = round(float(cena) * (1 - atlaide_val/100), 2)
    if request.method == 'POST':
        datums = request.form['datums']
        sakuma_laiks = request.form['sakuma_laiks']
        beigu_laiks = request.form['beigu_laiks']
        c.execute('INSERT INTO appointments (klienta_id, pakalpojuma_id, datums, sakuma_laiks, beigu_laiks) VALUES (?, ?, ?, ?, ?)',
                  (user['id'], pak_id, datums, sakuma_laiks, beigu_laiks))
        conn.commit()
        flash('Tikšanās pievienota!', 'success')
        return redirect(url_for('tiksanas'))
    conn.close()
    return render_template('rezervet.html', pak=pak, cena_kopa=cena_kopa, is_admin=(session.get('username') == ADMIN_USERNAME))

@app.route('/registreties', methods=['GET', 'POST'])
def registreties():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        vards = request.form.get('vards')
        uzvards = request.form.get('uzvards')
        pk = request.form.get('pk')
        tel_numurs = request.form.get('tel_numurs')
        email = request.form.get('email')
        if not username or not password or not email:
            flash('Lūdzu, ievadiet lietotājvārdu, paroli un e-pastu!', 'danger')
            return render_template('registreties.html')
        try:
            conn = get_db()
            c = conn.cursor()
            c.execute('INSERT INTO klienti (username, password, vards, uzvards, pk, tel_numurs, email) VALUES (?, ?, ?, ?, ?, ?, ?)', (username, password, vards, uzvards, pk, tel_numurs, email))
            conn.commit()
            flash('Reģistrācija veiksmīga! Tagad vari pieteikties.', 'success')
            return redirect(url_for('pieteikties'))
        except sqlite3.IntegrityError:
            flash('Lietotājvārds jau eksistē!', 'danger')
        except Exception as e:
            flash(f'Kļūda: {e}', 'danger')
        finally:
            try:
                conn.close()
            except:
                pass
    return render_template('registreties.html')

@app.route('/pieteikties', methods=['GET', 'POST'])
def pieteikties():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Lūdzu, ievadiet lietotājvārdu un paroli!', 'danger')
            return render_template('pieteikties.html')
        try:
            conn = get_db()
            c = conn.cursor()
            c.execute('SELECT * FROM klienti WHERE username=? AND password=?', (username, password))
            user = c.fetchone()
            conn.close()
            if user:
                session['username'] = username
                flash('Pieteikšanās veiksmīga!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Nepareizs lietotājvārds vai parole!', 'danger')
        except Exception as e:
            flash(f'Kļūda: {e}', 'danger')
    return render_template('pieteikties.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Izrakstīšanās veiksmīga!', 'success')
    return redirect(url_for('home'))

@app.route('/profils', methods=['GET', 'POST'])
def profils():
    if 'username' not in session:
        return redirect(url_for('pieteikties'))
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM klienti WHERE username=?', (session['username'],))
    user = c.fetchone()
    if not user:
        flash('Lietotājs nav atrasts!', 'danger')
        return redirect(url_for('home'))
    if request.method == 'POST':
        vards = request.form['vards']
        uzvards = request.form['uzvards']
        pk = request.form['pk']
        tel_numurs = request.form['tel_numurs']
        email = request.form['email']
        c.execute('UPDATE klienti SET vards=?, uzvards=?, pk=?, tel_numurs=?, email=? WHERE username=?',
                  (vards, uzvards, pk, tel_numurs, email, session['username']))
        conn.commit()
        flash('Profils atjaunots!', 'success')
        return redirect(url_for('pakalpojumi'))
    conn.close()
    return render_template('profils.html', user=user, is_admin=(session.get('username') == ADMIN_USERNAME))

@app.context_processor
def inject_user():
    return dict(logged_in=('username' in session), username=session.get('username'))

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'initdb':
        print("Initializing database...")
        init_db(force=True)
        print("Database initialized.")
    else:
        app.run(debug=True)