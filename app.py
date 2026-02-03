from flask import Flask, render_template, jsonify
import requests
import json
import os
import yfinance as yf
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env if present
load_dotenv()

app = Flask(__name__)

# Stock symbols to track
STOCKS = ['MSFT', 'GOOG', 'AAPL', 'CRM', 'NVDA', 'AMZN', 'META', 'ORCL']

# Load API keys from environment (.env or environment variables)
# Example .env keys: STOCK_API_KEY, NEWS_API_KEY
STOCK_API_KEY = os.getenv('STOCK_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

if not NEWS_API_KEY:
    print('Warning: NEWS_API_KEY not set. Using fallback demo news.')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stocks')
def get_stocks():
    """Fetch current stock prices"""
    stocks_data = {}
    
    for symbol in STOCKS:
        try:
            # Fetch data using yfinance (handles Yahoo Finance auth properly)
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if 'regularMarketPrice' in info and info['regularMarketPrice'] is not None:
                current_price = info['regularMarketPrice']
                previous_close = info.get('previousClose', current_price)
                change = current_price - previous_close
                change_percent = (change / previous_close * 100) if previous_close != 0 else 0
                
                stocks_data[symbol] = {
                    'price': round(current_price, 2),
                    'change': round(change, 2),
                    'changePercent': round(change_percent, 2),
                    'isUp': change >= 0,
                    'previousClose': round(previous_close, 2)
                }
                print(f"✓ Fetched live data for {symbol}: ${current_price}")
            else:
                print(f"Could not fetch price for {symbol}. Using fallback.")
                stocks_data[symbol] = get_fallback_stock_data(symbol)
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            print(f"Using fallback data for {symbol}.")
            stocks_data[symbol] = get_fallback_stock_data(symbol)
    
    return jsonify(stocks_data)

def get_fallback_stock_data(symbol):
    """Fallback data for demonstration"""
    fallback_data = {
        'MSFT': {'price': 440.50, 'change': 2.50, 'changePercent': 0.57, 'isUp': True, 'previousClose': 438.00},
        'GOOG': {'price': 205.75, 'change': -1.25, 'changePercent': -0.61, 'isUp': False, 'previousClose': 207.00},
        'AAPL': {'price': 230.40, 'change': 3.40, 'changePercent': 1.50, 'isUp': True, 'previousClose': 227.00},
        'CRM': {'price': 315.60, 'change': 1.10, 'changePercent': 0.35, 'isUp': True, 'previousClose': 314.50},
        'NVDA': {'price': 875.30, 'change': -5.70, 'changePercent': -0.65, 'isUp': False, 'previousClose': 881.00},
        'AMZN': {'price': 195.45, 'change': 2.15, 'changePercent': 1.11, 'isUp': True, 'previousClose': 193.30},
        'META': {'price': 615.20, 'change': -8.80, 'changePercent': -1.41, 'isUp': False, 'previousClose': 624.00},
        'ORCL': {'price': 143.70, 'change': 0.70, 'changePercent': 0.49, 'isUp': True, 'previousClose': 143.00},
    }
    return fallback_data.get(symbol, {'price': 0, 'change': 0, 'changePercent': 0, 'isUp': True, 'previousClose': 0})

@app.route('/api/news/<symbol>')
def get_news(symbol):
    """Fetch top 3 news stories for a stock"""
    try:
        # Using NewsAPI - sign up at https://newsapi.org/
        params = {
            'q': f'{symbol} stock',
            'sortBy': 'publishedAt',
            'language': 'en',
            'pageSize': 3
        }
        headers = {}
        # NewsAPI accepts 'X-Api-Key' header or 'apiKey' query param
        if NEWS_API_KEY:
            headers['X-Api-Key'] = NEWS_API_KEY

        response = requests.get(
            'https://newsapi.org/v2/everything',
            params=params,
            headers=headers if headers else None,
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            return jsonify({
                'success': True,
                'news': [{
                    'title': article.get('title'),
                    'description': article.get('description'),
                    'url': article.get('url'),
                    'source': article.get('source', {}).get('name'),
                    'publishedAt': article.get('publishedAt')
                } for article in articles[:3]]
            })
        else:
            return jsonify({'success': False, 'news': get_fallback_news(symbol)})
    except Exception as e:
        print(f"Error fetching news for {symbol}: {e}")
        return jsonify({'success': True, 'news': get_fallback_news(symbol)})

def get_fallback_news(symbol):
    """Fallback news data for demonstration"""
    fallback_news = {
        'MSFT': [
            {
                'title': f'{symbol} Announces New AI Initiative',
                'description': 'Microsoft expands its AI offerings with new enterprise solutions.',
                'url': '#',
                'source': 'Tech News Daily',
                'publishedAt': '2026-02-03T10:00:00Z'
            },
            {
                'title': f'{symbol} Q4 Earnings Beat Expectations',
                'description': 'Strong quarterly results driven by cloud services growth.',
                'url': '#',
                'source': 'Financial Times',
                'publishedAt': '2026-02-02T15:30:00Z'
            },
            {
                'title': f'{symbol} Partners with Leading Enterprise',
                'description': 'New strategic partnership announced to expand market reach.',
                'url': '#',
                'source': 'Business Wire',
                'publishedAt': '2026-02-01T12:00:00Z'
            }
        ]
    }
    
    return fallback_news.get(symbol, [
        {'title': f'Latest news for {symbol}', 'description': 'Stay tuned for updates', 'url': '#', 'source': 'News', 'publishedAt': datetime.now().isoformat()}
    ])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
