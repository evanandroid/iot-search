"""
Aplikasi web Mesin Pencari IoT (VSM + TF-IDF)

Jalankan:
    pip install flask
    python generate_dataset.py     # sekali saja, membuat data/dokumen_iot.json
    python app.py                  # buka http://127.0.0.1:5000
"""
import math
import os

from flask import Flask, abort, jsonify, render_template, request

from preprocessing import preprocess_trace
from vsm_engine import VSMEngine

BASE = os.path.dirname(os.path.abspath(__file__))
DATASET = os.path.join(BASE, "data", "dokumen_iot.json")
PER_HALAMAN = 10

app = Flask(__name__)
engine = VSMEngine(DATASET)  # indeksasi dilakukan sekali saat aplikasi dijalankan

CONTOH_KUERI = [
    "pemantauan kelembaban tanah",
    "lampu pintar rumah",
    "keamanan protokol MQTT",
    "sensor deteksi jatuh lansia",
    "smart grid energi terbarukan",
    "training kit IoT siswa SMK",
]


@app.route("/")
def index():
    return render_template(
        "index.html",
        stat=engine.statistik(),
        kategori=engine.kategori(),
        contoh=CONTOH_KUERI,
        populer=engine.term_teratas(10),
    )


@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    kategori = request.args.get("kategori", "").strip()
    halaman = max(1, request.args.get("page", 1, type=int))

    if not q:
        return render_template("results.html", q="", kategori=kategori, kategori_list=engine.kategori(),
                               kosong=True, hasil=[], total=0, halaman=1, jumlah_halaman=1,
                               stat=engine.statistik())

    r = engine.cari(q, kategori=kategori)
    terms = set(r["vektor_kueri"]["terms"])
    jumlah_halaman = max(1, math.ceil(r["total"] / PER_HALAMAN))
    halaman = min(halaman, jumlah_halaman)
    mulai = (halaman - 1) * PER_HALAMAN

    tampil = []
    for item in r["hasil"][mulai: mulai + PER_HALAMAN]:
        d = engine.dokumen[item["id"]]
        tampil.append({
            **item,
            "judul": d["judul"],
            "kategori": d["kategori"],
            "cuplikan": engine.sorot(d["isi"], terms),
        })

    skor_maks = r["hasil"][0]["skor"] if r["hasil"] else 1
    return render_template(
        "results.html", q=q, kategori=kategori, kategori_list=engine.kategori(), kosong=False,
        hasil=tampil, total=r["total"], waktu_ms=r["waktu_ms"], halaman=halaman,
        jumlah_halaman=jumlah_halaman, vektor=r["vektor_kueri"], norm_kueri=r["norm_kueri"],
        skor_maks=skor_maks, mulai=mulai, stat=engine.statistik(),
    )


@app.route("/doc/<int:did>")
def dokumen(did):
    if did not in engine.dokumen:
        abort(404)
    q = request.args.get("q", "").strip()
    terms = set(engine.vektor_kueri(q)["terms"]) if q else set()
    info = engine.detail_dokumen(did)
    return render_template("doc.html", info=info, q=q,
                           isi=engine.sorot(info["dokumen"]["isi"], terms, panjang=10_000))


@app.route("/preprocessing", methods=["GET", "POST"])
def pipeline():
    teks = (request.form.get("teks") or request.args.get("teks") or
            "Pemantauan kelembaban tanah secara otomatis menggunakan sensor dan jaringan nirkabel!").strip()
    return render_template("pipeline.html", teks=teks, trace=preprocess_trace(teks))


# ------------------------------------------------------------------ API JSON
@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").strip()
    k = request.args.get("k", 10, type=int)
    r = engine.cari(q, top_k=k)
    return jsonify({
        "query": q,
        "term_kueri": r["vektor_kueri"]["terms"],
        "total": r["total"],
        "waktu_ms": r["waktu_ms"],
        "hasil": [{"rank": h["rank"], "id": h["id"], "skor": round(h["skor"], 6),
                   "judul": engine.dokumen[h["id"]]["judul"]} for h in r["hasil"]],
    })


@app.route("/api/preprocess")
def api_preprocess():
    return jsonify(preprocess_trace(request.args.get("teks", "")))


@app.template_filter("fmt")
def fmt(nilai, digit=4):
    return f"{nilai:.{digit}f}"


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
