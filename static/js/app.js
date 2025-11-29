// Tab switching functionality
function switchTab(tabName) {
    // Determine which section this tab belongs to
    const isStegoTab = tabName.startsWith('stego-');
    const isWatermarkTab = tabName.startsWith('watermark-');

    if (isStegoTab) {
        // Hide all stego tab contents
        document.querySelectorAll('#stego-encode, #stego-decode').forEach(content => {
            content.classList.remove('active');
        });

        // Remove active class from stego buttons
        const stegoButtons = document.querySelectorAll('.stego-tab');
        stegoButtons.forEach(button => {
            button.classList.remove('active', 'border-purple-600', 'text-purple-600');
            button.classList.add('border-transparent');
        });

        // Show selected tab
        document.getElementById(tabName).classList.add('active');

        // Add active class to clicked button
        const activeButton = document.querySelector(`.stego-tab[data-tab="${tabName}"]`);
        activeButton.classList.add('active', 'border-purple-600', 'text-purple-600');
        activeButton.classList.remove('border-transparent');

    } else if (isWatermarkTab) {
        // Hide all watermark tab contents
        document.querySelectorAll('#watermark-visible, #watermark-image, #watermark-invisible').forEach(content => {
            content.classList.remove('active');
        });

        // Remove active class from watermark buttons
        const watermarkButtons = document.querySelectorAll('.watermark-tab');
        watermarkButtons.forEach(button => {
            button.classList.remove('active', 'border-indigo-600', 'text-indigo-600');
            button.classList.add('border-transparent');
        });

        // Show selected tab
        document.getElementById(tabName).classList.add('active');

        // Add active class to clicked button
        const activeButton = document.querySelector(`.watermark-tab[data-tab="${tabName}"]`);
        activeButton.classList.add('active', 'border-indigo-600', 'text-indigo-600');
        activeButton.classList.remove('border-transparent');
    }
}

// Toggle info box functionality
function toggleInfo(infoId) {
    const infoContent = document.getElementById(infoId);
    const icon = document.getElementById(infoId + '-icon');

    if (infoContent.classList.contains('show')) {
        infoContent.classList.remove('show');
        icon.classList.remove('fa-chevron-up');
        icon.classList.add('fa-chevron-down');
    } else {
        infoContent.classList.add('show');
        icon.classList.remove('fa-chevron-down');
        icon.classList.add('fa-chevron-up');
    }
}

// Image preview functionality
function setupImagePreview(inputId, previewId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);

    input.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                preview.innerHTML = `
                    <div class="border rounded-lg p-4 bg-gray-50">
                        <p class="text-sm text-gray-600 mb-2">Preview:</p>
                        <img src="${event.target.result}" alt="Preview" class="preview-image mx-auto rounded">
                    </div>
                `;
            };
            reader.readAsDataURL(file);
        }
    });
}

// Setup all image previews
setupImagePreview('stegoEncodeImage', 'stegoEncodePreview');
setupImagePreview('stegoDecodeImage', 'stegoDecodePreview');
setupImagePreview('watermarkVisibleImage', 'watermarkVisiblePreview');
setupImagePreview('watermarkImageBase', 'watermarkImageBasePreview');
setupImagePreview('watermarkImageLogo', 'watermarkImageLogoPreview');
setupImagePreview('watermarkInvisibleImage', 'watermarkInvisiblePreview');
setupImagePreview('watermarkInvisibleExtractImage', 'watermarkInvisibleExtractPreview');

// Show loading state
function showLoading(buttonElement) {
    buttonElement.disabled = true;
    buttonElement.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Memproses...';
}

// Reset button state
function resetButton(buttonElement, originalText) {
    buttonElement.disabled = false;
    buttonElement.innerHTML = originalText;
}

// Show success message
function showSuccess(elementId, message) {
    const element = document.getElementById(elementId);
    element.innerHTML = `
        <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg">
            <i class="fas fa-check-circle mr-2"></i>${message}
        </div>
    `;
}

// Show error message
function showError(elementId, message) {
    const element = document.getElementById(elementId);
    element.innerHTML = `
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg">
            <i class="fas fa-exclamation-circle mr-2"></i>${message}
        </div>
    `;
}

// Steganography Encode Form
document.getElementById('stegoEncodeForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const submitButton = e.target.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    showLoading(submitButton);

    const formData = new FormData();
    formData.append('image', document.getElementById('stegoEncodeImage').files[0]);
    formData.append('message', document.getElementById('stegoMessage').value);

    try {
        const response = await fetch('/steganography/encode', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'stego_image.png';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showSuccess('stegoEncodeResult', 'Pesan berhasil di-encode! Gambar telah didownload.');
        } else {
            const error = await response.json();
            showError('stegoEncodeResult', error.error || 'Terjadi kesalahan saat encode pesan.');
        }
    } catch (error) {
        showError('stegoEncodeResult', 'Terjadi kesalahan: ' + error.message);
    } finally {
        resetButton(submitButton, originalText);
    }
});

// Steganography Decode Form
document.getElementById('stegoDecodeForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const submitButton = e.target.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    showLoading(submitButton);

    const formData = new FormData();
    formData.append('image', document.getElementById('stegoDecodeImage').files[0]);

    try {
        const response = await fetch('/steganography/decode', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById('stegoDecodeResult').innerHTML = `
                <div class="bg-blue-100 border border-blue-400 text-blue-900 px-4 py-3 rounded-lg">
                    <p class="font-semibold mb-2"><i class="fas fa-message mr-2"></i>Pesan Tersembunyi:</p>
                    <div class="bg-white p-4 rounded border">
                        <p class="text-gray-800">${data.message}</p>
                    </div>
                </div>
            `;
        } else {
            showError('stegoDecodeResult', data.error || 'Terjadi kesalahan saat decode pesan.');
        }
    } catch (error) {
        showError('stegoDecodeResult', 'Terjadi kesalahan: ' + error.message);
    } finally {
        resetButton(submitButton, originalText);
    }
});

// Visible Watermark Form
document.getElementById('watermarkVisibleForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const submitButton = e.target.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    showLoading(submitButton);

    const formData = new FormData();
    formData.append('image', document.getElementById('watermarkVisibleImage').files[0]);
    formData.append('text', document.getElementById('watermarkText').value);
    formData.append('position', document.getElementById('watermarkPosition').value);
    formData.append('opacity', document.getElementById('watermarkOpacity').value);

    try {
        const response = await fetch('/watermark/visible', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'watermarked_image.png';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showSuccess('watermarkVisibleResult', 'Watermark berhasil ditambahkan! Gambar telah didownload.');
        } else {
            const error = await response.json();
            showError('watermarkVisibleResult', error.error || 'Terjadi kesalahan saat menambahkan watermark.');
        }
    } catch (error) {
        showError('watermarkVisibleResult', 'Terjadi kesalahan: ' + error.message);
    } finally {
        resetButton(submitButton, originalText);
    }
});

// Image/Logo Watermark Form
document.getElementById('watermarkImageForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const submitButton = e.target.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    showLoading(submitButton);

    const formData = new FormData();
    formData.append('image', document.getElementById('watermarkImageBase').files[0]);
    formData.append('logo', document.getElementById('watermarkImageLogo').files[0]);
    formData.append('position', document.getElementById('watermarkImagePosition').value);
    formData.append('opacity', document.getElementById('watermarkImageOpacity').value);
    formData.append('scale', document.getElementById('watermarkImageScale').value);

    try {
        const response = await fetch('/watermark/image', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'watermarked_logo.png';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showSuccess('watermarkImageResult', 'Watermark logo berhasil ditambahkan! Gambar telah didownload.');
        } else {
            const error = await response.json();
            showError('watermarkImageResult', error.error || 'Terjadi kesalahan saat menambahkan watermark logo.');
        }
    } catch (error) {
        showError('watermarkImageResult', 'Terjadi kesalahan: ' + error.message);
    } finally {
        resetButton(submitButton, originalText);
    }
});

// Invisible Watermark Add Form
document.getElementById('watermarkInvisibleAddForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const submitButton = e.target.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    showLoading(submitButton);

    const formData = new FormData();
    formData.append('image', document.getElementById('watermarkInvisibleImage').files[0]);
    formData.append('text', document.getElementById('watermarkInvisibleText').value);

    try {
        const response = await fetch('/watermark/invisible/add', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'watermarked_invisible.png';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showSuccess('watermarkInvisibleAddResult', 'Watermark invisible berhasil ditambahkan! Gambar telah didownload.');
        } else {
            const error = await response.json();
            showError('watermarkInvisibleAddResult', error.error || 'Terjadi kesalahan saat menambahkan watermark.');
        }
    } catch (error) {
        showError('watermarkInvisibleAddResult', 'Terjadi kesalahan: ' + error.message);
    } finally {
        resetButton(submitButton, originalText);
    }
});

// Invisible Watermark Extract Form
document.getElementById('watermarkInvisibleExtractForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const submitButton = e.target.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    showLoading(submitButton);

    const formData = new FormData();
    formData.append('image', document.getElementById('watermarkInvisibleExtractImage').files[0]);

    try {
        const response = await fetch('/watermark/invisible/extract', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById('watermarkInvisibleExtractResult').innerHTML = `
                <div class="bg-blue-100 border border-blue-400 text-blue-900 px-4 py-3 rounded-lg">
                    <p class="font-semibold mb-2"><i class="fas fa-copyright mr-2"></i>Watermark Ditemukan:</p>
                    <div class="bg-white p-4 rounded border">
                        <p class="text-gray-800">${data.watermark}</p>
                    </div>
                </div>
            `;
        } else {
            showError('watermarkInvisibleExtractResult', data.error || 'Terjadi kesalahan saat ekstrak watermark.');
        }
    } catch (error) {
        showError('watermarkInvisibleExtractResult', 'Terjadi kesalahan: ' + error.message);
    } finally {
        resetButton(submitButton, originalText);
    }
});
