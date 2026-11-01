"""
API Flask untuk prediksi risiko diabetes.

Cara pakai:
  1. Taruh file ini di folder yang SAMA dengan model_diabetes.pkl dan fitur.json
  2. pip install flask flask-cors pandas scikit-learn joblib
  3. python app.py
  4. Buka http://127.0.0.1:8000/health untuk mengecek server
"""
import json
import os
import joblib
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

BASE = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(BASE, "model_diabetes.pkl"))
with open(os.path.join(BASE, "fitur.json")) as f:
    FITUR = json.load(f)  # urutan kolom harus sama dengan saat training

# Batas nilai yang masuk akal (min, max) untuk validasi input
BATAS = {
    "Pregnancies": (0, 20),
    "Glucose": (40, 500),
    "BloodPressure": (30, 200),
    "SkinThickness": (0, 100),
    "Insulin": (0, 900),
    "BMI": (10, 70),
    "DiabetesPedigreeFunction": (0, 3),
    "Age": (1, 120),
}
WAJIB = ["Glucose", "BMI", "Age"]  # fitur lain boleh dikosongkan (diisi median oleh model)
NAMA = {"Pregnancies": "Jumlah kehamilan", "Glucose": "Kadar glukosa", "BloodPressure": "Tekanan darah",
        "SkinThickness": "Ketebalan kulit", "Insulin": "Insulin", "BMI": "BMI",
        "DiabetesPedigreeFunction": "Riwayat keluarga (DPF)", "Age": "Usia"}
DISCLAIMER = "Hasil ini adalah skrining awal berbasis AI, bukan diagnosis medis. Konsultasikan dengan dokter."

app = Flask(__name__)
CORS(app)  # izinkan website (alamat berbeda) memanggil API ini


@app.get("/health")
def health():
    return jsonify({"status": "ok", "fitur": FITUR})


@app.post("/predict")
def predict():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Kirim data dalam format JSON."}), 400

    nilai, galat = {}, []
    for k in FITUR:
        v = data.get(k)
        if v is None or (isinstance(v, str) and v.strip() == ""):
            if k in WAJIB:
                galat.append(f"{NAMA[k]} wajib diisi.")
            nilai[k] = None  # dibiarkan kosong -> diisi median oleh model
            continue
        try:
            v = float(v)
        except (TypeError, ValueError):
            galat.append(f"{NAMA[k]} harus berupa angka.")
            continue
        lo, hi = BATAS[k]
        if not (lo <= v <= hi):
            galat.append(f"{NAMA[k]} harus antara {lo} dan {hi}.")
            continue
        nilai[k] = v
    if galat:
        return jsonify({"error": " ".join(galat), "detail": galat}), 400

    X = pd.DataFrame([nilai], columns=FITUR).astype(float)  # None -> NaN
    prob = float(model.predict_proba(X)[0][1])               # peluang kelas "diabetes"
    tinggi = prob >= 0.5
    return jsonify({
        "label": "Risiko tinggi" if tinggi else "Risiko rendah",
        "probability": round(prob, 4),                        # peluang risiko diabetes
        "confidence": round(prob if tinggi else 1 - prob, 4),  # keyakinan pada label yang dipilih
        "disclaimer": DISCLAIMER,
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)
