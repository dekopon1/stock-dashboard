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
    
    // Load news
    const newsList = document.getElementById('newsList');
    newsList.innerHTML = '<p class="loading" style="color: #6b7280; padding: 20px;">Loading news stories...</p>';
    
    fetch(`/api/news/${symbol}`)
        .then(response => response.json())
        .then(data => {
            renderNews(data.news || []);
        })
        .catch(error => {
            console.error('Error loading news:', error);
            newsList.innerHTML = '<p style="color: #ef4444; padding: 20px;">Error loading news. Please try again.</p>';
        });
    
    // Show modal
    modal.classList.add('show');
}

function renderNews(articles) {
    const newsList = document.getElementById('newsList');
    newsList.innerHTML = '';
    
    if (articles.length === 0) {
        newsList.innerHTML = '<p style="color: #9ca3af; padding: 20px;">No news articles available.</p>';
        return;
    }
    
    articles.forEach(article => {
        const newsItem = document.createElement('div');
        newsItem.className = 'news-item';
        
        const publishDate = new Date(article.publishedAt);
        const formattedDate = publishDate.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        newsItem.innerHTML = `
            <div class="news-title">
                <a href="${article.url}" target="_blank" rel="noopener noreferrer">
                    ${article.title}
                </a>
            </div>
            <div class="news-description">
                ${article.description || 'No description available.'}
            </div>
            <div class="news-meta">
                <span class="news-source">${article.source}</span>
                <span class="news-time">${formattedDate}</span>
            </div>
        `;
        
        newsList.appendChild(newsItem);
    });
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
