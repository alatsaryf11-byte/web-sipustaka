from django.db import connection
from datetime import date

def dictfetchall(cursor):
    """Mengembalikan semua baris sebagai list of dict"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# ========== BUKU ==========
def get_all_buku():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM perpus_buku ORDER BY id")
        return dictfetchall(cursor)


def get_buku_by_id(buku_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM perpus_buku WHERE id = %s", [buku_id])
        data = dictfetchall(cursor)
        return data[0] if data else None


def create_buku(data):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO perpus_buku (judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, deskripsi)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, [data['judul'], data['pengarang'], data['kategori'], data['penerbit'],
              data['tahun_terbit'], data['rak'], data['stok'], data['deskripsi']])
        return True


def update_buku(buku_id, data):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE perpus_buku SET judul=%s, pengarang=%s, kategori=%s, penerbit=%s,
            tahun_terbit=%s, rak=%s, stok=%s, deskripsi=%s
            WHERE id=%s
        """, [data['judul'], data['pengarang'], data['kategori'], data['penerbit'],
              data['tahun_terbit'], data['rak'], data['stok'], data['deskripsi'], buku_id])
        return True


def delete_buku(buku_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM perpus_buku WHERE id = %s", [buku_id])
        return True


def cek_stok_buku(buku_id):
    """Cek stok buku, return stok"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT stok FROM perpus_buku WHERE id = %s", [buku_id])
        result = cursor.fetchone()
        return result[0] if result else 0


# ========== SISWA ==========
def get_all_siswa():
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nama, kelas, nis, is_active FROM perpus_siswa ORDER BY id")
        return dictfetchall(cursor)


def get_all_siswa_aktif():
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nama, kelas, nis FROM perpus_siswa WHERE is_active = TRUE ORDER BY nama")
        return dictfetchall(cursor)


def get_siswa_by_id(siswa_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM perpus_siswa WHERE id = %s", [siswa_id])
        data = dictfetchall(cursor)
        return data[0] if data else None


def create_siswa(data):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO perpus_siswa (nama, kelas, nis, is_active)
            VALUES (%s, %s, %s, %s)
        """, [data['nama'], data['kelas'], data['nis'], data['is_active']])
        return True


def update_siswa(siswa_id, data):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE perpus_siswa SET nama=%s, kelas=%s, nis=%s, is_active=%s
            WHERE id=%s
        """, [data['nama'], data['kelas'], data['nis'], data['is_active'], siswa_id])
        return True


def delete_siswa(siswa_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM perpus_siswa WHERE id = %s", [siswa_id])
        return True


# ========== PEMINJAMAN ==========
def update_status_terlambat():
    """Update status peminjaman menjadi Terlambat jika melewati jatuh tempo"""
    with connection.cursor() as cursor:
        today = date.today()
        cursor.execute("""
            UPDATE perpus_peminjaman 
            SET status = 'Terlambat' 
            WHERE status = 'Dipinjam' AND jatuh_tempo < %s
        """, [today])


def get_all_peminjaman():
    """Ambil semua peminjaman dengan status terlambat otomatis"""
    update_status_terlambat()
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.id, p.buku_id, s.nama as siswa_nama, b.judul as buku_judul,
                   p.tanggal_pinjam, p.jatuh_tempo, p.keperluan, p.status
            FROM perpus_peminjaman p
            JOIN perpus_siswa s ON p.siswa_id = s.id
            JOIN perpus_buku b ON p.buku_id = b.id
            ORDER BY p.id ASC
        """)
        return dictfetchall(cursor)


def get_peminjaman_by_id(peminjaman_id):
    update_status_terlambat()
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.*, s.nama as siswa_nama, b.judul as buku_judul
            FROM perpus_peminjaman p
            JOIN perpus_siswa s ON p.siswa_id = s.id
            JOIN perpus_buku b ON p.buku_id = b.id
            WHERE p.id = %s
        """, [peminjaman_id])
        data = dictfetchall(cursor)
        return data[0] if data else None


def create_peminjaman(data):
    with connection.cursor() as cursor:
        # Cek stok sebelum insert (dengan row lock untuk keamanan)
        cursor.execute("SELECT stok FROM perpus_buku WHERE id = %s", [data['buku_id']])
        stok = cursor.fetchone()[0]
        
        if stok <= 0:
            return False, "Stok buku habis, tidak bisa meminjam."
        
        cursor.execute("""
            INSERT INTO perpus_peminjaman (siswa_id, buku_id, tanggal_pinjam, jatuh_tempo, keperluan, status)
            VALUES (%s, %s, %s, %s, %s, 'Dipinjam')
        """, [data['siswa_id'], data['buku_id'], data['tanggal_pinjam'],
              data['jatuh_tempo'], data['keperluan']])
        
        # Kurangi stok
        cursor.execute("UPDATE perpus_buku SET stok = stok - 1 WHERE id = %s", [data['buku_id']])
        return True, "Buku berhasil dikembalikan."


def kembalikan_buku(peminjaman_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT status FROM perpus_peminjaman WHERE id = %s", [peminjaman_id])
        result = cursor.fetchone()
        
        if not result:
            return False, "Data peminjaman tidak ditemukan."
        
        if result[0] == 'Dikembalikan':
            return False, "Buku sudah dikembalikan sebelumnya."
        
        cursor.execute("UPDATE perpus_peminjaman SET status = 'Dikembalikan' WHERE id = %s", [peminjaman_id])
        cursor.execute("UPDATE perpus_buku SET stok = stok + 1 WHERE id = %s", [peminjaman_id])
        return True, "Buku berhasil dikembalikan."


def cek_status_peminjaman(peminjaman_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT status FROM perpus_peminjaman WHERE id = %s", [peminjaman_id])
        result = cursor.fetchone()
        return result[0] if result else None


# ========== DASHBOARD ==========
def get_dashboard_stats():
    update_status_terlambat()
    
    with connection.cursor() as cursor:
        # Total Buku (stok keseluruhan unit)
        cursor.execute("SELECT COUNT(*) FROM perpus_buku")
        total_buku = cursor.fetchone()[0]
        
        # Total Siswa Aktif
        cursor.execute("SELECT COALESCE(COUNT(*), 0) FROM perpus_siswa WHERE is_active = TRUE")
        total_siswa = cursor.fetchone()[0]
        
        # Sedang Dipinjam
        cursor.execute("SELECT COALESCE(COUNT(*), 0) FROM perpus_peminjaman WHERE status = 'Dipinjam'")
        sedang_dipinjam = cursor.fetchone()[0]
        
        # Sudah Dikembalikan
        cursor.execute("SELECT COALESCE(COUNT(*), 0) FROM perpus_peminjaman WHERE status = 'Dikembalikan'")
        sudah_dikembalikan = cursor.fetchone()[0]
        
        # Terlambat
        cursor.execute("SELECT COALESCE(COUNT(*), 0) FROM perpus_peminjaman WHERE status = 'Terlambat'")
        terlambat = cursor.fetchone()[0]
        
        return {
            'total_buku': total_buku,
            'total_siswa': total_siswa,
            'sedang_dipinjam': sedang_dipinjam,
            'sudah_dikembalikan': sudah_dikembalikan,
            'terlambat': terlambat,
        }
    
def get_stok_buku_dashboard():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT judul, stok
            FROM perpus_buku
            ORDER BY stok DESC
            LIMIT 5
        """)
        return dictfetchall(cursor)


def get_status_peminjaman_dashboard():
    update_status_terlambat()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT status, COUNT(*) as jumlah
            FROM perpus_peminjaman
            GROUP BY status
        """)

        hasil = {
            'Dipinjam': 0,
            'Dikembalikan': 0,
            'Terlambat': 0,
        }

        for row in dictfetchall(cursor):
            hasil[row['status']] = row['jumlah']

        return hasil