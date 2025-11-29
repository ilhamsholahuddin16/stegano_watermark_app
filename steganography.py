from PIL import Image
import numpy as np


def encode_message_lsb(image, message, return_steps=False):
    steps = []

    # LANGKAH 1: Konversi gambar ke array NumPy
    img_array = np.array(image)
    steps.append({
        'step': 1,
        'title': 'Konversi Gambar ke Array NumPy',
        'description': f'Gambar dikonversi menjadi array berisi nilai pixel (0-255)',
        'detail': f'Dimensi gambar: {img_array.shape} → Total {img_array.size} nilai pixel',
        'status': 'success'
    })

    # LANGKAH 2: Konversi pesan ke binary
    binary_message = ''.join([format(ord(char), '08b') for char in message])

    # Contoh untuk 10 karakter pertama (atau semua jika kurang dari 10)
    num_samples = min(10, len(message))
    sample_chars = message[:num_samples]
    sample_conversions = []
    for char in sample_chars:
        sample_conversions.append(f"'{char}' = ASCII {ord(char):3d} = {format(ord(char), '08b')}")

    sample_text = '\n'.join(sample_conversions)
    more_text = f"\n...dan {len(message) - num_samples} karakter lainnya" if len(message) > num_samples else ""

    steps.append({
        'step': 2,
        'title': 'Konversi Pesan ke Binary',
        'description': f'Setiap karakter dikonversi: ASCII → Binary 8-bit',
        'detail': f'Panjang pesan: {len(message)} karakter\n\nKonversi karakter:\n{sample_text}{more_text}\n\nTotal bit: {len(binary_message)}',
        'status': 'success'
    })

    # LANGKAH 3: Tambahkan delimiter
    binary_message += '1111111111111110'
    message_length = len(binary_message)

    steps.append({
        'step': 3,
        'title': 'Tambahkan Delimiter',
        'description': 'Menambahkan penanda akhir pesan (1111111111111110)',
        'detail': f'Panjang total dengan delimiter: {message_length} bit (termasuk 16 bit delimiter)',
        'status': 'success'
    })

    # LANGKAH 4: Flatten array
    img_flat = img_array.flatten()

    # LANGKAH 5: Validasi kapasitas
    if message_length > len(img_flat):
        steps.append({
            'step': 4,
            'title': 'Validasi Kapasitas',
            'description': 'Memeriksa apakah gambar cukup untuk menyimpan pesan',
            'detail': f'GAGAL! Pesan memerlukan {message_length} bit, tapi hanya tersedia {len(img_flat)} bit',
            'status': 'error'
        })
        raise ValueError(
            f"Pesan terlalu panjang! Maksimal {len(img_flat)} bit, "
            f"pesan memerlukan {message_length} bit"
        )

    capacity_percent = (message_length / len(img_flat)) * 100
    steps.append({
        'step': 4,
        'title': 'Validasi Kapasitas',
        'description': 'Memeriksa apakah gambar cukup untuk menyimpan pesan',
        'detail': f'Kapasitas tersedia: {len(img_flat)} bit\nDibutuhkan: {message_length} bit\nPenggunaan: {capacity_percent:.2f}%',
        'status': 'success'
    })

    # LANGKAH 6: Embed pesan ke LSB
    modified_count = 0
    sample_modifications = []
    num_samples = min(15, message_length)  # Tampilkan 15 contoh

    for i in range(message_length):
        original_value = img_flat[i]
        img_flat[i] = (img_flat[i] & 0xFE) | int(binary_message[i])

        if img_flat[i] != original_value:
            modified_count += 1

        # Simpan 15 contoh modifikasi pertama
        if len(sample_modifications) < num_samples:
            change_marker = "✓ CHANGED" if img_flat[i] != original_value else "  (same)"
            sample_modifications.append(
                f"Pixel {i:4d}: {original_value:3d} ({format(original_value, '08b')}) → "
                f"{img_flat[i]:3d} ({format(img_flat[i], '08b')}) [bit={binary_message[i]}] {change_marker}"
            )

    modification_percent = (modified_count / message_length) * 100
    sample_text = '\n'.join(sample_modifications)
    more_text = f"\n...dan {message_length - num_samples} pixel lainnya" if message_length > num_samples else ""

    steps.append({
        'step': 5,
        'title': 'Modifikasi LSB Pixel',
        'description': 'Menyisipkan bit pesan ke bit terakhir (LSB) setiap pixel',
        'detail': f'Total pixel diproses: {message_length}\nPixel yang berubah: {modified_count} ({modification_percent:.1f}%)\nPixel yang sama: {message_length - modified_count} ({100 - modification_percent:.1f}%)\n\nContoh modifikasi ({num_samples} pixel pertama):\n{sample_text}{more_text}',
        'status': 'success'
    })

    # LANGKAH 7: Reshape array
    stego_array = img_flat.reshape(img_array.shape)
    steps.append({
        'step': 6,
        'title': 'Reshape Array ke Bentuk Gambar',
        'description': 'Mengembalikan array yang sudah dimodifikasi ke bentuk gambar asli',
        'detail': f'Array flat → Gambar {img_array.shape}',
        'status': 'success'
    })

    # LANGKAH 8: Konversi ke PIL Image
    stego_image = Image.fromarray(stego_array.astype('uint8'))
    steps.append({
        'step': 7,
        'title': 'Konversi ke Format Gambar',
        'description': 'Array NumPy dikonversi kembali ke format PIL Image',
        'detail': f'Gambar stego siap disimpan (format: {stego_image.mode}, size: {stego_image.size})',
        'status': 'success'
    })

    if return_steps:
        return stego_image, steps
    return stego_image


def decode_message_lsb(image, return_steps=False):
    steps = []

    # LANGKAH 1: Konversi gambar ke array NumPy
    img_array = np.array(image)
    steps.append({
        'step': 1,
        'title': 'Baca Gambar Stego',
        'description': 'Gambar yang berisi pesan tersembunyi dikonversi ke array NumPy',
        'detail': f'Dimensi gambar: {img_array.shape}\nTotal pixel values: {img_array.size}',
        'status': 'success'
    })

    # LANGKAH 2: Flatten array
    img_flat = img_array.flatten()
    steps.append({
        'step': 2,
        'title': 'Flatten Array',
        'description': 'Array gambar diratakan untuk memudahkan ekstraksi LSB',
        'detail': f'Array {img_array.shape} → Array 1D dengan {len(img_flat)} elemen',
        'status': 'success'
    })

    # LANGKAH 3: Ekstrak LSB dari setiap pixel
    binary_message = ''
    sample_extractions = []
    num_samples = 15  # Tampilkan 15 contoh

    for i, pixel in enumerate(img_flat):
        lsb = pixel & 1
        binary_message += str(lsb)

        # Simpan 15 contoh ekstraksi pertama
        if len(sample_extractions) < num_samples:
            sample_extractions.append(
                f"Pixel {i:4d}: nilai={pixel:3d} ({format(pixel, '08b')}) → LSB = {lsb}"
            )

    sample_text = '\n'.join(sample_extractions)
    more_text = f"\n...dan {len(img_flat) - num_samples} pixel lainnya"

    steps.append({
        'step': 3,
        'title': 'Ekstrak LSB dari Setiap Pixel',
        'description': 'Mengambil bit terakhir (LSB) dari setiap nilai pixel',
        'detail': f'Total bit diekstrak: {len(binary_message):,}\n\nContoh ekstraksi ({num_samples} pixel pertama):\n{sample_text}{more_text}',
        'status': 'success'
    })

    # LANGKAH 4: Cari delimiter
    delimiter = '1111111111111110'
    delimiter_index = binary_message.find(delimiter)

    if delimiter_index == -1:
        steps.append({
            'step': 4,
            'title': 'Cari Delimiter',
            'description': 'Mencari pola delimiter (1111111111111110)',
            'detail': 'Delimiter tidak ditemukan - Gambar tidak berisi pesan tersembunyi',
            'status': 'error'
        })
        if return_steps:
            return "No hidden message found", steps
        return "No hidden message found"

    steps.append({
        'step': 4,
        'title': 'Cari Delimiter',
        'description': 'Mencari pola delimiter (1111111111111110)',
        'detail': f'Delimiter ditemukan pada posisi bit ke-{delimiter_index}\nPanjang pesan (tanpa delimiter): {delimiter_index} bit',
        'status': 'success'
    })

    # LANGKAH 5: Ambil bagian pesan
    binary_message = binary_message[:delimiter_index]
    num_chars = delimiter_index // 8

    steps.append({
        'step': 5,
        'title': 'Isolasi Pesan Binary',
        'description': 'Mengambil bit sebelum delimiter sebagai pesan',
        'detail': f'Panjang pesan binary: {delimiter_index} bit\nJumlah karakter: {num_chars} karakter (setiap karakter = 8 bit)',
        'status': 'success'
    })

    # LANGKAH 6: Konversi binary ke text
    message = ''
    sample_conversions = []
    num_samples = min(10, len(binary_message) // 8)  # Tampilkan 10 karakter

    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i+8]
        if len(byte) == 8:
            char_code = int(byte, 2)
            char = chr(char_code)
            message += char

            # Simpan 10 contoh konversi pertama
            if len(sample_conversions) < num_samples:
                display_char = char if char.isprintable() else f'[{char_code}]'
                sample_conversions.append(
                    f"{byte} → ASCII {char_code:3d} → '{display_char}'"
                )

    sample_conv_text = '\n'.join(sample_conversions)
    more_text = f"\n...dan {len(message) - num_samples} karakter lainnya" if len(message) > num_samples else ""

    # Tampilkan pesan (batasi jika terlalu panjang)
    message_preview = message if len(message) <= 100 else message[:100] + "..."

    steps.append({
        'step': 6,
        'title': 'Konversi Binary ke Text',
        'description': 'Mengkonversi setiap 8 bit binary ke karakter ASCII',
        'detail': f'Berhasil mendekode: {len(message)} karakter\n\nContoh konversi ({num_samples} karakter pertama):\n{sample_conv_text}{more_text}\n\nPesan: "{message_preview}"',
        'status': 'success'
    })

    if return_steps:
        return message, steps
    return message


def get_max_message_size(image):
    img_array = np.array(image)
    total_pixels = img_array.size

    # Setiap pixel bisa menyimpan 1 bit
    # Dikurangi 16 bit untuk delimiter
    max_bits = total_pixels - 16
    max_bytes = max_bits // 8
    max_chars = max_bytes

    return {
        'max_bits': max_bits,
        'max_bytes': max_bytes,
        'max_chars': max_chars,
        'image_dimensions': img_array.shape,
        'total_pixels': total_pixels
    }
