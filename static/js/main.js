async function refreshBalance() {
    const btn = document.getElementById('refreshBtn');
    const loading = document.getElementById('loading');
    const content = document.getElementById('content');
    
    btn.disabled = true;
    loading.style.display = 'block';
    
    try {
        const response = await fetch('/api/balance');
        const data = await response.json();
        content.innerHTML = getContentHtml(data);
    } catch (error) {
        content.innerHTML = '<div class="error">Ошибка при обновлении данных</div>';
    } finally {
        btn.disabled = false;
        loading.style.display = 'none';
    }
}

function getContentHtml(data) {
    if (data.status === 'error') {
        return `<div class="error">${data.error || 'Неизвестная ошибка'}</div>`;
    }
    
    return `
        <div class="info-card">
            <div class="balance">${data.balance} рублей</div>
            <div class="cost">Стоимость запроса: ${data.cost_per_request} копейки</div>
            <div class="rows">Доступно строк: ${data.rows_available}</div>
        </div>
    `;
}