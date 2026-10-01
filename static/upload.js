const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const submitBtn = document.getElementById('submitBtn');
const loadingCard = document.getElementById('loadingCard');
const uploadForm = document.getElementById('uploadForm');

dropzone.addEventListener('click', () => fileInput.click());
dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
});
dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        showFile();
    }
});
fileInput.addEventListener('change', showFile);

function showFile() {
    const file = fileInput.files[0];
    if (!file) return;
    if (!/\.(zip|tar|tar\.gz|tgz)$/i.test(file.name)) {
        fileInfo.textContent = 'Error: hanya file .zip, .tar, .tar.gz yang diizinkan.';
        fileInfo.classList.add('error');
        submitBtn.disabled = true;
        return;
    }
    fileInfo.classList.remove('error');
    fileInfo.textContent = `File: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
    submitBtn.disabled = false;
}

uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const file = fileInput.files[0];
    if (!file) return;

    loadingCard.style.display = 'block';
    submitBtn.disabled = true;

    const fd = new FormData();
    fd.append('file', file);

    try {
        const res = await fetch('/detect', { method: 'POST', body: fd });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Upload gagal');

        sessionStorage.setItem('detection', JSON.stringify(data));
        window.location.href = '/confirm';
    } catch (err) {
        loadingCard.style.display = 'none';
        submitBtn.disabled = false;
        fileInfo.textContent = 'Error: ' + err.message;
        fileInfo.classList.add('error');
    }
});
