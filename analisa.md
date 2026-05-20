kita akan membuat analisa bank data perikanan (contoh format data pada file BANK DATA PERIKANAN TANGKAP (Jawaban).xlsx ) yang nanti akan kita pindahkan datanya ke file "template data input.xlsx"
jadi kita memilikibeberapa kolom, dan yang saya mau fokuskan adalah pada kolom alat tangkap utama dan alat tangkap tambahan
Alat Tangkap Utama:
ID Alat Tangkap: 
1. Bagan Perahu
2. Sero
3. Jaring Insang Tetap
4. Pancing Ulur
5. Pukat Ikan/Pukat Hela Pertengahan Berpapan
6. Rawai Dasar
7. Pukat Cincin Pelagis Besar Dengan Satu Kapal
8. Penggaruk Tanpa Kapal
9. Jala Tebar
10. Bubu
11. Yang Lain

Untuk alat tangkap yang tidak ada pada "Alat Tangkap Utama", masukan ke "Alat Tangkap Tambahan".. jadi nanti dia akan masuk ke kolom ALAT TANGKAP TAMBAHAN

kita asumsikan
- A = file "BANK DATA PERIKANAN TANGKAP (Jawaban).xlsx"
- B = file "template data input.xlsx"

saya jelaskan ya cara membaca file BANK DATA PERIKANAN TANGKAP untuk kolom ALAT TANGKAP UTAMA.
misalnya :
- pada file A, kolom ALAT TANGKAP UTAMA, tertulis "BAGAN PERAHU", nanti datanya kita pindahkan ke file B pada kolom "ALAT TANGKAP UTAMA"
- karena "BAGAN PERAHU" ID=1 maka untuk mengisi kolom "JENIS TANGKAPAN" pada file B, kita baca di kolom "JENIS TANGKAPAN" pada file A
- kolom "BERAT PER-JENIS TANGKAPAN DALAM 1 KALI TRIP (KG)" pada file B, kita baca di kolom "BERAT PER-JENIS TANGKAPAN DALAM 1 KALI TRIP (KG)" pada file A
- kolom "HARGA PER-JENIS TANGKAPAN /kg (Rp.)" pada file B, kita baca di kolom "HARGA PER-JENIS TANGKAPAN /kg (Rp.)" pada file A

KHUSUS UNTUK ID >1 begini cara bacanya
- pada file A kolom "ALAT TANGKAP UTAMA" tertulis "BUBU", nanti data dipindahkan untuk kolom "ALAT TANGKAP UTAMA" pada file B
- karena "BUBU" ID=10 maka untuk mengisi kolom "JENIS TANGKAPAN" pada file B, kita baca pada row tersebut, dan cari row setelahnya yang berisi data. ketika ketemu data, maka lihat kolomnya dan baca. jika mengandung kata kunci "JENIS TANGKAPAN" maka masukkan nilainya ke kolom "JENIS TANGKAPAN" pada file B. kemudian baca lagi data setelahnya pada kolom yang sama, jika mengandung kata kunci "BERAT PER-JENIS TANGKAPAN DALAM 1 KALI TRIP (KG)" maka masukkan nilainya ke kolom "BERAT PER-JENIS TANGKAPAN DALAM 1 KALI TRIP (KG)" pada file B. kemudian baca lagi data setelahnya pada kolom yang sama, jika mengandung kata kunci "HARGA PER-JENIS TANGKAPAN /kg (Rp.)" maka masukkan nilainya ke kolom "HARGA PER-JENIS TANGKAPAN /kg (Rp.)" pada file B.

setelah 3 kolom tadi bisa di isi ("ALAT TANGKAP UTAMA", "JENIS TANGKAPAN", "BERAT PER-JENIS TANGKAPAN DALAM 1 KALI TRIP (KG)", "HARGA PER-JENIS TANGKAPAN /kg (Rp.)") maka lanjut ke pembacaaan "ALAT TANGKAP TAMBAHAN"

saya jelaskan ya cara membaca file BANK DATA PERIKANAN TANGKAP untuk kolom ALAT TANGKAP TAMBAHAN.
misalnya:
-  pada file A kolom ALAT TANGKAP TAMBAHAN tertulis apapun itu, maka data tersebut dimasukan ke kolom "ALAT TANGKAP TAMBAHAN" PADA FILE b
- untuk mengisi kolom "JENIS TANGKAPAN 2" pada file B diambil data pada kolom "JENIS TANGKAPAN 12"
- untuk mengisi kolom "BERAT PER-JENIS TANGKAPAN DALAM 1 KALI TRIP (KG) 2" pada file B diambil data pada kolom "BERAT PER-JENIS TANGKAPAN DALAM 1 KALI TRIP (KG) 12"
- untuk mengisi kolom "HARGA PER-JENIS TANGKAPAN /kg (Rp.) 2" pada file B diambil data pada kolom "HARGA PER-JENIS TANGKAPAN /kg (Rp.) 12"


Kolom "Tuliskan Nama Lengkap Anda" pada file A masukkan ke kolom "NAMA PETUGAS" pada file B
pada ROW dengan Kolom DESA 1,2,3,4 dan seterusnya, yang ada isinya pada file A masukkan ke kolom "DESA" pada file B

pada ROW dengan kolom JENIS KAPAL Catatan: KM_0005 : Daya Mesin 16 PK - 28 PK KM_0005-0010 : Daya Mesin 30 PK-40 PK  MT_0005 : Daya Mesin dibawah (<10 PK) PTM : Perahu Tanpa Motor pada file A  masukkan ke kolom "JENIS KAPAL" pada file B

pada ROW dengan kolom UKURAN DAYA MESIN (PK) Contoh: 24 pada file A masukkan ke kolom "UKURAN DAYA MESIN (PK)" pada file B

pada ROW dengan kolom UKURAN PANJANG KAPAL (METER) contoh: 9 pada file A masukkan ke kolom UKURAN PANJANG KAPAL (METER) pada file B


pada ROW dengan kolom UKURAN LEBAR KAPAL (METER) Contoh: 5 pada file A masukkan ke kolom UKURAN LEBAR KAPAL (METER) pada file B
