"""
Menguji API tanpa tampilan website. Jalankan SETELAH `python app.py` aktif
(di terminal lain):   python test_api.py
"""
import json
import urllib.request
import urllib.error

URL = "http://127.0.0.1:8000/predict"

KASUS = {
    "Glukosa normal":        {"Glucose": 90,  "BMI": 22,   "Age": 25},
    "Risiko tinggi":         {"Glucose": 180, "BMI": 38,   "Age": 55, "Pregnancies": 6},
    "Data lengkap":          {"Pregnancies": 2, "Glucose": 120, "BloodPressure": 70, "SkinThickness": 25,
                              "Insulin": 100, "BMI": 30, "DiabetesPedigreeFunction": 0.5, "Age": 40},
    "Glukosa kosong":        {"BMI": 25, "Age": 30},
    "Huruf, bukan angka":    {"Glucose": "abc", "BMI": 25, "Age": 30},
    "Usia tidak masuk akal": {"Glucose": 100, "BMI": 25, "Age": -5},
}

for nama, data in KASUS.items():
    req = urllib.request.Request(URL, json.dumps(data).encode(), {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            hasil = json.load(r)
            print(f"[{r.status}] {nama}: {hasil['label']} (peluang {hasil['probability']:.0%})")
    except urllib.error.HTTPError as e:
        print(f"[{e.code}] {nama}: {json.load(e)['error']}")
    except urllib.error.URLError:
        print("Server belum berjalan. Jalankan dulu: python app.py")
        break
