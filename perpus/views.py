from django.shortcuts import render, redirect
from django.contrib import messages
from . import db_utils


# ========== DASHBOARD ==========
def dashboard(request):
    stats = db_utils.get_dashboard_stats()

    context = {
        'stats': stats,
        'stok_buku': db_utils.get_stok_buku_dashboard(),
        'status_map': db_utils.get_status_peminjaman_dashboard(),
    }

    return render(request, 'perpus/dashboard.html', context)


# ========== BUKU CRUD ==========
def buku_list(request):
    buku_list = db_utils.get_all_buku()
    return render(request, 'perpus/buku_list.html', {'buku_list': buku_list})


def buku_create(request):
    if request.method == 'POST':
        # Validasi
        judul = request.POST.get('judul', '').strip()
        pengarang = request.POST.get('pengarang', '').strip()
        penerbit = request.POST.get('penerbit', '').strip()
        tahun_terbit = request.POST.get('tahun_terbit', '')
        stok = request.POST.get('stok', '')
        
        if not judul:
            messages.error(request, 'Judul buku wajib diisi.')
            return redirect('buku_create')
        if not pengarang:
            messages.error(request, 'Pengarang wajib diisi.')
            return redirect('buku_create')
        if not penerbit:
            messages.error(request, 'Penerbit wajib diisi.')
            return redirect('buku_create')
        
        try:
            tahun_terbit = int(tahun_terbit)
        except (ValueError, TypeError):
            messages.error(request, 'Tahun terbit harus berupa angka.')
            return redirect('buku_create')
        
        try:
            stok = int(stok)
            if stok < 0:
                messages.error(request, 'Stok tidak boleh negatif.')
                return redirect('buku_create')
        except (ValueError, TypeError):
            messages.error(request, 'Stok harus berupa angka.')
            return redirect('buku_create')
        
        data = {
            'judul': judul,
            'pengarang': pengarang,
            'kategori': request.POST.get('kategori'),
            'penerbit': penerbit,
            'tahun_terbit': tahun_terbit,
            'rak': request.POST.get('rak'),
            'stok': stok,
            'deskripsi': request.POST.get('deskripsi', ''),
        }
        db_utils.create_buku(data)
        messages.success(request, 'Buku berhasil ditambahkan.')
        return redirect('buku_list')
    
    categories = ['Novel', 'Sejarah', 'Pendidikan']
    rak_list = ['Rak A-01', 'Rak A-02', 'Rak A-03', 'Rak A-04', 'Rak A-05']
    return render(request, 'perpus/buku_form.html', {
        'title': 'Tambah Buku',
        'categories': categories,
        'rak_list': rak_list,
    })


def buku_detail(request, buku_id):
    buku = db_utils.get_buku_by_id(buku_id)
    if not buku:
        messages.error(request, 'Buku tidak ditemukan.')
        return redirect('buku_list')
    return render(request, 'perpus/buku_detail.html', {'buku': buku})


def buku_edit(request, buku_id):
    buku = db_utils.get_buku_by_id(buku_id)
    if not buku:
        messages.error(request, 'Buku tidak ditemukan.')
        return redirect('buku_list')
    
    if request.method == 'POST':
        # Validasi
        judul = request.POST.get('judul', '').strip()
        pengarang = request.POST.get('pengarang', '').strip()
        penerbit = request.POST.get('penerbit', '').strip()
        tahun_terbit = request.POST.get('tahun_terbit', '')
        stok = request.POST.get('stok', '')
        
        if not judul:
            messages.error(request, 'Judul buku wajib diisi.')
            return redirect('buku_edit', buku_id=buku_id)
        if not pengarang:
            messages.error(request, 'Pengarang wajib diisi.')
            return redirect('buku_edit', buku_id=buku_id)
        if not penerbit:
            messages.error(request, 'Penerbit wajib diisi.')
            return redirect('buku_edit', buku_id=buku_id)
        
        try:
            tahun_terbit = int(tahun_terbit)
        except (ValueError, TypeError):
            messages.error(request, 'Tahun terbit harus berupa angka.')
            return redirect('buku_edit', buku_id=buku_id)
        
        try:
            stok = int(stok)
            if stok < 0:
                messages.error(request, 'Stok tidak boleh negatif.')
                return redirect('buku_edit', buku_id=buku_id)
        except (ValueError, TypeError):
            messages.error(request, 'Stok harus berupa angka.')
            return redirect('buku_edit', buku_id=buku_id)
        
        data = {
            'judul': judul,
            'pengarang': pengarang,
            'kategori': request.POST.get('kategori'),
            'penerbit': penerbit,
            'tahun_terbit': tahun_terbit,
            'rak': request.POST.get('rak'),
            'stok': stok,
            'deskripsi': request.POST.get('deskripsi', ''),
        }
        db_utils.update_buku(buku_id, data)
        messages.success(request, 'Buku berhasil diperbarui.')
        return redirect('buku_detail', buku_id=buku_id)
    
    categories = ['Novel', 'Sejarah', 'Pendidikan']
    rak_list = ['Rak A-01', 'Rak A-02', 'Rak A-03', 'Rak A-04', 'Rak A-05']
    return render(request, 'perpus/buku_form.html', {
        'title': 'Edit Buku',
        'buku': buku,
        'categories': categories,
        'rak_list': rak_list,
    })


def buku_delete(request, buku_id):
    buku = db_utils.get_buku_by_id(buku_id)
    if not buku:
        messages.error(request, 'Buku tidak ditemukan.')
        return redirect('buku_list')
    
    if request.method == 'POST':
        db_utils.delete_buku(buku_id)
        messages.success(request, 'Buku berhasil dihapus.')
        return redirect('buku_list')
    
    return render(request, 'perpus/buku_confirm_delete.html', {'buku': buku})


# ========== SISWA CRUD ==========
def user_list(request):
    siswa_list = db_utils.get_all_siswa()
    return render(request, 'perpus/user_list.html', {'siswa_list': siswa_list})


def user_create(request):
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        kelas = request.POST.get('kelas', '').strip()
        nis = request.POST.get('nis', '').strip()
        
        if not nama:
            messages.error(request, 'Nama wajib diisi.')
            return redirect('user_create')
        if not kelas:
            messages.error(request, 'Kelas wajib diisi.')
            return redirect('user_create')
        if not nis:
            messages.error(request, 'NIS wajib diisi.')
            return redirect('user_create')
        
        data = {
            'nama': nama,
            'kelas': kelas,
            'nis': nis,
            'is_active': request.POST.get('is_active') == 'on',
        }
        
        try:
            db_utils.create_siswa(data)
            messages.success(request, 'User berhasil ditambahkan.')
            return redirect('user_list')
        except Exception as e:
            if 'unique constraint' in str(e).lower() or 'duplicate' in str(e).lower():
                messages.error(request, 'NIS sudah terdaftar.')
            else:
                messages.error(request, f'Gagal menambahkan user: {str(e)}')
            return redirect('user_create')
    
    return render(request, 'perpus/user_form.html', {'title': 'Tambah User'})


def user_detail(request, user_id):
    siswa = db_utils.get_siswa_by_id(user_id)
    if not siswa:
        messages.error(request, 'User tidak ditemukan.')
        return redirect('user_list')
    return render(request, 'perpus/user_detail.html', {'siswa': siswa})


def user_edit(request, user_id):
    siswa = db_utils.get_siswa_by_id(user_id)
    if not siswa:
        messages.error(request, 'User tidak ditemukan.')
        return redirect('user_list')
    
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        kelas = request.POST.get('kelas', '').strip()
        nis = request.POST.get('nis', '').strip()
        
        if not nama:
            messages.error(request, 'Nama wajib diisi.')
            return redirect('user_edit', user_id=user_id)
        if not kelas:
            messages.error(request, 'Kelas wajib diisi.')
            return redirect('user_edit', user_id=user_id)
        if not nis:
            messages.error(request, 'NIS wajib diisi.')
            return redirect('user_edit', user_id=user_id)
        
        data = {
            'nama': nama,
            'kelas': kelas,
            'nis': nis,
            'is_active': request.POST.get('is_active') == 'on',
        }
        
        try:
            db_utils.update_siswa(user_id, data)
            messages.success(request, 'User berhasil diperbarui.')
            return redirect('user_detail', user_id=user_id)
        except Exception as e:
            if 'unique constraint' in str(e).lower() or 'duplicate' in str(e).lower():
                messages.error(request, 'NIS sudah terdaftar.')
            else:
                messages.error(request, f'Gagal memperbarui user: {str(e)}')
            return redirect('user_edit', user_id=user_id)
    
    return render(request, 'perpus/user_form.html', {
        'title': 'Edit User',
        'siswa': siswa,
    })


def user_delete(request, user_id):
    siswa = db_utils.get_siswa_by_id(user_id)
    if not siswa:
        messages.error(request, 'User tidak ditemukan.')
        return redirect('user_list')
    
    if request.method == 'POST':
        db_utils.delete_siswa(user_id)
        messages.success(request, 'User berhasil dihapus.')
        return redirect('user_list')
    
    return render(request, 'perpus/user_confirm_delete.html', {'siswa': siswa})


# ========== PEMINJAMAN CRUD ==========
def peminjaman_list(request):
    peminjaman_list = db_utils.get_all_peminjaman()
    return render(request, 'perpus/peminjaman_list.html', {'peminjaman_list': peminjaman_list})


def peminjaman_create(request):
    if request.method == 'POST':
        siswa_id = request.POST.get('siswa_id')
        buku_id = request.POST.get('buku_id')
        tanggal_pinjam = request.POST.get('tanggal_pinjam')
        jatuh_tempo = request.POST.get('jatuh_tempo')
        keperluan = request.POST.get('keperluan', '')
        
        # Validasi
        if not siswa_id:
            messages.error(request, 'Siswa wajib dipilih.')
            return redirect('peminjaman_create')
        if not buku_id:
            messages.error(request, 'Buku wajib dipilih.')
            return redirect('peminjaman_create')
        if not tanggal_pinjam:
            messages.error(request, 'Tanggal pinjam wajib diisi.')
            return redirect('peminjaman_create')
        if not jatuh_tempo:
            messages.error(request, 'Jatuh tempo wajib diisi.')
            return redirect('peminjaman_create')
        
        # Cek stok
        stok = db_utils.cek_stok_buku(buku_id)
        if stok <= 0:
            messages.error(request, 'Stok buku habis, tidak bisa meminjam.')
            return redirect('peminjaman_create')
        
        data = {
            'siswa_id': siswa_id,
            'buku_id': buku_id,
            'tanggal_pinjam': tanggal_pinjam,
            'jatuh_tempo': jatuh_tempo,
            'keperluan': keperluan,
        }
        
        success, message = db_utils.create_peminjaman(data)
        if success:
            messages.success(request, message)
            return redirect('peminjaman_list')
        else:
            messages.error(request, message)
            return redirect('peminjaman_create')
    
    siswa_list = db_utils.get_all_siswa_aktif()
    buku_list = db_utils.get_all_buku()
    return render(request, 'perpus/peminjaman_form.html', {
        'siswa_list': siswa_list,
        'buku_list': buku_list,
    })


def peminjaman_kembalikan(request, peminjaman_id):
    success, message = db_utils.kembalikan_buku(peminjaman_id,)
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    return redirect('peminjaman_list')