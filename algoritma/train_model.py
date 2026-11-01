"""
Melatih model Logistic Regression untuk prediksi risiko diabetes.

Cara pakai:
  1. Taruh diabetes.csv (dari Kaggle) di folder yang sama dengan file ini.
  2. pip install pandas scikit-learn joblib
  3. python train_model.py
Hasil: model_diabetes.pkl dan fitur.json (dipakai oleh API).
"""
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix,
                             classification_report)

# ---------- 1. Baca data ----------
df = pd.read_csv("diabetes.csv")
print("Ukuran data:", df.shape)
print(df["Outcome"].value_counts(), "\n")

# ---------- 2. Bersihkan data ----------
# Pada dataset ini, angka 0 di kolom berikut sebenarnya data hilang.
kolom_nol = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]
df[kolom_nol] = df[kolom_nol].replace(0, np.nan)
print("Data hilang per kolom:\n", df.isna().sum(), "\n")

# ---------- 3. Pisahkan fitur dan target, lalu bagi data ----------
FITUR = ["Pregnancies", "Glucose", "BloodPressure", "BMI", "Age"]
X = df[FITUR]
y = df["Outcome"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

# ---------- 4. Susun model ----------
# Imputasi (isi data hilang dengan median) dan scaling ada DI DALAM pipeline,
# supaya hanya belajar dari data latih (tidak bocor ke data uji).
model = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression(class_weight="balanced", max_iter=1000)),
])
model.fit(X_train, y_train)

# ---------- 5. Evaluasi pada data uji ----------
pred = model.predict(X_test)
prob = model.predict_proba(X_test)[:, 1]
print("=== HASIL EVALUASI (data uji) ===")
print(f"Akurasi  : {accuracy_score(y_test, pred):.3f}")
print(f"Precision: {precision_score(y_test, pred):.3f}")
print(f"Recall   : {recall_score(y_test, pred):.3f}")
print(f"F1-score : {f1_score(y_test, pred):.3f}")
print(f"ROC-AUC  : {roc_auc_score(y_test, prob):.3f}")
print("\nConfusion matrix (baris = asli, kolom = prediksi):")
print(confusion_matrix(y_test, pred))
print("\n", classification_report(y_test, pred, target_names=["Tidak diabetes", "Diabetes"]))

# ---------- 6. Fitur yang paling berpengaruh ----------
koef = pd.Series(model.named_steps["clf"].coef_[0], index=X.columns)
print("Koefisien (makin positif = makin menaikkan risiko):")
print(koef.sort_values(ascending=False).round(3))

# ---------- 7. Simpan model ----------
joblib.dump(model, "model_diabetes.pkl")
with open("fitur.json", "w") as f:
    json.dump(list(X.columns), f)
print("\nModel disimpan ke model_diabetes.pkl")