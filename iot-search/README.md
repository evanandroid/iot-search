# IoT Search: Mesin Pencari VSM + TF-IDF

Mesin pencari berbasis Vector Space Model (VSM) dan TF-IDF dengan 1.000 dokumen bertema Internet of Things.

## Menjalankan

```bash
pip install -r requirements.txt
python generate_dataset.py   # opsional, dataset sudah disertakan di data/dokumen_iot.json
python app.py                # buka http://127.0.0.1:5000
```

## Struktur

| Berkas | Fungsi |
|---|---|
| `generate_dataset.py` | Membuat 1.000 dokumen IoT (sintetis, seed tetap sehingga hasilnya konsisten) |
| `preprocessing.py` | **Fitur 2**: case folding, cleaning, tokenizing, stopword removal, stemming |
| `vsm_engine.py` | **Fitur 3**: inverted index, pembobotan TF-IDF, cosine similarity, perangkingan |
| `app.py` | Rute Flask: `/`, `/search`, `/doc/<id>`, `/preprocessing`, `/api/search`, `/api/preprocess` |
| `templates/index.html` | **Fitur 1**: dashboard pencarian |
| `templates/results.html` | **Fitur 4**: halaman hasil pencarian |

## Rumus

- TF: `tf = 1 + log10(f)`
- IDF: `idf = log10(N / df)`
- Bobot: `w = tf x idf`
- Kemiripan: `cos(q, d) = (q . d) / (|q| x |d|)`

Judul dokumen dihitung dua kali saat indeksasi sehingga kata pada judul lebih berbobot.
Term yang muncul di seluruh dokumen bernilai idf = 0 sehingga tidak memengaruhi peringkat.

## Catatan

- Stemmer ditulis sendiri (berbasis aturan + kamus kata dasar kecil di `preprocessing.py`), tanpa Sastrawi.
  Jika dataset diganti, tambahkan kata dasar baru ke `ROOT_WORDS` atau gunakan Sastrawi.
- Untuk memakai dataset sendiri, ganti `data/dokumen_iot.json` dengan format
  `[{"id": 1, "judul": "...", "kategori": "...", "isi": "..."}, ...]`.
