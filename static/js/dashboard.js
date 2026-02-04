const STOCKS = ['MSFT', 'GOOG', 'AAPL', 'CRM', 'NVDA', 'AMZN', 'META', 'ORCL'];
let stocksData = {};
let selectedStock = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadStocks();
    
    // Refresh stocks every 30 seconds
    setInterval(loadStocks, 30000);
    
    // Modal close handlers
    const modal = document.getElementById('newsModal');
    const closeBtn = document.querySelector('.close');
    
    closeBtn.onclick = () => closeModal();
    
    window.onclick = (event) => {
        if (event.target === modal) {
            closeModal();
        }
    };
});

function loadStocks() {
    const stockGrid = document.getElementById('stockGrid');
    
    if (stockGrid.children.length === 0) {
        stockGrid.innerHTML = '<div class="loading">Loading stock data...</div>';
    }
    
    fetch('/api/stocks')
        .then(response => response.json())
        .then(data => {
            stocksData = data;
            renderStocks();
            updateLastUpdated();
        })
        .catch(error => {
            console.error('Error loading stocks:', error);
            stockGrid.innerHTML = '<div class="loading">Error loading stock data. Please try again.</div>';
        });
}

function renderStocks() {
    const stockGrid = document.getElementById('stockGrid');
    stockGrid.innerHTML = '';
    
    STOCKS.forEach(symbol => {
        const stock = stocksData[symbol];
        if (stock) {
            const card = createStockCard(symbol, stock);
            stockGrid.appendChild(card);
        }
    });
}

function createStockCard(symbol, data) {
    const card = document.createElement('div');
    card.className = `stock-card ${data.isUp ? 'up' : 'down'}`;
    card.onclick = () => openNewsModal(symbol);
    
    const changeSign = data.isUp ? '+' : '';
    const changeArrow = data.isUp ? '▲' : '▼';
    const formattedChange = `${changeSign}${data.change.toFixed(2)}`;
    const formattedPercent = `${changeSign}${data.changePercent.toFixed(2)}%`;
    
    card.innerHTML = `
        <div class="stock-symbol">${symbol}</div>
        <div class="stock-price">$${data.price.toFixed(2)}</div>
        <div class="stock-change">
            <span class="change-arrow">${changeArrow}</span>
            <span>${formattedChange} (${formattedPercent})</span>
        </div>
        <div class="previous-close">Prev Close: $${data.previousClose.toFixed(2)}</div>
        <div class="click-hint">Click for latest news 📰</div>
    `;
    
    return card;
}

function openNewsModal(symbol) {
    selectedStock = symbol;
    const stock = stocksData[symbol];
    const modal = document.getElementById('newsModal');
    
    // Update header
    document.getElementById('modalStockName').textContent = symbol;
    document.getElementById('modalStockPrice').textContent = `Price: $${stock.price.toFixed(2)}`;
    
    const changeSign = stock.isUp ? '+' : '';
    const changePercent = stock.isUp ? '+' : '';
    document.getElementById('modalStockChange').textContent = 
        `Change: ${changeSign}$${stock.change.toFixed(2)} (${changePercent}${stock.changePercent.toFixed(2)}%)`;
    
    // Update color based on up/down
    const modalHeader = document.querySelector('.modal-header');
    if (stock.isUp) {
        modalHeader.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
    } else {
        modalHeader.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
    }
    
    // Load analysis
    const analysisList = document.getElementById('analysisList');
    analysisList.innerHTML = '<p class="loading" style="color: #6b7280; padding: 20px;">Loading AI analysis...</p>';
    
    fetch(`/api/analysis/${symbol}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderAnalysis(data.analysis, data.cached);
            } else {
                analysisList.innerHTML = `<p style="color: #ef4444; padding: 20px;">Error loading analysis: ${data.error || 'Unknown error'}</p>`;
            }
        })
        .catch(error => {
            console.error('Error loading analysis:', error);
            analysisList.innerHTML = '<p style="color: #ef4444; padding: 20px;">Error loading analysis. Please try again.</p>';
        });
    
    // Show modal
    modal.classList.add('show');
}

function renderAnalysis(analysis, cached) {
    const analysisList = document.getElementById('analysisList');
    analysisList.innerHTML = '';
    
    // Create analysis container
    const div = document.createElement('div');
    div.style.cssText = 'padding: 20px; line-height: 1.6; color: #1f2937; font-size: 14px;';
    
    // Convert markdown to HTML (basic: bold, italics, bullet points)
    let html = analysis
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n- /g, '<br/>• ')
        .replace(/\n/g, '<br/>');
    
    div.innerHTML = html;
    analysisList.appendChild(div);
    
    // Add cache indicator if cached
    if (cached) {
        const cacheNote = document.createElement('p');
        cacheNote.style.cssText = 'padding: 10px 20px; font-size: 12px; color: #9ca3af; border-top: 1px solid #e5e7eb; margin-top: 10px;';
        cacheNote.textContent = '(Cached analysis)';
        analysisList.appendChild(cacheNote);
    }
}

function closeModal() {
    const modal = document.getElementById('newsModal');
    modal.classList.remove('show');
    selectedStock = null;
}

function updateLastUpdated() {
    const lastUpdated = document.getElementById('lastUpdated');
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    lastUpdated.textContent = `Last updated: ${timeString}`;
}
