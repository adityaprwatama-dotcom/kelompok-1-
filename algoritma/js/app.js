/* Logika form Cek Risiko: validasi, hitung BMI, panggil API, tampilkan hasil. */
(function () {
  const $ = s => document.querySelector(s);
  const el = { usia: $("#usia"), glukosa: $("#glukosa"), berat: $("#berat"), tinggi: $("#tinggi"),
               hamil: $("#hamil"), td: $("#td"), bmi: $("#bmi"), err: $("#err"), hasil: $("#hasil"), btn: $("#btn") };

  const num = e => (e.value.trim() === "" ? null : Number(e.value));
  const hitungBMI = () => {
    const b = num(el.berat), t = num(el.tinggi);
    return b && t ? Math.round((b / ((t / 100) ** 2)) * 10) / 10 : null;
  };
  function tampilBMI() { const v = hitungBMI(); el.bmi.textContent = v ? v : "-"; }
  [el.berat, el.tinggi].forEach(e => e.addEventListener("input", tampilBMI));

  function esc(s) { const d = document.createElement("div"); d.textContent = s; return d.innerHTML; }
  function galat(msg) { el.err.textContent = msg; el.err.hidden = false; el.hasil.hidden = true; }

  // Validasi sisi pengguna (batas sama dengan yang dipakai API)
  function validasi() {
    const aturan = [
      [el.usia, "Usia", 1, 120, true], [el.glukosa, "Gula darah puasa", 40, 500, true],
      [el.berat, "Berat badan", 10, 300, true], [el.tinggi, "Tinggi badan", 80, 230, true],
      [el.hamil, "Jumlah kehamilan", 0, 20, false], [el.td, "Tekanan darah", 30, 200, false]
    ];
    for (const [e, nama, lo, hi, wajib] of aturan) {
      const v = num(e);
      if (v === null) { if (wajib) return nama + " wajib diisi."; continue; }
      if (Number.isNaN(v) || v < lo || v > hi) return nama + " harus antara " + lo + " dan " + hi + ".";
    }
    const bmi = hitungBMI();
    if (bmi < 10 || bmi > 70) return "BMI hasil perhitungan (" + bmi + ") tidak masuk akal. Periksa berat dan tinggi badan.";
    return null;
  }

  function tampilkan(r) {
    const pct = Math.round(r.probability * 100), tinggi = r.label === "Risiko tinggi";
    el.hasil.innerHTML =
      '<div class="label dark">Hasil</div>' +
      '<div class="lvl">' + esc(r.label) + '</div>' +
      '<p class="pct">Perkiraan peluang: <b>' + pct + '%</b></p>' +
      '<div class="bar" role="img" aria-label="Peluang ' + pct + ' persen"><i style="width:' + pct + '%"></i></div>' +
      '<p>' + (tinggi
        ? "Pola datamu mirip dengan pola pada orang yang terdiagnosis diabetes di data latih. Sebaiknya segera periksakan gula darah ke dokter atau fasilitas kesehatan."
        : "Pola datamu lebih mirip dengan orang yang tidak terdiagnosis diabetes di data latih. Hasil rendah bukan jaminan bebas diabetes, jadi tetap jaga pola hidup dan periksa berkala.") + '</p>' +
      '<p class="small">' + esc(r.disclaimer || "Hasil ini bukan diagnosis medis.") + '</p>';
    el.err.hidden = true; el.hasil.hidden = false;
    el.hasil.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  $("#form").addEventListener("submit", async e => {
    e.preventDefault();
    const pesan = validasi();
    if (pesan) return galat(pesan);

    const data = { Age: num(el.usia), Glucose: num(el.glukosa), BMI: hitungBMI() };
    if (num(el.hamil) !== null) data.Pregnancies = num(el.hamil);
    if (num(el.td) !== null) data.BloodPressure = num(el.td);

    el.btn.disabled = true; el.btn.textContent = "Menghitung...";
    const ctl = new AbortController(), timer = setTimeout(() => ctl.abort(), CONFIG.TIMEOUT_MS);
    try {
      const res = await fetch(CONFIG.API_URL, { method: "POST", headers: { "Content-Type": "application/json" },
                                                body: JSON.stringify(data), signal: ctl.signal });
      const json = await res.json();
      if (!res.ok) return galat(json.error || "Server menolak data yang dikirim.");
      tampilkan(json);
    } catch (err) {
      galat("Tidak dapat terhubung ke server prediksi. Pastikan API sudah berjalan (jalankan python app.py di folder ALGORITMA), lalu coba lagi.");
    } finally {
      clearTimeout(timer); el.btn.disabled = false; el.btn.textContent = "Hitung risiko";
    }
  });
})();
