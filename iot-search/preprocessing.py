"""
Fitur 2 - Sistem Pra-proses Teks (Preprocessing Pipeline)

Tahapan:
  1. Case folding      : mengubah seluruh huruf menjadi huruf kecil
  2. Cleaning          : membuang angka, tanda baca, dan karakter khusus
  3. Tokenizing        : memecah teks menjadi token (kata)
  4. Stopword removal  : membuang kata umum yang tidak membawa makna (yang, dan, di, ...)
  5. Stemming          : mengubah kata berimbuhan menjadi kata dasar (algoritma berbasis
                         aturan ala Nazief & Adriani + kamus kata dasar sederhana)

Seluruh modul ditulis tanpa dependensi eksternal agar mudah dijalankan.
"""
import re
from functools import lru_cache

# ---------------------------------------------------------------------------
# Stopword bahasa Indonesia (+ beberapa kata Inggris umum yang muncul pada teks teknis)
# ---------------------------------------------------------------------------
STOPWORDS = set("""
yang dan di ke dari pada untuk dengan dalam adalah ini itu atau juga akan dapat agar
oleh sebagai karena sehingga serta bagi atas antara tentang terhadap hanya lebih paling
sangat saat ketika jika apabila bahwa sudah telah masih belum tidak bukan tanpa secara
setiap beberapa banyak berbagai seperti yaitu yakni melalui hingga sampai lalu kemudian
sebelum sesudah selama sambil bila mungkin harus perlu para si sang nya pun lah kah
saya kami kita kamu anda mereka dia ia ada
the of and in to a is for on with an as by at from
""".split())

# Kata yang tidak boleh di-stem (istilah teknis / kata dasar yang mirip imbuhan)
PROTECTED = set("""
sensor internet protokol data platform server broker gateway mikrokontroler arduino
raspberry firmware cloud dashboard bluetooth wifi mqtt coap lora lorawan zigbee aktuator
aplikasi informasi komputer jaringan perangkat sistem energi industri mesin manusia
pasien dokter rumah sakit kota desa kampus pelajar siswa guru modul relay motor servo
baterai listrik daya teknologi analisis analitik algoritma evaluasi operasi integrasi
transportasi logistik kualitas kapasitas privasi enkripsi standar simulasi prediksi
komunikasi koneksi informasi parameter deteksi monitor kontrol status model mode
internet iot esp scada rfid gps gsm udp tls ipv blockchain digital virtual
beban masalah pemerintah perintah
""".split())

# Kamus kata dasar sederhana (domain umum + domain IoT). Digunakan sebagai pembanding
# hasil pemotongan imbuhan: stem hanya diterima jika hasilnya ada di kamus ini.
ROOT_WORDS = set("""
pantau kirim ukur hemat guna bangun rancang kembang terap manfaat ajar baca hasil jaga
kalibrasi sesuai pelihara butuh andal lacak layan tingkat tinggi rendah laku kerja hubung
tanam batas buka sedia jadi mampu mudah ubah proses simpan tampil cakup capai dorong
dukung tekan tentu terima harap ingat isi kenal hitung identifikasi kumpul kurang jangkau
janji tunjuk turun tutup nyala imbang sentuh soroti lengkap liput lumpuh muat tarik tawar
bahas bentuk beri buat cepat paham pengaruh panjang mungkin kaji kena terus lalu dasar
aman tepat siap sedia ada sebab usul uji coba kembali sebar ganti bagi rawat jalan
lampu pintu kunci cerdas pintar tanah air udara suhu kelembaban cahaya arus tegangan
kendara parkir sampah banjir sungai tambak panen tani hama ternak pakan ikan ayam
obat jantung detak tubuh infus lansia jatuh nafas oksigen darah sakit sehat mudah
sumber tenaga biaya waktu tempat lokasi posisi jarak gerak getar suara gelombang
kait atur kelola ukur kendali operasi bantu mampu bukti hasil tanggap
kembang pelajar didik latih pelatihan siswa guru kurikulum ajar belajar
alir kabel nirkabel pasang lindung sambung lanjut
""".split())

PARTICLES = ("lah", "kah", "tah", "pun")
POSSESSIVES = ("nya", "ku", "mu")
SUFFIXES = ("kan", "an", "i")  # dicoba lebih dulu daripada tanpa sufiks

# (awalan, [pengganti huruf awal kata dasar])
PREFIX_RULES = [
    ("memper", [""]), ("diper", [""]), ("meng", ["", "k"]), ("meny", ["s"]),
    ("men", ["", "t"]), ("mem", ["", "p"]), ("me", [""]),
    ("peng", ["", "k"]), ("peny", ["s"]), ("pen", ["", "t"]), ("pem", ["", "p"]),
    ("per", [""]), ("pe", [""]), ("ber", [""]), ("bel", [""]), ("be", [""]),
    ("ter", [""]), ("te", [""]), ("di", [""]), ("ke", [""]), ("se", [""]),
]

_PUNCT_RE = re.compile(r"[^a-z\s]")
_SPACE_RE = re.compile(r"\s+")
_WORD_RE = re.compile(r"[A-Za-z]+")


# ---------------------------------------------------------------------------
# Tahap 1-4
# ---------------------------------------------------------------------------
def case_folding(teks: str) -> str:
    return teks.lower()


def cleaning(teks: str) -> str:
    teks = _PUNCT_RE.sub(" ", teks)
    return _SPACE_RE.sub(" ", teks).strip()


def tokenizing(teks: str) -> list:
    return teks.split() if teks else []


def stopword_removal(tokens: list) -> list:
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


# ---------------------------------------------------------------------------
# Tahap 5: stemming
# ---------------------------------------------------------------------------
def _prefix_candidates(kata: str, depth: int = 0):
    """Hasilkan kandidat kata dasar setelah membuang awalan (maksimal 2 lapis)."""
    for awalan, pengganti in PREFIX_RULES:
        if kata.startswith(awalan) and len(kata) - len(awalan) >= 3:
            sisa = kata[len(awalan):]
            for p in pengganti:
                kandidat = p + sisa
                yield kandidat
                if depth < 1:
                    yield from _prefix_candidates(kandidat, depth + 1)


@lru_cache(maxsize=50000)
def stem(kata: str) -> str:
    if len(kata) <= 3 or kata in PROTECTED or kata in ROOT_WORDS:
        return kata

    asli = kata
    # buang partikel (-lah, -kah, ...) lalu kata ganti kepunyaan (-nya, -ku, -mu)
    for p in PARTICLES:
        if kata.endswith(p) and len(kata) - len(p) >= 4:
            kata = kata[: -len(p)]
            break
    for p in POSSESSIVES:
        if kata.endswith(p) and len(kata) - len(p) >= 4:
            kata = kata[: -len(p)]
            break
    if kata in PROTECTED or kata in ROOT_WORDS:
        return kata

    # coba semua kombinasi sufiks (derivasi) x awalan, terima jika ada di kamus
    for suf in SUFFIXES + ("",):
        if suf and not kata.endswith(suf):
            continue
        dasar = kata[: len(kata) - len(suf)] if suf else kata
        if len(dasar) < 3:
            continue
        if dasar in ROOT_WORDS:
            return dasar
        for kandidat in _prefix_candidates(dasar):
            if kandidat in ROOT_WORDS:
                return kandidat
    # tidak ditemukan di kamus -> biarkan (hindari over-stemming istilah teknis)
    return kata if kata != asli else asli


def stemming(tokens: list) -> list:
    return [stem(t) for t in tokens]


# ---------------------------------------------------------------------------
# Pipeline lengkap
# ---------------------------------------------------------------------------
def preprocess(teks: str) -> list:
    """Pipeline lengkap -> daftar term siap diindeks."""
    return stemming(stopword_removal(tokenizing(cleaning(case_folding(teks)))))


def preprocess_trace(teks: str) -> dict:
    """Pipeline lengkap dengan hasil antara setiap tahap (untuk ditampilkan di UI)."""
    t1 = case_folding(teks)
    t2 = cleaning(t1)
    t3 = tokenizing(t2)
    t4 = stopword_removal(t3)
    t5 = stemming(t4)
    return {
        "asli": teks,
        "case_folding": t1,
        "cleaning": t2,
        "tokenizing": t3,
        "stopword_removal": t4,
        "stopword_terbuang": [t for t in t3 if t not in t4],
        "stemming": t5,
        "perubahan_stem": [(a, b) for a, b in zip(t4, t5) if a != b],
    }


def kata_asli(teks: str):
    """Iterator kata (huruf saja) pada teks asli beserta posisi, untuk highlight."""
    for m in _WORD_RE.finditer(teks):
        yield m
