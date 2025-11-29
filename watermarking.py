from PIL import Image, ImageDraw, ImageFont
import numpy as np


def add_visible_watermark(image, watermark_text, position='bottom-right', opacity=128, return_steps=False):
    steps = []

    # LANGKAH 1: Duplikasi gambar
    img = image.copy()
    width, height = img.size
    steps.append({
        'step': 1,
        'title': 'Duplikasi Gambar Asli',
        'description': 'Membuat salinan gambar untuk preserve gambar original',
        'detail': f'Ukuran gambar: {width} x {height} pixel\nMode: {img.mode}',
        'status': 'success'
    })

    # LANGKAH 2: Buat overlay transparan
    overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    steps.append({
        'step': 2,
        'title': 'Buat Layer Overlay Transparan',
        'description': 'Membuat layer RGBA transparan untuk menampung watermark',
        'detail': f'Layer RGBA dibuat dengan ukuran {width}x{height}\nAlpha channel = 0 (transparan penuh)',
        'status': 'success'
    })

    # LANGKAH 3: Konfigurasi font
    try:
        font_size = int(min(width, height) * 0.05)
        font = ImageFont.truetype("arial.ttf", font_size)
        font_info = f"Font: Arial\nSize: {font_size}px (5% dari dimensi terkecil)"
    except:
        font = ImageFont.load_default()
        font_info = "Font: Default system font"

    steps.append({
        'step': 3,
        'title': 'Konfigurasi Font',
        'description': 'Menentukan jenis dan ukuran font untuk watermark',
        'detail': font_info,
        'status': 'success'
    })

    # LANGKAH 4: Hitung posisi
    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    margin = 20
    positions = {
        'top-left': (margin, margin),
        'top-right': (width - text_width - margin, margin),
        'bottom-left': (margin, height - text_height - margin),
        'bottom-right': (width - text_width - margin, height - text_height - margin),
        'center': ((width - text_width) // 2, (height - text_height) // 2)
    }

    text_position = positions.get(position, positions['bottom-right'])
    # Hitung detail posisi untuk semua opsi
    all_positions = []
    for pos_name, pos_coord in positions.items():
        marker = " ← DIPILIH" if pos_name == position else ""
        all_positions.append(f"  {pos_name:15s} : {pos_coord}{marker}")

    positions_detail = '\n'.join(all_positions)

    steps.append({
        'step': 4,
        'title': 'Hitung Posisi Watermark',
        'description': 'Menentukan koordinat penempatan watermark pada gambar',
        'detail': f'Dimensi teks: {text_width} x {text_height} pixel\nMargin dari tepi: {margin}px\n\nPilihan posisi tersedia:\n{positions_detail}\n\nKoordinat final: {text_position}',
        'status': 'success'
    })

    # LANGKAH 5: Gambar teks
    draw.text(text_position, watermark_text, fill=(255, 255, 255, opacity), font=font)
    opacity_percent = (opacity / 255) * 100
    steps.append({
        'step': 5,
        'title': 'Gambar Teks Watermark',
        'description': 'Menggambar teks pada layer overlay dengan opacity',
        'detail': f'Teks: "{watermark_text}"\nWarna: Putih (RGB 255,255,255)\nOpacity: {opacity}/255 ({opacity_percent:.1f}%)',
        'status': 'success'
    })

    # LANGKAH 6: Alpha compositing
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # Ambil sample pixel SEBELUM compositing
    sample_x = text_position[0] + text_width // 2
    sample_y = text_position[1] + text_height // 2

    # Pastikan koordinat dalam bounds
    sample_x = min(max(sample_x, 0), width - 1)
    sample_y = min(max(sample_y, 0), height - 1)

    before_pixel = img.getpixel((sample_x, sample_y))
    overlay_pixel = overlay.getpixel((sample_x, sample_y))

    watermarked = Image.alpha_composite(img, overlay)

    # Ambil sample pixel SESUDAH compositing
    after_pixel = watermarked.getpixel((sample_x, sample_y))

    # Kalkulasi alpha blending dengan pixel REAL
    alpha_normalized = opacity / 255.0
    examples = []
    examples.append(f"Perhitungan REAL pada koordinat ({sample_x}, {sample_y}):")
    examples.append(f"")
    examples.append(f"SEBELUM (Background):")
    examples.append(f"  RGB({before_pixel[0]}, {before_pixel[1]}, {before_pixel[2]})")
    examples.append(f"")
    examples.append(f"WATERMARK (Foreground):")
    examples.append(f"  RGB(255, 255, 255) dengan alpha={opacity}/255 ({opacity_percent:.1f}%)")
    examples.append(f"")
    examples.append(f"RUMUS: Result = Foreground × α + Background × (1-α)")
    examples.append(f"")
    examples.append(f"  R = 255 × {alpha_normalized:.3f} + {before_pixel[0]} × {1-alpha_normalized:.3f}")
    examples.append(f"    = {255*alpha_normalized:.2f} + {before_pixel[0]*(1-alpha_normalized):.2f}")
    examples.append(f"    = {255*alpha_normalized + before_pixel[0]*(1-alpha_normalized):.2f}")
    examples.append(f"")
    examples.append(f"  G = 255 × {alpha_normalized:.3f} + {before_pixel[1]} × {1-alpha_normalized:.3f}")
    examples.append(f"    = {255*alpha_normalized:.2f} + {before_pixel[1]*(1-alpha_normalized):.2f}")
    examples.append(f"    = {255*alpha_normalized + before_pixel[1]*(1-alpha_normalized):.2f}")
    examples.append(f"")
    examples.append(f"  B = 255 × {alpha_normalized:.3f} + {before_pixel[2]} × {1-alpha_normalized:.3f}")
    examples.append(f"    = {255*alpha_normalized:.2f} + {before_pixel[2]*(1-alpha_normalized):.2f}")
    examples.append(f"    = {255*alpha_normalized + before_pixel[2]*(1-alpha_normalized):.2f}")
    examples.append(f"")
    examples.append(f"SESUDAH (Hasil Alpha Compositing):")
    examples.append(f"  Teoritis: RGB({int(255*alpha_normalized + before_pixel[0]*(1-alpha_normalized))}, {int(255*alpha_normalized + before_pixel[1]*(1-alpha_normalized))}, {int(255*alpha_normalized + before_pixel[2]*(1-alpha_normalized))})")
    examples.append(f"  Aktual:   RGB({after_pixel[0]}, {after_pixel[1]}, {after_pixel[2]})")
    examples.append(f"")
    examples.append(f"Perubahan nilai:")
    examples.append(f"  ΔR = {after_pixel[0]} - {before_pixel[0]} = {after_pixel[0] - before_pixel[0]:+d}")
    examples.append(f"  ΔG = {after_pixel[1]} - {before_pixel[1]} = {after_pixel[1] - before_pixel[1]:+d}")
    examples.append(f"  ΔB = {after_pixel[2]} - {before_pixel[2]} = {after_pixel[2] - before_pixel[2]:+d}")

    example_text = '\n'.join(examples)

    steps.append({
        'step': 6,
        'title': 'Alpha Compositing',
        'description': 'Menggabungkan layer overlay dengan gambar base',
        'detail': f'Formula per pixel: Result = Foreground × α + Background × (1-α)\n\n{example_text}\n\nLayer overlay berhasil digabungkan dengan gambar base',
        'status': 'success'
    })

    # LANGKAH 7: Konversi ke RGB
    result = watermarked.convert('RGB')
    steps.append({
        'step': 7,
        'title': 'Konversi ke RGB',
        'description': 'Mengkonversi hasil dari RGBA ke RGB untuk kompatibilitas',
        'detail': f'Mode: RGBA → RGB\nGambar siap disimpan (size: {result.size})',
        'status': 'success'
    })

    if return_steps:
        return result, steps
    return result


def add_visible_watermark_image(base_image, watermark_image, position='bottom-right',
                                 opacity=128, scale=0.2, return_steps=False):
    steps = []

    # LANGKAH 1: Duplikasi gambar base
    img = base_image.copy()
    width, height = img.size
    steps.append({
        'step': 1,
        'title': 'Duplikasi Gambar Base',
        'description': 'Membuat salinan gambar utama',
        'detail': f'Ukuran gambar: {width} x {height} pixel\nMode: {img.mode}',
        'status': 'success'
    })

    # LANGKAH 2-3: Resize logo
    wm_width = int(width * scale)
    watermark = watermark_image.copy()
    wm_aspect = watermark.width / watermark.height
    wm_height = int(wm_width / wm_aspect)
    watermark = watermark.resize((wm_width, wm_height), Image.Resampling.LANCZOS)

    scale_percent = scale * 100
    steps.append({
        'step': 2,
        'title': 'Resize Logo dengan Aspect Ratio',
        'description': 'Mengubah ukuran logo berdasarkan skala yang dipilih',
        'detail': f'Ukuran original: {watermark_image.width} x {watermark_image.height}\nSkala: {scale_percent:.0f}% dari lebar gambar base\nUkuran baru: {wm_width} x {wm_height}\nAspect ratio: {wm_aspect:.2f}',
        'status': 'success'
    })

    # LANGKAH 4: Konversi ke RGBA
    if watermark.mode != 'RGBA':
        watermark = watermark.convert('RGBA')

    steps.append({
        'step': 3,
        'title': 'Konversi Logo ke RGBA',
        'description': 'Memastikan logo memiliki alpha channel untuk transparansi',
        'detail': f'Mode logo: {watermark.mode}\nAlpha channel siap untuk opacity adjustment',
        'status': 'success'
    })

    # LANGKAH 5: Sesuaikan opacity
    alpha = watermark.split()[3]
    alpha = alpha.point(lambda p: int(p * (opacity / 255.0)))
    watermark.putalpha(alpha)

    opacity_percent = (opacity / 255) * 100
    steps.append({
        'step': 4,
        'title': 'Sesuaikan Opacity Logo',
        'description': 'Mengalikan alpha channel dengan faktor opacity',
        'detail': f'Opacity: {opacity}/255 ({opacity_percent:.1f}%)\nFormula: new_alpha = original_alpha × ({opacity}/255)',
        'status': 'success'
    })

    # LANGKAH 6: Hitung posisi
    margin = 20
    positions = {
        'top-left': (margin, margin),
        'top-right': (width - wm_width - margin, margin),
        'bottom-left': (margin, height - wm_height - margin),
        'bottom-right': (width - wm_width - margin, height - wm_height - margin),
        'center': ((width - wm_width) // 2, (height - wm_height) // 2)
    }

    paste_position = positions.get(position, positions['bottom-right'])
    # Hitung detail posisi untuk semua opsi
    all_logo_positions = []
    for pos_name, pos_coord in positions.items():
        marker = " ← DIPILIH" if pos_name == position else ""
        all_logo_positions.append(f"  {pos_name:15s} : {pos_coord}{marker}")

    logo_positions_detail = '\n'.join(all_logo_positions)

    steps.append({
        'step': 5,
        'title': 'Hitung Posisi Paste',
        'description': 'Menentukan koordinat penempatan logo pada gambar',
        'detail': f'Ukuran logo setelah resize: {wm_width} x {wm_height} pixel\nMargin dari tepi: {margin}px\n\nPilihan posisi tersedia:\n{logo_positions_detail}\n\nKoordinat final: {paste_position}',
        'status': 'success'
    })

    # LANGKAH 7-8: Paste logo
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # Ambil sample pixel SEBELUM paste (di tengah area logo)
    sample_logo_x = paste_position[0] + wm_width // 2
    sample_logo_y = paste_position[1] + wm_height // 2

    # Pastikan koordinat dalam bounds
    sample_logo_x = min(max(sample_logo_x, 0), width - 1)
    sample_logo_y = min(max(sample_logo_y, 0), height - 1)

    before_logo_pixel = img.getpixel((sample_logo_x, sample_logo_y))

    # Ambil pixel logo pada posisi yang sama (koordinat relatif)
    logo_sample_x = sample_logo_x - paste_position[0]
    logo_sample_y = sample_logo_y - paste_position[1]
    logo_pixel = watermark.getpixel((logo_sample_x, logo_sample_y))

    img.paste(watermark, paste_position, watermark)

    # Ambil sample pixel SESUDAH paste
    after_logo_pixel = img.getpixel((sample_logo_x, sample_logo_y))

    # Kalkulasi alpha blending dengan pixel REAL dari logo
    logo_alpha = logo_pixel[3] if len(logo_pixel) == 4 else 255
    alpha_normalized = logo_alpha / 255.0

    logo_examples = []
    logo_examples.append(f"Perhitungan REAL pada koordinat ({sample_logo_x}, {sample_logo_y}):")
    logo_examples.append(f"")
    logo_examples.append(f"SEBELUM (Background):")
    logo_examples.append(f"  RGB({before_logo_pixel[0]}, {before_logo_pixel[1]}, {before_logo_pixel[2]})")
    logo_examples.append(f"")
    logo_examples.append(f"LOGO (Foreground):")
    logo_examples.append(f"  RGBA({logo_pixel[0]}, {logo_pixel[1]}, {logo_pixel[2]}, {logo_alpha})")
    logo_examples.append(f"  Opacity setting: {opacity}/255 ({opacity_percent:.1f}%)")
    logo_examples.append(f"  Alpha efektif: {logo_alpha}/255 ({logo_alpha/255*100:.1f}%)")
    logo_examples.append(f"")
    logo_examples.append(f"RUMUS: Result = Logo × α + Background × (1-α)")
    logo_examples.append(f"")
    logo_examples.append(f"  R = {logo_pixel[0]} × {alpha_normalized:.3f} + {before_logo_pixel[0]} × {1-alpha_normalized:.3f}")
    logo_examples.append(f"    = {logo_pixel[0]*alpha_normalized:.2f} + {before_logo_pixel[0]*(1-alpha_normalized):.2f}")
    logo_examples.append(f"    = {logo_pixel[0]*alpha_normalized + before_logo_pixel[0]*(1-alpha_normalized):.2f}")
    logo_examples.append(f"")
    logo_examples.append(f"  G = {logo_pixel[1]} × {alpha_normalized:.3f} + {before_logo_pixel[1]} × {1-alpha_normalized:.3f}")
    logo_examples.append(f"    = {logo_pixel[1]*alpha_normalized:.2f} + {before_logo_pixel[1]*(1-alpha_normalized):.2f}")
    logo_examples.append(f"    = {logo_pixel[1]*alpha_normalized + before_logo_pixel[1]*(1-alpha_normalized):.2f}")
    logo_examples.append(f"")
    logo_examples.append(f"  B = {logo_pixel[2]} × {alpha_normalized:.3f} + {before_logo_pixel[2]} × {1-alpha_normalized:.3f}")
    logo_examples.append(f"    = {logo_pixel[2]*alpha_normalized:.2f} + {before_logo_pixel[2]*(1-alpha_normalized):.2f}")
    logo_examples.append(f"    = {logo_pixel[2]*alpha_normalized + before_logo_pixel[2]*(1-alpha_normalized):.2f}")
    logo_examples.append(f"")
    logo_examples.append(f"SESUDAH (Hasil Alpha Blending):")
    logo_examples.append(f"  Teoritis: RGB({int(logo_pixel[0]*alpha_normalized + before_logo_pixel[0]*(1-alpha_normalized))}, {int(logo_pixel[1]*alpha_normalized + before_logo_pixel[1]*(1-alpha_normalized))}, {int(logo_pixel[2]*alpha_normalized + before_logo_pixel[2]*(1-alpha_normalized))})")
    logo_examples.append(f"  Aktual:   RGB({after_logo_pixel[0]}, {after_logo_pixel[1]}, {after_logo_pixel[2]})")
    logo_examples.append(f"")
    logo_examples.append(f"Perubahan nilai:")
    logo_examples.append(f"  ΔR = {after_logo_pixel[0]} - {before_logo_pixel[0]} = {after_logo_pixel[0] - before_logo_pixel[0]:+d}")
    logo_examples.append(f"  ΔG = {after_logo_pixel[1]} - {before_logo_pixel[1]} = {after_logo_pixel[1] - before_logo_pixel[1]:+d}")
    logo_examples.append(f"  ΔB = {after_logo_pixel[2]} - {before_logo_pixel[2]} = {after_logo_pixel[2] - before_logo_pixel[2]:+d}")
    logo_examples.append(f"")
    logo_examples.append(f"Catatan:")
    logo_examples.append(f"  - Pixel logo dengan alpha=0 (transparan) → background tetap terlihat")
    logo_examples.append(f"  - Pixel logo dengan alpha=255 (opaque) → logo sepenuhnya terlihat")
    logo_examples.append(f"  - Nilai alpha menengah → blending antara logo dan background")

    logo_example_text = '\n'.join(logo_examples)

    steps.append({
        'step': 6,
        'title': 'Paste Logo dengan Alpha Blending',
        'description': 'Menempelkan logo pada gambar menggunakan alpha channel sebagai mask',
        'detail': f'Logo di-paste pada koordinat {paste_position}\nUkuran area: {wm_width} x {wm_height} pixel\n\n{logo_example_text}',
        'status': 'success'
    })

    # LANGKAH 9: Konversi ke RGB
    result = img.convert('RGB')
    steps.append({
        'step': 7,
        'title': 'Konversi ke RGB',
        'description': 'Mengkonversi hasil dari RGBA ke RGB untuk kompatibilitas',
        'detail': f'Mode: RGBA → RGB\nGambar siap disimpan (size: {result.size})',
        'status': 'success'
    })

    if return_steps:
        return result, steps
    return result


def add_invisible_watermark(image, watermark_text):
    print(f"[WATERMARK INVISIBLE] Menambahkan watermark: '{watermark_text}'")

    # Import fungsi dari modul steganography
    from steganography import encode_message_lsb

    # Tambahkan prefix "WM:" untuk identifikasi watermark
    watermark_with_prefix = f"WM:{watermark_text}"
    print(f"[WATERMARK INVISIBLE] Dengan prefix: '{watermark_with_prefix}'")

    # Gunakan metode LSB steganography untuk encoding
    watermarked_image = encode_message_lsb(image, watermark_with_prefix)

    print("[WATERMARK INVISIBLE] Watermark berhasil disembunyikan")
    return watermarked_image


def extract_invisible_watermark(image):
    print("[WATERMARK INVISIBLE] Mengekstrak watermark dari gambar...")

    # Import fungsi dari modul steganography
    from steganography import decode_message_lsb

    # Decode pesan menggunakan LSB steganography
    message = decode_message_lsb(image)

    # Verifikasi apakah ada prefix "WM:"
    if message.startswith("WM:"):
        watermark = message[3:]  # Hapus prefix "WM:"
        print(f"[WATERMARK INVISIBLE] Watermark ditemukan: '{watermark}'")
        return watermark
    else:
        print("[WATERMARK INVISIBLE] Tidak ditemukan watermark (prefix 'WM:' tidak ada)")
        return "No watermark found"


def compare_images(original, watermarked):
    # Konversi ke array
    orig_array = np.array(original)
    wm_array = np.array(watermarked)

    # Hitung MSE (Mean Squared Error)
    mse = np.mean((orig_array.astype(float) - wm_array.astype(float)) ** 2)

    # Hitung PSNR (Peak Signal-to-Noise Ratio)
    # PSNR tinggi = kualitas bagus (minimal perubahan)
    if mse == 0:
        psnr = float('inf')
    else:
        max_pixel = 255.0
        psnr = 20 * np.log10(max_pixel / np.sqrt(mse))

    # Hitung persentase pixel yang berbeda
    diff_pixels = np.sum(orig_array != wm_array)
    total_pixels = orig_array.size
    diff_percentage = (diff_pixels / total_pixels) * 100

    return {
        'mse': mse,
        'psnr': psnr,
        'diff_pixels': diff_pixels,
        'total_pixels': total_pixels,
        'diff_percentage': diff_percentage
    }
