import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, jsonify
from pymongo import MongoClient

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', msg="Home")

@app.route('/daftar', methods=['GET'])
def daftar():
    return render_template('daftar.html', msg="Daftar")

@app.route('/hasil', methods=['GET'])
def hasil():
    return render_template('hasil.html', msg="Hasil")

@app.route("/submit", methods=["POST"])
def submit():

    nama = request.form["nama"]
    email = request.form["email"]
    nomorhp = int(request.form["nomorhp"])
    semester = int(request.form["semester"])
    # ipk = int(request.form["ipk"])
    beasiswa = request.form["beasiswa"]
    # berkas = request.files["berkas"]

    db.beasiswa.insert_one({
        "name": nama,
        "email": email,
        "nomorhp": nomorhp,
        "semester": semester,
        # "ipk": ipk,
        "beasiswa": beasiswa,
        # "berkas": berkas
    })
    
    return jsonify({"result": "success"})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)