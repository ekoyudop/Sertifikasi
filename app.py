#Import library berupa flask, python-dotenv, dan mongodb. Serta import datetime untuk memasukkan waktu. 
import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, jsonify
from pymongo import MongoClient
from datetime import datetime

#Menghubungkan ke environment dengan nama file ".env"
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

#Sesuaikan MongoDB 
MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)

#Route ke "/" berisikan halaman pilihan beasiswa dengan "index.html" sebagai tujuannya
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

#Route ke "/daftar" berisikan halaman daftar atau registrasi beasiswa dengan "daftar.html" sebagai tujuannya
@app.route('/daftar', methods=['GET'])
def daftar():
    return render_template('daftar.html')

#Route ke "/hasil" berisikan halaman hasil beasiswa dengan "hasil.html" sebagai tujuannya, dan database dengan tabel beasiswa untuk mengisi tabelnya
@app.route('/hasil', methods=['GET'])
def hasil():
    tabel_beasiswa_list = db.beasiswa.find()
    beasiswa_list = db.beasiswa.find()
    
    # Menghitung jumlah pilihan beasiswa
    pilihan_beasiswa = {}
    for beasiswa in beasiswa_list:
        if beasiswa['beasiswa'] in pilihan_beasiswa:
            pilihan_beasiswa[beasiswa['beasiswa']] += 1
        else:
            pilihan_beasiswa[beasiswa['beasiswa']] = 1
    
    # Mengirimkan data jumlah pilihan beasiswa ke halaman HTML
    return render_template('hasil.html', tabel_beasiswa_list=tabel_beasiswa_list ,beasiswa_list=beasiswa_list, pilihan_beasiswa=pilihan_beasiswa)

#Route "/get_ipk" untuk mengambil nilai ipk berdasarkan nama dan semester yang diinputkan di halaman daftar mahasiswa
@app.route('/get_ipk', methods=['POST'])
def get_ipk():
    nama = request.form['nama']
    semester = int(request.form['semester'])
    ipk_key = f'ipk-semester{semester}'

    #Mencari data mahasiswa berdasarkan nama, jika tidak ketemu akan error dan menampilkan nilai ipk = 0
    mahasiswa_data = db.mahasiswa.find_one({'nama': nama})
    if not mahasiswa_data:
        return jsonify({'result': 'error', 'ipk': 0})

    #Ketika data mahasiswa ketemu, maka mengambil nilai ipk dari database mahasiswa.
    ipk = mahasiswa_data[ipk_key] if ipk_key in mahasiswa_data else None
    return jsonify({'result': 'success', 'ipk': ipk})



#Route /"submit" untuk mengirimkan hasil input pada halaman daftar ke database.
@app.route("/submit", methods=["POST"])
def submit():
    #Hasil input dari halaman daftar, untuk nomorhp dan semester berupa integer, dan ipk berupa float, sedangkan berkas berupa file.
    nama = request.form["nama"]
    email = request.form["email"]
    nomorhp = int(request.form["nomorhp"])
    semester = int(request.form["semester"])
    ipk = float(request.form["ipk"])
    beasiswa = request.form["beasiswa"]
    berkas = request.files["berkas"]
    
    #mengambil nilai dari waktu sekarang menggunakan library datetime
    today = datetime.now()
    mytime = today.strftime("%Y-%m-%d-%H-%M-%S") #Format waktu berupa tahun-bulan-harui-jam-menit-detik
    
    if berkas:
        extension = berkas.filename.split('.')[-1] #mengambil format file
        filename = f'static/registrasi/beasiswa-{nama}-{mytime}.{extension}' #membuat filename berupa "beasiswa-nama-waktu.format file"
        berkas.save(filename) #menyimpan file beerdasarkan nama file baru di atas

    #memasukkan ke database beasiswa, untuk berkas ketika file tidak ada maka dikosongkan, dan untuk status diisi dengan "Belum diverifikasi"
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