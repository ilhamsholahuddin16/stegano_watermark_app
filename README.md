# 📁 STRUKTUR MODUL PROJECT

## 🎯 Pemisahan Modul

Project ini telah direfactor untuk memisahkan kode berdasarkan fungsinya:

### 📂 Struktur File

```
citra_digital/
│
├── 🌐 app.py                     # Flask Web Application
│   └─ Routing dan HTTP handlers
│
├── 🔐 steganography.py           # Modul Steganografi
│   ├─ encode_message_lsb()       # Encode pesan ke gambar
│   ├─ decode_message_lsb()       # Decode pesan dari gambar
│   └─ get_max_message_size()    # Hitung kapasitas gambar
│
├── 🏷️  watermarking.py           # Modul Watermarking
│   ├─ add_visible_watermark()            # Watermark teks
│   ├─ add_visible_watermark_image()     # Watermark logo
│   ├─ add_invisible_watermark()         # Watermark invisible
│   ├─ extract_invisible_watermark()     # Ekstrak invisible watermark
│   └─ compare_images()                   # Analisis perbandingan gambar
│
├── 📚 DOCUMENTATION.md           # Dokumentasi lengkap
│   └─ Penjelasan detail cara kerja setiap metode
│
├── 📋 MODULE_STRUCTURE.md        # File ini
│
├── templates/
│   └── 🎨 index.html            # Interface web
│
└── static/
    └── js/
        └── ⚡ app.js            # JavaScript frontend
```

---

## 🔄 Alur Kerja Aplikasi

### 1️⃣ **STEGANOGRAFI**

```
┌─────────────┐
│   User      │
│ Upload img  │
│ + message   │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────────┐
│   app.py    │────▶│ steganography.py │
│ /stego/     │     │                  │
│  encode     │     │ encode_message_  │
└─────────────┘     │     lsb()        │
       ▲            └──────────────────┘
       │                     │
       │                     │ Processing:
       │                     ├─ Convert to array
       │                     ├─ Message → binary
       │                     ├─ Modify LSB
       │                     └─ Add delimiter
       │
       ▼
┌─────────────┐
│  Response   │
│ Stego Image │
└─────────────┘
```

### 2️⃣ **WATERMARKING**

```
┌─────────────┐
│   User      │
│ Upload img  │
│ + watermark │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────────┐
│   app.py    │────▶│ watermarking.py  │
│ /watermark/ │     │                  │
│  visible    │     │ add_visible_     │
└─────────────┘     │  watermark()     │
       ▲            └──────────────────┘
       │                     │
       │                     │ Processing:
       │                     ├─ Create overlay
       │                     ├─ Draw text/logo
       │                     ├─ Alpha composite
       │                     └─ Convert to RGB
       │
       ▼
┌─────────────┐
│  Response   │
│ Watermarked │
└─────────────┘
```

---

## 🔍 Detail Modul

### 📄 app.py

**Fungsi:** Web Server dan Routing

**Endpoints:**

| Route | Method | Fungsi |
|-------|--------|--------|
| `/` | GET | Halaman utama |
| `/steganography/encode` | POST | Encode pesan LSB |
| `/steganography/decode` | POST | Decode pesan LSB |
| `/watermark/visible` | POST | Tambah watermark teks |
| `/watermark/image` | POST | Tambah watermark logo |
| `/watermark/invisible/add` | POST | Tambah watermark invisible |
| `/watermark/invisible/extract` | POST | Ekstrak watermark invisible |

**Import:**
```python
from steganography import (
    encode_message_lsb,
    decode_message_lsb,
    get_max_message_size
)

from watermarking import (
    add_visible_watermark,
    add_visible_watermark_image,
    add_invisible_watermark,
    extract_invisible_watermark,
    compare_images
)
```

---

### 📄 steganography.py

**Fungsi:** Implementasi LSB Steganography

**Functions:**

#### `encode_message_lsb(image, message)`
- **Input:** PIL Image, string message
- **Output:** PIL Image (stego)
- **Proses:**
  1. Convert image → NumPy array
  2. Convert message → binary string
  3. Modify LSB of pixels
  4. Add delimiter
  5. Reshape → image

#### `decode_message_lsb(image)`
- **Input:** PIL Image (stego)
- **Output:** string message
- **Proses:**
  1. Convert image → NumPy array
  2. Extract LSB from pixels
  3. Find delimiter
  4. Convert binary → text

#### `get_max_message_size(image)`
- **Input:** PIL Image
- **Output:** dict dengan info kapasitas
- **Info:** max_bits, max_bytes, max_chars, dimensions

**Dependencies:**
```python
from PIL import Image
import numpy as np
```

---

### 📄 watermarking.py

**Fungsi:** Implementasi berbagai metode Watermarking

**Functions:**

#### `add_visible_watermark(image, text, position, opacity)`
- **Input:** PIL Image, watermark text, position, opacity
- **Output:** PIL Image (watermarked)
- **Proses:**
  1. Create RGBA overlay
  2. Configure font
  3. Calculate position
  4. Draw text on overlay
  5. Alpha composite
  6. Convert to RGB

#### `add_visible_watermark_image(base, logo, position, opacity, scale)`
- **Input:** PIL Image (base), PIL Image (logo), position, opacity, scale
- **Output:** PIL Image (watermarked)
- **Proses:**
  1. Resize logo with aspect ratio
  2. Convert to RGBA
  3. Adjust opacity
  4. Calculate position
  5. Paste with alpha blending
  6. Convert to RGB

#### `add_invisible_watermark(image, text)`
- **Input:** PIL Image, watermark text
- **Output:** PIL Image (watermarked)
- **Proses:**
  1. Add "WM:" prefix
  2. Call encode_message_lsb()
  3. Return stego image

#### `extract_invisible_watermark(image)`
- **Input:** PIL Image
- **Output:** string watermark
- **Proses:**
  1. Call decode_message_lsb()
  2. Check "WM:" prefix
  3. Return watermark or "No watermark found"

#### `compare_images(original, watermarked)`
- **Input:** PIL Image (original), PIL Image (watermarked)
- **Output:** dict dengan statistik
- **Metrics:** MSE, PSNR, diff_pixels, diff_percentage

**Dependencies:**
```python
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from steganography import encode_message_lsb, decode_message_lsb
```

---

## 💡 Keuntungan Pemisahan Modul

### ✅ **Separation of Concerns**
- Setiap modul memiliki tanggung jawab spesifik
- app.py → Routing & HTTP
- steganography.py → LSB operations
- watermarking.py → Watermark operations

### ✅ **Reusability**
```python
# Modul bisa digunakan independently
from steganography import encode_message_lsb
from PIL import Image

img = Image.open('test.png')
stego = encode_message_lsb(img, "Secret message")
stego.save('stego.png')
```

### ✅ **Maintainability**
- Mudah menemukan dan memperbaiki bug
- Setiap modul bisa ditest secara terpisah
- Perubahan di satu modul tidak affect modul lain

### ✅ **Readability**
- Kode lebih terorganisir dan mudah dibaca
- Dokumentasi lengkap di setiap fungsi
- Jelas fungsi mana yang melakukan apa

### ✅ **Scalability**
- Mudah menambah metode baru
- Bisa menambah modul lain (e.g., encryption.py)
- Tidak membuat file menjadi terlalu besar

---

## 🧪 Testing Modul

### Test Steganography
```python
from PIL import Image
from steganography import encode_message_lsb, decode_message_lsb

# Test encode
img = Image.open('test.png')
message = "Hello, this is a secret message!"
stego = encode_message_lsb(img, message)
stego.save('stego_test.png')

# Test decode
stego_loaded = Image.open('stego_test.png')
decoded = decode_message_lsb(stego_loaded)
print(f"Decoded: {decoded}")

# Verify
assert decoded == message, "Message mismatch!"
print("✓ Steganography test passed")
```

### Test Watermarking
```python
from PIL import Image
from watermarking import add_visible_watermark, add_invisible_watermark, extract_invisible_watermark

# Test visible watermark
img = Image.open('test.jpg')
watermarked = add_visible_watermark(img, "© 2024 Test", opacity=150)
watermarked.save('watermarked_test.jpg')
print("✓ Visible watermark test passed")

# Test invisible watermark
img = Image.open('test.png')
wm_img = add_invisible_watermark(img, "Copyright 2024")
wm_img.save('invisible_wm_test.png')

# Extract and verify
extracted = extract_invisible_watermark(wm_img)
assert extracted == "Copyright 2024", "Watermark mismatch!"
print("✓ Invisible watermark test passed")
```

---

## 📊 Dependencies

**Required Libraries:**
```
Flask>=2.0.0
Pillow>=9.0.0
numpy>=1.20.0
```

**Install:**
```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
Flask==2.3.0
Pillow==10.0.0
numpy==1.24.0
```

---

## 🚀 Running the Application

### Development Mode
```bash
# Windows
python app.py

# Linux/Mac
python3 app.py
```
