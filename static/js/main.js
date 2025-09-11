async function refreshAllServices() {
    const btn = document.getElementById('refreshBtn');
    const loading = document.getElementById('loading');
    const content = document.getElementById('content');
    
    btn.disabled = true;
    loading.style.display = 'block';
    
    try {
        const response = await fetch('/api/all');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        content.innerHTML = generateAllServicesHtml(data);
    } catch (error) {
        console.error('Error fetching data:', error);
        content.innerHTML = '<div class="error">Ошибка при обновлении данных</div>';
    } finally {
        btn.disabled = false;
        loading.style.display = 'none';
    }
}

function generateAllServicesHtml(data) {
    return `
        <!-- XMLRiver Service -->
        <div class="service-section">
            <h2>💰 XMLRiver (Яндекс.Кошелек)</h2>
            ${generateXmlRiverHtml(data.xmlriver)}
        </div>

        <!-- Database Service -->
        <div class="service-section">
            <h2>🛢️ База данных ClickHouse</h2>
            ${generateDatabaseHtml(data.database)}
        </div>

        <!-- DaData Service -->
        <div class="service-section">
            <h2>📊 DaData API</h2>
            ${generateDadataHtml(data.dadata)}
        </div>

        <!-- System Monitoring -->
        <div class="service-section">
            <h2>🖥️ Мониторинг системы</h2>
            ${generateSystemHtml(data.system)}
        </div>
    `;
}

function generateXmlRiverHtml(data) {
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

function generateDatabaseHtml(data) {
    if (data.status === 'error') {
        return `<div class="error">${data.error || 'Неизвестная ошибка'}</div>`;
    }
    
    const companiesBlock = data.unique_companies_count !== null && data.unique_companies_count !== undefined ? `
        <div class="companies-highlight-block">
            <div class="companies-icon">🏢</div>
            <div class="companies-info">
                <div class="companies-title">Уникальные компании</div>
                <div class="companies-number">${data.unique_companies_count}</div>
                <div class="companies-subtitle">подозрительных компаний, у которых одно название связано с несколькими ИНН</div>
            </div>
        </div>
    ` : '';
    
    return `
        <div class="info-card">
            <div class="status-ok">${data.connection_status}</div>
            ${data.response_time ? `<div class="response-time">Время отклика: ${data.response_time}</div>` : ''}
        </div>
        ${companiesBlock}
    `;
}

function generateDadataHtml(data) {
    if (data.status === 'error') {
        return `<div class="error">${data.error || 'Неизвестная ошибка'}</div>`;
    }
    
    const accountsHtml = data.accounts.map((account, index) => `
        <div class="dadata-account">
            <strong>${account.account_name}</strong><br>
            Дата: ${account.date}<br>
            Осталось запросов: <span class="remaining">${account.remaining_requests}</span>
        </div>
        ${index < data.accounts.length - 1 ? '<hr class="account-separator">' : ''}
    `).join('');
    
    return `<div class="info-card">${accountsHtml}</div>`;
}

function generateSystemHtml(data) {
    if (data.status === 'error') {
        return `<div class="error">${data.error || 'Неизвестная ошибка'}</div>`;
    }
    
    return `
        <div class="info-card">
            <div class="system-resource">
                <strong>💾 Оперативная память:</strong><br>
                Занято: ${data.ram_percent}% (${data.ram_used_gb})
            </div>
            <hr class="resource-separator">
            <div class="system-resource">
                <strong>💿 Дисковое пространство:</strong><br>
                Занято: ${data.disk_percent}% (${data.disk_used_gb})
            </div>
            <hr class="resource-separator">
            <div class="system-resource">
                <strong>⚡ Процессор (CPU):</strong><br>
                Загруженность: ${data.cpu_percent}%
            </div>
        </div>
    `;
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('Page loaded successfully');
});