from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# 1. Fungsi membuat database dan tabel
def init_db():
    conn = sqlite3.connect('database_surat.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS surat
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  no_surat TEXT, 
                  alamat_surat TEXT, 
                  tgl_dibuat TEXT, 
                  tgl_dikirim TEXT, 
                  perihal TEXT)''')
    conn.commit()
    conn.close()

# 2. Fungsi generate nomor surat otomatis
def generate_no_surat():
    conn = sqlite3.connect('database_surat.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM surat")
    total = c.fetchone()[0] + 1
    conn.close()
    
    bulan_romawi = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
    sekarang = datetime.now()
    bulan = bulan_romawi[sekarang.month - 1]
    tahun = sekarang.year
    
    # Format: 001/HMPS-PAI/01/A-0/XI/2026
    return f"{total:03d}/HMPS-PAI/01/A-0/{bulan}/{tahun}"

# 3. Halaman Utama
@app.route('/')
def index():
    conn = sqlite3.connect('database_surat.db')
    c = conn.cursor()
    c.execute("SELECT * FROM surat ORDER BY id DESC")
    data_surat = c.fetchall()
    conn.close()
    
    no_otomatis = generate_no_surat() 
    return render_template('index.html', surat=data_surat, no_otomatis=no_otomatis)

# 4. Proses Simpan Data
@app.route('/tambah', methods=['POST'])
def tambah():
    alamat = request.form['alamat_surat']
    tgl_dibuat = request.form['tgl_dibuat']
    tgl_dikirim = request.form['tgl_dikirim']
    perihal = request.form['perihal']
    
    # Cek apakah user mengedit nomor surat di kotak kuning
    no_surat_input = request.form.get('no_surat', '').strip()
    
    if no_surat_input:
        no_surat = no_surat_input 
    else:
        no_surat = generate_no_surat()

    conn = sqlite3.connect('database_surat.db')
    c = conn.cursor()
    c.execute("INSERT INTO surat (no_surat, alamat_surat, tgl_dibuat, tgl_dikirim, perihal) VALUES (?, ?, ?, ?, ?)",
              (no_surat, alamat, tgl_dibuat, tgl_dikirim, perihal))
    conn.commit()
    conn.close()
    
    return redirect('/')

# 5. Proses Hapus Satu Data
@app.route('/hapus/<int:id>')
def hapus(id):
    conn = sqlite3.connect('database_surat.db')
    c = conn.cursor()
    c.execute("DELETE FROM surat WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

# 6. Proses Kosongkan Seluruh Tabel
@app.route('/hapus_semua')
def hapus_semua():
    conn = sqlite3.connect('database_surat.db')
    c = conn.cursor()
    c.execute("DELETE FROM surat")
    # Mereset nomor urut ID kembali ke 1
    c.execute("DELETE FROM sqlite_sequence WHERE name='surat'") 
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)