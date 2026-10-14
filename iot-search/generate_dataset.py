"""
Generator dataset 1.000 dokumen bertema Internet of Things (IoT) berbahasa Indonesia.

Dokumen disusun dari kombinasi topik, perangkat, protokol, aplikasi, dan kalimat
penjelas sehingga setiap dokumen memiliki kosakata yang bervariasi. Dataset bersifat
sintetis (dibuat untuk keperluan praktikum / demo Sistem Temu Kembali Informasi).

Jalankan:  python generate_dataset.py
Keluaran:  data/dokumen_iot.json
"""
import json
import random

random.seed(2026)
JUMLAH_DOKUMEN = 1000

# ---------------------------------------------------------------------------
# Kategori -> daftar topik. Setiap topik: (nama topik, [kalimat definisi/penjelasan])
# ---------------------------------------------------------------------------
KATEGORI = {
    "Smart Home": {
        "topik": [
            "lampu pintar", "kunci pintu digital", "termostat pintar", "kamera pengawas rumah",
            "stopkontak pintar", "sensor kebocoran gas", "tirai otomatis", "pendeteksi asap",
            "asisten suara rumah", "sistem irigasi taman otomatis",
        ],
        "kalimat": [
            "{t} memungkinkan pemilik rumah mengontrol perangkat dari jarak jauh melalui aplikasi ponsel.",
            "Penggunaan {t} membantu menghemat energi listrik karena perangkat menyala hanya saat dibutuhkan.",
            "Sistem {t} terhubung ke jaringan WiFi rumah dan mengirim data status ke server cloud.",
            "Integrasi {t} dengan asisten suara memudahkan pengguna memberi perintah tanpa menyentuh perangkat.",
            "Keamanan {t} bergantung pada enkripsi komunikasi dan pembaruan firmware secara berkala.",
            "Mikrokontroler ESP32 sering dipakai untuk membangun prototipe {t} dengan biaya rendah.",
            "Pengguna dapat membuat jadwal otomatis pada {t} sesuai kebiasaan harian keluarga.",
            "Notifikasi realtime dari {t} diterima pemilik rumah ketika terjadi kondisi tidak normal.",
        ],
    },
    "Pertanian Cerdas": {
        "topik": [
            "pemantauan kelembaban tanah", "irigasi tetes otomatis", "greenhouse pintar",
            "pemantauan suhu kandang ayam", "pemberian pakan ikan otomatis", "pemantauan pH air tambak",
            "deteksi hama tanaman", "drone pemantau lahan", "prediksi panen berbasis data sensor",
            "pemantauan nutrisi hidroponik",
        ],
        "kalimat": [
            "Petani memanfaatkan {t} untuk meningkatkan hasil panen dan menekan biaya operasional.",
            "Sensor lapangan pada {t} mengirim data melalui jaringan LoRa ke gateway terdekat.",
            "Dengan {t}, penyiraman dilakukan berdasarkan data kelembaban sehingga air tidak terbuang.",
            "Dashboard {t} menampilkan grafik suhu, kelembaban, dan intensitas cahaya secara realtime.",
            "Penerapan {t} di pedesaan menghadapi tantangan keterbatasan jaringan internet dan listrik.",
            "Panel surya digunakan sebagai sumber daya pada {t} di lahan yang jauh dari jaringan listrik.",
            "Analisis data historis dari {t} membantu petani menentukan waktu tanam yang tepat.",
            "Modul GSM menjadi alternatif komunikasi untuk {t} ketika sinyal WiFi tidak tersedia.",
        ],
    },
    "Kesehatan": {
        "topik": [
            "pemantauan detak jantung jarak jauh", "gelang kesehatan pintar", "monitor kadar glukosa",
            "pelacakan suhu tubuh pasien", "infus pintar", "pengingat minum obat otomatis",
            "telemedicine berbasis sensor", "pemantauan saturasi oksigen", "sensor deteksi jatuh lansia",
            "rekam medis terintegrasi perangkat wearable",
        ],
        "kalimat": [
            "Rumah sakit menerapkan {t} agar tenaga medis dapat memantau kondisi pasien tanpa kontak langsung.",
            "Data dari {t} dikirim ke server dan dianalisis untuk mendeteksi anomali kondisi pasien.",
            "Perangkat {t} menggunakan protokol Bluetooth Low Energy untuk menghemat daya baterai.",
            "Privasi data pasien pada {t} harus dijaga dengan enkripsi dan kontrol akses yang ketat.",
            "Akurasi sensor pada {t} perlu dikalibrasi agar hasil pengukuran dapat dipercaya secara klinis.",
            "Peringatan dini dari {t} dikirim ke dokter dan keluarga melalui aplikasi seluler.",
            "Penelitian tentang {t} menunjukkan peningkatan kecepatan respons penanganan darurat.",
            "Integrasi {t} dengan kecerdasan buatan membantu memprediksi risiko penyakit kronis.",
        ],
    },
    "Industri": {
        "topik": [
            "pemeliharaan prediktif mesin", "pemantauan getaran motor", "manajemen aset pabrik",
            "pelacakan logistik gudang", "kontrol kualitas produksi otomatis", "pemantauan konsumsi energi pabrik",
            "robot lengan terhubung jaringan", "digital twin lini produksi", "sistem SCADA modern",
            "pemantauan rantai dingin distribusi",
        ],
        "kalimat": [
            "Industri 4.0 mengandalkan {t} untuk meningkatkan efisiensi dan mengurangi waktu henti produksi.",
            "Sensor industri pada {t} mengirim data menggunakan protokol MQTT dan OPC UA.",
            "Penerapan {t} memungkinkan teknisi mendeteksi kerusakan sebelum mesin berhenti beroperasi.",
            "Edge computing pada {t} memproses data di dekat sumber sehingga latensi menjadi rendah.",
            "Keamanan siber pada {t} menjadi perhatian utama karena serangan dapat melumpuhkan produksi.",
            "Platform analitik {t} memvisualisasikan indikator kinerja utama secara realtime.",
            "Integrasi {t} dengan sistem ERP mempercepat pengambilan keputusan manajemen.",
            "Tantangan {t} meliputi interoperabilitas perangkat dari berbagai produsen yang berbeda.",
        ],
    },
    "Kota Cerdas": {
        "topik": [
            "lampu jalan pintar", "manajemen parkir cerdas", "pemantauan kualitas udara kota",
            "pengelolaan sampah berbasis sensor", "sistem peringatan banjir dini", "lalu lintas adaptif",
            "transportasi publik terhubung", "pemantauan debit sungai", "meteran air pintar",
            "pemantauan kebisingan perkotaan",
        ],
        "kalimat": [
            "Pemerintah kota memanfaatkan {t} untuk meningkatkan kualitas layanan publik.",
            "Jaringan sensor {t} tersebar di berbagai titik kota dan terhubung melalui LoRaWAN.",
            "Data terbuka dari {t} dapat dimanfaatkan peneliti dan pengembang aplikasi masyarakat.",
            "Penerapan {t} membantu mengurangi kemacetan, polusi, dan konsumsi energi perkotaan.",
            "Pusat komando kota menampilkan data {t} pada dashboard terpadu untuk pemantauan realtime.",
            "Pembangunan {t} memerlukan standar komunikasi yang terbuka agar mudah diintegrasikan.",
            "Partisipasi warga dalam {t} meningkat melalui aplikasi pelaporan di ponsel pintar.",
            "Biaya pemeliharaan {t} menjadi pertimbangan penting dalam perencanaan anggaran daerah.",
        ],
    },
    "Pendidikan": {
        "topik": [
            "training kit IoT untuk siswa SMK", "praktikum mikrokontroler", "laboratorium IoT kampus",
            "absensi berbasis RFID", "kelas pintar dengan sensor kehadiran", "modul pembelajaran Arduino",
            "proyek akhir sistem tertanam", "kompetisi robotik pelajar", "simulasi jaringan sensor nirkabel",
            "pelatihan guru teknologi IoT",
        ],
        "kalimat": [
            "Pembelajaran {t} membantu siswa memahami konsep perangkat keras dan perangkat lunak secara terpadu.",
            "Penerapan {t} meningkatkan keterampilan abad 21 seperti pemecahan masalah dan kolaborasi.",
            "Kurikulum yang memuat {t} perlu disesuaikan dengan kebutuhan dunia industri.",
            "Evaluasi {t} dilakukan menggunakan kuesioner penerimaan teknologi dan uji kompetensi.",
            "Persepsi kemudahan penggunaan memengaruhi penerimaan siswa terhadap {t}.",
            "Ketersediaan perangkat dan kesiapan pengajar menjadi faktor penentu keberhasilan {t}.",
            "Platform simulasi daring dapat melengkapi {t} ketika perangkat fisik terbatas.",
            "Penelitian tindakan kelas pada {t} menunjukkan peningkatan motivasi belajar peserta didik.",
        ],
    },
    "Energi": {
        "topik": [
            "smart grid", "pemantauan panel surya", "meteran listrik pintar", "manajemen beban listrik rumah tangga",
            "baterai penyimpan energi terhubung", "pembangkit listrik mikrohidro terpantau", "stasiun pengisian kendaraan listrik",
            "audit energi gedung", "pemantauan turbin angin", "prediksi konsumsi daya",
        ],
        "kalimat": [
            "Operator listrik menggunakan {t} untuk menyeimbangkan pasokan dan permintaan daya.",
            "Data konsumsi dari {t} memungkinkan pelanggan memantau penggunaan listrik secara detail.",
            "Penerapan {t} mendukung integrasi energi terbarukan ke dalam jaringan listrik nasional.",
            "Sensor arus dan tegangan pada {t} dibaca oleh mikrokontroler lalu dikirim melalui MQTT.",
            "Algoritma pembelajaran mesin pada {t} memprediksi beban puncak untuk efisiensi operasi.",
            "Kendala {t} mencakup standar komunikasi, investasi awal, dan keamanan data pelanggan.",
            "Dashboard {t} menampilkan grafik daya, energi, dan biaya penggunaan harian.",
            "Penghematan energi akibat {t} dapat mencapai belasan persen pada gedung komersial.",
        ],
    },
    "Transportasi": {
        "topik": [
            "pelacakan kendaraan GPS", "manajemen armada logistik", "sistem peringatan kantuk pengemudi",
            "tiket elektronik transportasi umum", "pemantauan kondisi jalan", "kendaraan terhubung V2X",
            "pelacakan kontainer pelabuhan", "monitor tekanan ban otomatis", "navigasi pengiriman barang",
            "sistem parkir tanpa tiket",
        ],
        "kalimat": [
            "Perusahaan logistik menerapkan {t} agar lokasi dan kondisi kendaraan dapat dipantau terus-menerus.",
            "Modul GPS dan GSM pada {t} mengirim koordinat posisi ke server setiap beberapa detik.",
            "Penggunaan {t} menurunkan konsumsi bahan bakar dan meningkatkan ketepatan waktu pengiriman.",
            "Analitik data pada {t} membantu mengidentifikasi rute paling efisien.",
            "Keselamatan pengemudi meningkat berkat peringatan otomatis dari {t}.",
            "Tantangan {t} meliputi cakupan jaringan seluler dan kebutuhan daya perangkat di kendaraan.",
            "Sistem {t} dapat diintegrasikan dengan aplikasi pelanggan untuk pelacakan paket realtime.",
            "Privasi lokasi pengguna perlu dilindungi dalam pengelolaan data {t}.",
        ],
    },
}

# ---------------------------------------------------------------------------
# Kalimat teknis umum (protokol, arsitektur, keamanan, perangkat) untuk variasi kosakata
# ---------------------------------------------------------------------------
KALIMAT_TEKNIS = [
    "Protokol MQTT menggunakan model publish dan subscribe sehingga cocok untuk perangkat dengan sumber daya terbatas.",
    "Broker MQTT seperti Mosquitto bertugas menerima pesan dari penerbit dan meneruskannya ke pelanggan topik.",
    "Protokol CoAP dirancang untuk perangkat terbatas dan berjalan di atas UDP dengan overhead kecil.",
    "Arsitektur IoT umumnya terdiri atas lapisan perangkat, lapisan jaringan, lapisan platform, dan lapisan aplikasi.",
    "LoRaWAN menawarkan komunikasi jarak jauh dengan konsumsi daya rendah untuk sensor yang tersebar luas.",
    "Zigbee membentuk jaringan mesh yang andal untuk perangkat rumah pintar berdaya rendah.",
    "Bluetooth Low Energy banyak digunakan pada perangkat wearable karena hemat baterai.",
    "NB-IoT memanfaatkan infrastruktur seluler untuk menjangkau perangkat di area yang luas.",
    "Raspberry Pi sering berperan sebagai gateway yang mengumpulkan data sensor sebelum dikirim ke cloud.",
    "Arduino dan ESP8266 menjadi pilihan populer untuk pembelajaran sistem tertanam dan prototipe cepat.",
    "Sensor DHT22 mengukur suhu dan kelembaban udara dengan antarmuka digital satu kawat.",
    "Sensor ultrasonik HC-SR04 menghitung jarak berdasarkan waktu pantulan gelombang suara.",
    "Sensor PIR mendeteksi gerakan manusia melalui perubahan radiasi inframerah.",
    "Aktuator seperti relay, motor servo, dan solenoid mengubah perintah digital menjadi aksi fisik.",
    "Edge computing memproses data di dekat sumbernya untuk mengurangi latensi dan beban jaringan.",
    "Cloud computing menyediakan penyimpanan dan analitik skala besar untuk data yang dihasilkan perangkat IoT.",
    "Kecerdasan buatan dan pembelajaran mesin digunakan untuk mengenali pola dan memprediksi kejadian dari data sensor.",
    "Keamanan IoT mencakup autentikasi perangkat, enkripsi TLS, dan pembaruan firmware over the air.",
    "Serangan botnet seperti Mirai memanfaatkan perangkat IoT dengan kata sandi bawaan yang lemah.",
    "Standar IPv6 menyediakan ruang alamat yang cukup untuk miliaran perangkat IoT.",
    "Manajemen daya dan mode deep sleep memperpanjang umur baterai perangkat sensor.",
    "Basis data deret waktu seperti InfluxDB cocok untuk menyimpan data sensor dengan penanda waktu.",
    "Platform Node-RED memudahkan perancangan alur data IoT dengan pemrograman visual.",
    "Interoperabilitas antarperangkat membutuhkan standar terbuka dan antarmuka pemrograman aplikasi yang konsisten.",
    "Visualisasi data melalui dashboard Grafana membantu pengguna memahami tren dan anomali dengan cepat.",
    "Firmware perangkat perlu diperbarui secara berkala untuk menutup celah keamanan yang ditemukan.",
    "Latensi, bandwidth, dan keandalan koneksi menjadi parameter kualitas layanan pada jaringan IoT.",
    "Digital twin adalah replika virtual dari objek fisik yang diperbarui menggunakan data sensor realtime.",
    "Jaringan 5G menjanjikan latensi rendah dan kapasitas koneksi besar untuk aplikasi IoT masif.",
    "Blockchain diusulkan untuk menjaga integritas dan keterlacakan data pada ekosistem IoT.",
]

PEMBUKA = [
    "Artikel ini membahas {t} dalam konteks {k}.",
    "Perkembangan teknologi Internet of Things mendorong pemanfaatan {t} di bidang {k}.",
    "Studi kasus tentang {t} memberikan gambaran penerapan IoT pada sektor {k}.",
    "Tinjauan singkat mengenai {t} menyoroti manfaat dan tantangan implementasinya.",
    "Salah satu penerapan IoT yang menarik di bidang {k} adalah {t}.",
    "Penelitian terkini mengkaji rancang bangun {t} berbasis mikrokontroler dan jaringan nirkabel.",
]

PENUTUP = [
    "Ke depan, penelitian lanjutan diperlukan untuk meningkatkan akurasi, keamanan, dan skalabilitas sistem.",
    "Hasil uji coba menunjukkan sistem berjalan stabil dengan tingkat keberhasilan pengiriman data yang tinggi.",
    "Dengan perencanaan yang tepat, penerapan teknologi ini dapat memberikan manfaat ekonomi yang signifikan.",
    "Kolaborasi antara akademisi, industri, dan pemerintah akan mempercepat adopsi teknologi ini.",
    "Pengembangan lebih lanjut dapat memanfaatkan analitik data besar dan kecerdasan buatan.",
    "Evaluasi pengguna menunjukkan bahwa sistem mudah digunakan dan bermanfaat bagi pengguna akhir.",
]

JUDUL = [
    "Rancang Bangun {T} Berbasis IoT",
    "Implementasi {T} Menggunakan ESP32 dan MQTT",
    "Analisis {T} pada Bidang {K}",
    "Tinjauan Penerapan {T} di Sektor {K}",
    "Pemanfaatan {T} untuk Meningkatkan Efisiensi",
    "Studi Kasus {T}: Tantangan dan Peluang",
    "Sistem {T} dengan Dashboard Realtime",
    "Keamanan dan Privasi pada {T}",
    "Pengembangan {T} Berbasis Cloud",
    "Perbandingan Protokol Komunikasi pada {T}",
]


def buat_dokumen(i: int) -> dict:
    kategori = random.choice(list(KATEGORI))
    data = KATEGORI[kategori]
    topik = random.choice(data["topik"])

    judul = random.choice(JUDUL).format(T=topik.title(), K=kategori)
    kalimat = [random.choice(PEMBUKA).format(t=topik, k=kategori.lower())]
    kalimat += [s.format(t=topik) for s in random.sample(data["kalimat"], k=random.randint(2, 4))]
    kalimat += random.sample(KALIMAT_TEKNIS, k=random.randint(2, 4))
    pembuka, isi_tengah = kalimat[0], kalimat[1:]
    random.shuffle(isi_tengah)
    kalimat = [pembuka] + isi_tengah + [random.choice(PENUTUP)]

    return {
        "id": i,
        "judul": judul,
        "kategori": kategori,
        "isi": " ".join(kalimat),
    }


if __name__ == "__main__":
    dokumen = [buat_dokumen(i) for i in range(1, JUMLAH_DOKUMEN + 1)]
    with open("data/dokumen_iot.json", "w", encoding="utf-8") as f:
        json.dump(dokumen, f, ensure_ascii=False, indent=2)
    print(f"{len(dokumen)} dokumen berhasil dibuat -> data/dokumen_iot.json")
