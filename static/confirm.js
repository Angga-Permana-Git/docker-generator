const detection = JSON.parse(sessionStorage.getItem('detection'));

if (!detection) {
    document.body.innerHTML = '<div class="container"><div class="card"><h2>Error</h2><p>Session tidak ditemukan. Silakan upload ulang.</p><a href="/">Kembali</a></div></div>';
    throw new Error('No detection');
}

const fwLabels = {
    nextjs: 'Next.js', react: 'React.js', nodeexpress: 'Node/Express',
    laravel: 'Laravel', codeigniter4: 'CodeIgniter 4', codeigniter3: 'CodeIgniter 3',
    django: 'Django', fastapi: 'FastAPI', flask: 'Flask', generic: 'Generic'
};

document.getElementById('fwLabel').textContent = fwLabels[detection.framework] || detection.framework;
document.getElementById('fwType').textContent = detection.type;
document.getElementById('fwPort').textContent = detection.detected_port;
document.getElementById('fwDb').textContent = detection.db_suggestion;

document.getElementById('sessionId').value = detection.session_id;
document.getElementById('fwName').value = detection.framework;
document.getElementById('sourceDir').value = detection.source_dir;
document.getElementById('app_name').value = 'myapp';
document.getElementById('port').value = detection.detected_port;

const dbType = document.getElementById('db_type');
if (['postgresql', 'mysql', 'mariadb'].includes(detection.db_suggestion)) {
    dbType.value = detection.db_suggestion;
}

const enableSso = document.getElementById('enable_sso');
const ssoFields = document.getElementById('ssoFields');
const enableAi = document.getElementById('enable_ai');
const aiKeyField = document.getElementById('aiKeyField');
const ssoProvider = document.getElementById('sso_provider');
const tenantField = document.getElementById('tenantField');
const domainField = document.getElementById('domainField');

enableSso.addEventListener('change', () => {
    ssoFields.style.display = enableSso.checked ? 'block' : 'none';
});
enableAi.addEventListener('change', () => {
    aiKeyField.style.display = enableAi.checked ? 'block' : 'none';
});
ssoProvider.addEventListener('change', () => {
    tenantField.style.display = ssoProvider.value === 'azuread' ? 'block' : 'none';
    domainField.style.display = (ssoProvider.value === 'generic' || ssoProvider.value === 'genericpmk') ? 'block' : 'none';
});

const form = document.getElementById('confirmForm');
const result = document.getElementById('result');
const aiStatus = document.getElementById('aiStatus');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    result.style.display = 'none';

    const fd = new FormData(form);
    if (!enableSso.checked) {
        fd.delete('sso_provider');
        fd.delete('sso_client_id');
        fd.delete('sso_client_secret');
        fd.delete('sso_tenant_id');
        fd.delete('sso_domain');
    }
    if (!enableAi.checked) {
        fd.delete('ai_provider');
        fd.delete('ai_api_key');
    }

    try {
        const res = await fetch('/generate', { method: 'POST', body: fd });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Generate gagal');

        document.getElementById('downloadLink').href = data.download_url;
        result.style.display = 'block';
        if (data.ai_used) {
            aiStatus.textContent = 'AI analysis berhasil digunakan.';
        } else if (data.ai_error) {
            aiStatus.textContent = 'AI gagal, menggunakan template standar: ' + data.ai_error;
        }
    } catch (err) {
        alert('Error: ' + err.message);
    }
});
