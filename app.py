from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

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
        #registracija
        return redirect(url_for('pieteikties'))
    return render_template('registreties.html')

@app.route('/pieteikties', methods=['GET', 'POST'])
def pieteikties():
    if request.method == 'POST':
        #pietiksanas
        return redirect(url_for('home'))
    return render_template('pieteikties.html')

if __name__ == '__main__':
    app.run(debug=True)