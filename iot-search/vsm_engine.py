"""
Fitur 3 - Mesin Hitung VSM & Perangkingan (Backend Engine)

Alur kerja:
  1. Indeksasi   : setiap dokumen di-preprocess lalu dibangun inverted index
                   term -> {id_dokumen: tf}
  2. Pembobotan  : TF-IDF
                       tf  = 1 + log10(f)            (f = frekuensi term dalam dokumen)
                       idf = log10(N / df)           (N = jumlah dokumen, df = jumlah dokumen yang memuat term)
                       w   = tf x idf
  3. Perangkingan: Vector Space Model dengan Cosine Similarity
                       sim(q, d) = (q . d) / (|q| x |d|)
                   Dokumen diurutkan menurun berdasarkan nilai similarity.
"""
import json
import math
import time
from collections import Counter, defaultdict

from markupsafe import Markup, escape

from preprocessing import preprocess, stem, kata_asli, case_folding


class VSMEngine:
    def __init__(self, path_dataset: str):
        with open(path_dataset, encoding="utf-8") as f:
            self.dokumen = {d["id"]: d for d in json.load(f)}
        self.N = len(self.dokumen)

        self.doc_terms = {}                      # id -> Counter(term -> f)
        self.inverted = defaultdict(dict)        # term -> {id: f}
        self.idf = {}                            # term -> idf
        self.doc_weights = {}                    # id -> {term: w}
        self.doc_norm = {}                       # id -> |d|
        self.waktu_indeksasi = 0.0
        self._bangun_indeks()

    # ------------------------------------------------------------------ indeksasi
    def _bangun_indeks(self):
        mulai = time.perf_counter()

        # 1) preprocessing + inverted index (judul dihitung dua kali agar lebih berbobot)
        for did, d in self.dokumen.items():
            terms = preprocess(d["judul"]) * 2 + preprocess(d["isi"])
            cnt = Counter(terms)
            self.doc_terms[did] = cnt
            for term, f in cnt.items():
                self.inverted[term][did] = f

        # 2) IDF
        for term, posting in self.inverted.items():
            self.idf[term] = math.log10(self.N / len(posting))

        # 3) bobot TF-IDF + panjang vektor dokumen
        for did, cnt in self.doc_terms.items():
            bobot = {t: (1 + math.log10(f)) * self.idf[t] for t, f in cnt.items()}
            self.doc_weights[did] = bobot
            self.doc_norm[did] = math.sqrt(sum(w * w for w in bobot.values()))

        self.waktu_indeksasi = time.perf_counter() - mulai

    # ------------------------------------------------------------------ statistik
    def statistik(self) -> dict:
        total_token = sum(sum(c.values()) for c in self.doc_terms.values())
        return {
            "jumlah_dokumen": self.N,
            "jumlah_term": len(self.inverted),
            "total_token": total_token,
            "rata_term_per_dokumen": round(total_token / self.N, 1),
            "waktu_indeksasi_ms": round(self.waktu_indeksasi * 1000, 1),
            "jumlah_kategori": len({d["kategori"] for d in self.dokumen.values()}),
        }

    def kategori(self) -> list:
        return sorted({d["kategori"] for d in self.dokumen.values()})

    def term_teratas(self, n=12) -> list:
        """Term dengan df terbanyak (untuk contoh kata kunci populer)."""
        urut = sorted(self.inverted.items(), key=lambda kv: -len(kv[1]))
        return [(t, len(p)) for t, p in urut if self.idf[t] > 0][:n]

    # ------------------------------------------------------------------ pencarian
    def vektor_kueri(self, query: str) -> dict:
        """Bobot kueri: (1 + log10 tf) x idf; term di luar kosakata diabaikan."""
        terms = preprocess(query)
        cnt = Counter(terms)
        detail = []
        for t, f in cnt.items():
            if t in self.idf:
                w = (1 + math.log10(f)) * self.idf[t]
                detail.append({"term": t, "tf": f, "df": len(self.inverted[t]),
                               "idf": self.idf[t], "w": w, "dikenal": True})
            else:
                detail.append({"term": t, "tf": f, "df": 0, "idf": 0.0, "w": 0.0, "dikenal": False})
        return {"terms": terms, "detail": detail}

    def cari(self, query: str, kategori: str = "", top_k: int = None) -> dict:
        mulai = time.perf_counter()
        vk = self.vektor_kueri(query)
        wq = {d["term"]: d["w"] for d in vk["detail"] if d["dikenal"] and d["w"] > 0}
        norm_q = math.sqrt(sum(w * w for w in wq.values()))

        hasil = []
        total = 0
        if norm_q > 0:
            dot = defaultdict(float)
            kontribusi = defaultdict(dict)
            for t, w_q in wq.items():
                for did in self.inverted[t]:
                    w_d = self.doc_weights[did][t]
                    dot[did] += w_q * w_d
                    kontribusi[did][t] = w_d
            for did, nilai in dot.items():
                if self.doc_norm[did] == 0:
                    continue
                d = self.dokumen[did]
                if kategori and d["kategori"] != kategori:
                    continue
                skor = nilai / (norm_q * self.doc_norm[did])
                hasil.append({"id": did, "skor": skor, "term_cocok": sorted(kontribusi[did])})
            hasil.sort(key=lambda r: (-r["skor"], r["id"]))
            total = len(hasil)
            if top_k:
                hasil = hasil[:top_k]
            for rank, r in enumerate(hasil, 1):
                r["rank"] = rank

        return {
            "query": query,
            "vektor_kueri": vk,
            "norm_kueri": norm_q,
            "hasil": hasil,
            "total": total,
            "waktu_ms": round((time.perf_counter() - mulai) * 1000, 2),
        }

    # ------------------------------------------------------------------ tampilan
    def sorot(self, teks: str, terms: set, panjang: int = 260) -> Markup:
        """Potong teks di sekitar kata cocok pertama lalu beri <mark> pada kata yang cocok."""
        posisi = None
        for m in kata_asli(teks):
            if stem(case_folding(m.group())) in terms:
                posisi = m.start()
                break
        mulai = 0
        if posisi is not None and posisi > panjang // 3:
            mulai = teks.rfind(" ", 0, posisi - panjang // 4) + 1
        potongan = teks[mulai: mulai + panjang]
        if mulai + panjang < len(teks):
            potongan = potongan.rsplit(" ", 1)[0] + " ..."
        if mulai > 0:
            potongan = "... " + potongan

        keluar, akhir = [], 0
        for m in kata_asli(potongan):
            if stem(case_folding(m.group())) in terms:
                keluar.append(str(escape(potongan[akhir:m.start()])))
                keluar.append(f"<mark>{escape(m.group())}</mark>")
                akhir = m.end()
        keluar.append(str(escape(potongan[akhir:])))
        return Markup("".join(keluar))

    def detail_dokumen(self, did: int, query_terms=None, top=15) -> dict:
        d = self.dokumen[did]
        bobot = self.doc_weights[did]
        urut = sorted(bobot.items(), key=lambda kv: -kv[1])[:top]
        return {
            "dokumen": d,
            "norm": self.doc_norm[did],
            "jumlah_term": len(bobot),
            "term_teratas": [
                {"term": t, "tf": self.doc_terms[did][t], "df": len(self.inverted[t]),
                 "idf": self.idf[t], "w": w} for t, w in urut
            ],
        }
