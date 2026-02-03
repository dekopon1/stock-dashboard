# Stock Price Dashboard

An interactive real-time stock price dashboard displaying live data for major tech stocks with color-coded indicators and expandable news sections.

## Features

✅ **Real-Time Stock Prices** - Live price updates for MSFT, GOOG, AAPL, CRM, NVDA, AMZN, META, ORCL
✅ **Color-Coded Cards** - Green for gains, Red for losses
✅ **Expandable News Section** - Click any stock to see top 3 latest stories
✅ **Auto-Refresh** - Updates every 30 seconds
✅ **Responsive Design** - Works on desktop, tablet, and mobile
✅ **Beautiful UI** - Modern gradient design with smooth animations

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Add API Keys (Required for Stock Prices)

**Stock API (Required):** Sign up for a free Finnhub API key at [https://finnhub.io/](https://finnhub.io/). Free tier: 60 requests/min.

**News API (Optional):** For live news stories, sign up at [NewsAPI.org](https://newsapi.org/).

Create a file named `.env` in the project root with:

```env
STOCK_API_KEY=your_finnhub_key_here
NEWS_API_KEY=your_newsapi_key_here
```

The app uses `python-dotenv` to load `.env` automatically. Alternatively set environment variables directly.

> **Note:** If `STOCK_API_KEY` isn't set, the app will use fallback demo stock data. If `NEWS_API_KEY` isn't set, fallback demo news will display.

### 3. Run the Application

```bash
python app.py
```

The dashboard will be available at: **http://localhost:5000**

## How to Use

1. **View Stock Prices** - See all 8 stocks on the dashboard with current prices and changes
2. **Identify Trends** - Green cards = up, Red cards = down
3. **Read News** - Click any stock card to expand and view the latest 3 news stories
4. **Auto-Refresh** - Data refreshes automatically every 30 seconds

## File Structure

```
├── app.py                          # Flask backend
├── requirements.txt                # Python dependencies
├── templates/
│   └── index.html                 # Main dashboard HTML
└── static/
    ├── css/
    │   └── style.css              # Styling and animations
    └── js/
        └── dashboard.js           # Interactive functionality
```

## API Endpoints

- `GET /` - Main dashboard page
- `GET /api/stocks` - Get current prices for all stocks (JSON)
- `GET /api/news/<SYMBOL>` - Get top 3 news stories for a stock (JSON)

## Data Sources

- **Stock Prices**: Finnhub API (free tier, 60 requests/min)
- **News**: NewsAPI.org (optional, uses fallback demo data if not configured)

## Customization

### Add/Remove Stocks

Edit the `STOCKS` list in `app.py`:

```python
STOCKS = ['MSFT', 'GOOG', 'AAPL', 'CRM', 'NVDA', 'AMZN', 'META', 'ORCL']
```

### Change Refresh Rate

Modify the interval in `static/js/dashboard.js`:

```javascript
setInterval(loadStocks, 30000);  // Change 30000 to desired milliseconds
```

### Customize Colors

Edit `static/css/style.css` to change gradient colors and styling.

## Troubleshooting

**Issue**: Stocks showing as red/down even when they're up
- The fallback data is being used. The app is working correctly!

**Issue**: News not loading
- Add a NewsAPI key, or the fallback demo news will display instead

**Issue**: Port 5000 already in use
- Change the port in `app.py`: `app.run(debug=True, port=5001)`

## Deploying to Render

1. Create a new Web Service on Render and connect your GitHub repository (https://github.com/dekopon1/stock-dashboard).
2. For the build command use:

```
pip install -r requirements.txt
```

3. For the start command use:

```
gunicorn app:app
```

4. Add environment variables on Render for `NEWS_API_KEY` and `STOCK_API_KEY` (if you use them). Render will provide a `PORT` environment variable automatically.

This repo includes a `Procfile` and `render.yaml` to simplify deployment.

## Future Enhancements

- Real-time WebSocket updates
- Historical price charts
- Portfolio tracking
- Stock comparison tools
- Alerts for price changes
- Dark mode toggle

## License

MIT License - Feel free to use and modify!
