from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Buku
    path('buku/', views.buku_list, name='buku_list'),
    path('buku/tambah/', views.buku_create, name='buku_create'),
    path('buku/<int:buku_id>/', views.buku_detail, name='buku_detail'),
    path('buku/<int:buku_id>/edit/', views.buku_edit, name='buku_edit'),
    path('buku/<int:buku_id>/hapus/', views.buku_delete, name='buku_delete'),
    
    # User/Siswa
    path('user/', views.user_list, name='user_list'),
    path('user/tambah/', views.user_create, name='user_create'),
    path('user/<int:user_id>/', views.user_detail, name='user_detail'),
    path('user/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('user/<int:user_id>/hapus/', views.user_delete, name='user_delete'),
    
    # Peminjaman
    path('peminjaman/', views.peminjaman_list, name='peminjaman_list'),
    path('peminjaman/tambah/', views.peminjaman_create, name='peminjaman_create'),
    path('peminjaman/<int:peminjaman_id>/kembalikan/', views.peminjaman_kembalikan, name='peminjaman_kembalikan'),
]