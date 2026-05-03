// --- CONFIGURAÇÃO DB LOCAL (INDEXEDDB) ---
const db = new Dexie("AlmoxOfflineDB");
db.version(1).stores({
    products: "id, code, name, stock",
    pendingMovements: "++id, product_code, type, quantity, responsible, date"
});

// --- ESTADO GLOBAL ---
let currentUser = null;
let token = localStorage.getItem('token');
let products = [];

// --- INICIALIZAÇÃO ---
document.addEventListener('DOMContentLoaded', async () => {
    if (token) {
        tryLoginWithToken();
    }
    
    // Registrar Service Worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js');
    }

    // Monitorar Conexão
    window.addEventListener('online', syncOfflineData);
    window.addEventListener('offline', () => {
        document.getElementById('offline-banner').classList.remove('hidden');
    });

    if (!navigator.onLine) {
        document.getElementById('offline-banner').classList.remove('hidden');
    }
});

// --- AUTENTICAÇÃO ---
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const user = document.getElementById('login-user').value;
    const pass = document.getElementById('login-pass').value;

    const formData = new FormData();
    formData.append('username', user);
    formData.append('password', pass);

    try {
        const res = await fetch('/token', { method: 'POST', body: formData });
        if (!res.ok) throw new Error('Falha no login');
        const data = await res.json();
        
        token = data.access_token;
        localStorage.setItem('token', token);
        initApp();
    } catch (err) {
        const errDiv = document.getElementById('login-error');
        errDiv.innerText = "Usuário ou senha incorretos.";
        errDiv.classList.remove('hidden');
    }
});

function tryLoginWithToken() {
    // Tenta carregar dados iniciais para ver se token é válido
    initApp();
}

async function initApp() {
    document.getElementById('page-login').classList.add('hidden');
    document.getElementById('app-container').classList.remove('hidden');
    showPage('dashboard');
    loadData();
    syncOfflineData();
}

document.getElementById('btn-logout').addEventListener('click', () => {
    localStorage.removeItem('token');
    location.reload();
});

// --- NAVEGAÇÃO ---
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(`page-${pageId}`).classList.add('active');
    
    // Update nav colors
    document.querySelectorAll('nav button').forEach(btn => btn.classList.replace('text-blue-600', 'text-gray-400'));
    // (Lógica simples de seleção)
}

// --- DADOS E SYNC ---
async function loadData() {
    try {
        if (navigator.onLine) {
            const res = await fetch('/products', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            products = await res.json();
            // Salva no banco local para uso offline futuro
            await db.products.clear();
            await db.products.bulkAdd(products);
        } else {
            products = await db.products.toArray();
        }
        renderInventory();
        updateStats();
        populateProductSelect();
    } catch (err) {
        console.error("Erro ao carregar dados", err);
    }
}

function renderInventory() {
    const tbody = document.getElementById('inventory-table-body');
    tbody.innerHTML = products.map(p => `
        <tr class="border-b bg-white">
            <td class="p-3">
                <div class="font-bold">${p.name}</div>
                <div class="text-[10px] text-gray-400">${p.code}</div>
            </td>
            <td class="p-3 font-mono ${p.stock <= p.min_stock ? 'text-red-600 font-bold' : ''}">
                ${p.stock}
            </td>
            <td class="p-3 text-gray-500">${p.location}</td>
        </tr>
    `).join('');
}

async function updateStats() {
    if (!navigator.onLine) return;
    try {
        const res = await fetch('/stats', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const stats = await res.json();
        document.getElementById('stat-total').innerText = stats.total;
        document.getElementById('stat-alert').innerText = stats.alert;
        document.getElementById('stat-use').innerText = stats.in_use;
        document.getElementById('stat-today').innerText = stats.today;
    } catch (e) {}
}

function populateProductSelect() {
    const select = document.getElementById('mov-product');
    select.innerHTML = '<option value="">Selecione...</option>' + 
        products.map(p => `<option value="${p.code}">${p.name} (${p.code})</option>`).join('');
}

// --- MOVIMENTAÇÃO ---
document.getElementById('movement-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const mov = {
        product_code: document.getElementById('mov-product').value,
        type: document.getElementById('mov-type').value,
        quantity: parseFloat(document.getElementById('mov-qty').value),
        responsible: document.getElementById('mov-resp').value,
        date: new Date().toISOString(),
        local_id: Date.now() // ID temporário para controle
    };

    if (navigator.onLine) {
        const success = await sendMovementsToServer([mov]);
        if (success) {
            alert("Movimentação registrada com sucesso!");
            loadData();
        }
    } else {
        // MODO OFFLINE
        await db.pendingMovements.add(mov);
        // Atualiza estoque local visual para o usuário não se confundir
        const p = products.find(prod => prod.code === mov.product_code);
        if (p) {
            if (mov.type === 'SAIDA') p.stock -= mov.quantity;
            else p.stock += mov.quantity;
        }
        renderInventory();
        alert("Você está offline. O registro foi salvo e será enviado quando houver internet.");
    }
    e.target.reset();
});

async function sendMovementsToServer(movements) {
    try {
        const res = await fetch('/sync/movements', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(movements)
        });
        return res.ok;
    } catch (e) {
        return false;
    }
}

async function syncOfflineData() {
    if (!navigator.onLine || !token) return;
    
    document.getElementById('offline-banner').classList.add('hidden');
    const pending = await db.pendingMovements.toArray();
    
    if (pending.length > 0) {
        document.getElementById('sync-status').innerText = "Sincronizando...";
        const success = await sendMovementsToServer(pending);
        if (success) {
            await db.pendingMovements.clear();
            document.getElementById('sync-status').innerText = "Sincronizado";
            loadData();
        } else {
            document.getElementById('sync-status').innerText = "Erro ao Sincronizar";
        }
    }
}
