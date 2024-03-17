import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, jsonify
from pymongo import MongoClient
import jwt
import datetime
import hashlib
from bson import ObjectId
from datetime import datetime


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/daftar', methods=['GET'])
def daftar():
    return render_template('daftar.html')

@app.route('/hasil', methods=['GET'])
def hasil():
    beasiswa_list = db.beasiswa.find()
    return render_template('hasil.html', beasiswa_list=beasiswa_list)

@app.route('/get_ipk', methods=['POST'])
def get_ipk():
    nama = request.form['nama']
    semester = int(request.form['semester'])
    ipk_key = f'ipk-semester{semester}'

    mahasiswa_data = db.mahasiswa.find_one({'nama': nama})
    if not mahasiswa_data:
        return jsonify({'result': 'error', 'ipk': 0})

    ipk = mahasiswa_data[ipk_key] if ipk_key in mahasiswa_data else None
    return jsonify({'result': 'success', 'ipk': ipk})

@app.route("/submit", methods=["POST"])
def submit():
    
    nama = request.form["nama"]
    email = request.form["email"]
    nomorhp = int(request.form["nomorhp"])
    semester = int(request.form["semester"])
    ipk = int(request.form["ipk"])
    beasiswa = request.form["beasiswa"]
    berkas = request.files["berkas"]

    today = datetime.now()
    mytime = today.strftime("%Y-%m-%d-%H-%M-%S")
    
    if berkas:
        extension = berkas.filename.split('.')[-1]
        filename = f'static/submit-{mytime}.{extension}'
        berkas.save(filename)

    db.beasiswa.insert_one({
        "nama": nama,
        "email": email,
        "nomorhp": nomorhp,
        "semester": semester,
        "ipk": ipk,
        "beasiswa": beasiswa,
        "berkas": filename if berkas else None,
        "status": "Belum diverifikasi"
    })
    
    return jsonify({"result": "success"})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)