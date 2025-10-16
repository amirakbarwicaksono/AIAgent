# ==========================================================
# Pengenalan Dataset dan DataFrame (lanjutan dari topik AI Search)
# Studi Kasus: Analisis Rute Jakarta menggunakan Pandas
# ==========================================================

import pandas as pd
from datetime import datetime

# Contoh hasil simulasi rute dari A* dan Dijkstra
hasil_simulasi = [
    {"Algoritma": "A*", "Start": "Kebon Jeruk", "Goal": "Kota Tua", 
     "Total_Jarak": 19, "Estimasi_Waktu": 30, "Kondisi": "Normal"},
    
    {"Algoritma": "Dijkstra", "Start": "Kebon Jeruk", "Goal": "Kota Tua", 
     "Total_Jarak": 19, "Estimasi_Waktu": 33, "Kondisi": "Normal"},
    
    {"Algoritma": "A*", "Start": "Kebon Jeruk", "Goal": "Kota Tua", 
     "Total_Jarak": 21, "Estimasi_Waktu": 40, "Kondisi": "Banjir di Slipi"},
    
    {"Algoritma": "Dijkstra", "Start": "Kebon Jeruk", "Goal": "Kota Tua", 
     "Total_Jarak": 21, "Estimasi_Waktu": 41, "Kondisi": "Banjir di Slipi"}
]

# Membuat DataFrame
df = pd.DataFrame(hasil_simulasi)

# Tambahkan kolom waktu eksekusi
df["Waktu_Eksekusi"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Tampilkan dataset
print("=== Dataset Simulasi Rute Jakarta ===")
print(df)

# Simpan ke file CSV
df.to_csv("dataset_rute_jakarta.csv", index=False)
print("\n Dataset disimpan ke 'dataset_rute_jakarta.csv'")

# Analisis sederhana
print("\n Rata-rata Estimasi Waktu Tempuh:")
print(df.groupby("Algoritma")["Estimasi_Waktu"].mean())

# Filter kondisi tertentu
print("\n Filter kondisi banjir:")
print(df[df["Kondisi"].str.contains("Banjir")])
