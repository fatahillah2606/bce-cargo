# Bahtera Cahaya Express

Proyek ini adalah aplikasi web berbasis **Python Flask** dengan integrasi **Flowbite** untuk styling.

---

## Requirements

Pastikan Anda telah menginstal:

- Python 3.8+
- Node.js & npm
- Git (untuk clone repositori)

---

## Langkah-Langkah Instalasi

### 1. Clone Repository

```bash
git clone https://github.com/fatahillah2606/bce-cargo.git
cd bce-cargo
```

### 2. Buat dan Aktifkan Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # untuk Linux/macOS
.venv\Scripts\activate     # untuk Windows
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Jika terjadi kesalahan dalam menginstall dependencies, jalankan perintah ini

```bash
pip install flask bcrypt "pymongo[srv]" flask-session dotenv requests pytz
```

### 4. Install Node.js Dependencies

```bash
npm install
```

### 5. Buat File ```.env``` dari Template

Salin file ```.env.example``` menjadi ```.env```:

```bash
cp .env.example .env  # Linux/macOS
copy .env.example .env  # Windows (CMD)
```

Lalu, sesuaikan nilai-nilai di dalam ```.env``` sesuai dengan konfigurasi lokal Anda.

---

## Menjalankan Tailwind CSS

Untuk memproses file Tailwind CSS secara otomatis:

```bash
npx @tailwindcss/cli -i ./static/src/input.css -o ./static/dist/output.css --watch
```

Perintah ini akan memantau perubahan dan membangun ulang file CSS ke dalam direktori ```static/dist```.

---

## Menjalankan Aplikasi Flask

Aktifkan virtual environment lalu jalankan server:

```bash
flask run --debug
```

Aplikasi akan tersedia di http://127.0.0.1:5000.

> Made with ❤️ by BCE Team