# Stock Price Dashboard

An interactive real-time stock price dashboard displaying live data for major tech stocks with color-coded indicators and AI-powered analysis of price movements.

## Features

✅ **Real-Time Stock Prices** - Live price updates for MSFT, GOOG, AAPL, CRM, NVDA, AMZN, META, ORCL
✅ **Color-Coded Cards** - Green for gains, Red for losses
✅ **AI-Powered Analysis** - Click any stock to see AI-generated analysis of why it's up or down
✅ **Auto-Refresh** - Updates every 30 seconds
✅ **Responsive Design** - Works on desktop, tablet, and mobile
✅ **Beautiful UI** - Modern gradient design with smooth animations

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Add API Keys (Required for Stock Prices & AI Analysis)

**Stock API (Required):** Sign up for a free Finnhub API key at [https://finnhub.io/](https://finnhub.io/). Free tier: 60 requests/min.

**Gemini AI API (Required for Analysis):** Get a free Gemini API key at [https://ai.google.dev/](https://ai.google.dev/). Click "Get API Key" and create a new key. Free tier: 60 requests/min.

Create a file named `.env` in the project root with:

```env
STOCK_API_KEY=your_finnhub_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

The app uses `python-dotenv` to load `.env` automatically. Alternatively set environment variables directly.

> **Note:** If `STOCK_API_KEY` isn't set, the app will use fallback demo stock data. If `GEMINI_API_KEY` isn't set, analysis will not load.

### 3. Run the Application

```bash
python app.py
```

The dashboard will be available at: **http://localhost:5000**

## How to Use

1. **View Stock Prices** - See all 8 stocks on the dashboard with current prices and changes
2. **Identify Trends** - Green cards = up, Red cards = down
3. **Get AI Analysis** - Click any stock card to expand and view AI-generated analysis of price movements
   - Analysis includes relevant news, market context, analyst sentiment, and a concise summary
   - Results are cached for 4 hours to minimize API calls
4. **Auto-Refresh** - Stock prices refresh automatically every 30 seconds

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
- `GET /api/analysis/<SYMBOL>` - Get AI-powered analysis of a stock (JSON, with web search)

## Data Sources

- **Stock Prices**: Finnhub API (free tier, 60 requests/min)
- **AI Analysis**: Google Gemini 1.5 Flash API with web search (free tier, 60 requests/min)
  - Automatically searches for recent news, market trends, and analyst sentiment
  - Results cached for 4 hours

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
- The fallback demo data is being used. The app is working correctly!

**Issue**: Analysis not loading
- Ensure `GEMINI_API_KEY` is set in `.env` or environment variables
- Check that your Gemini API key is valid at [https://ai.google.dev/](https://ai.google.dev/)

**Issue**: Port 5000 already in use
- Change the port in `app.py`: `app.run(debug=True, port=5001)`

**Issue**: Rate limit errors
- Free tier limits: 60 requests/min for Finnhub and Gemini APIs
- Analysis is cached for 4 hours, so repeated clicks on the same stock won't consume extra API quota

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

4. Add environment variables on Render:
   - `STOCK_API_KEY` - Your Finnhub API key
   - `GEMINI_API_KEY` - Your Google Gemini API key
   - Render will provide a `PORT` environment variable automatically.

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
