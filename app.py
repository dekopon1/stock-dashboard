from flask import Flask, render_template, jsonify
import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import google.generativeai as genai

# Load environment variables from .env if present
load_dotenv()

app = Flask(__name__)

# Stock symbols to track
STOCKS = ['MSFT', 'GOOG', 'AAPL', 'CRM', 'NVDA', 'AMZN', 'META', 'ORCL']

# Load API keys from environment (.env or environment variables)
# Example .env keys: STOCK_API_KEY (Finnhub), NEWS_API_KEY (NewsAPI), GEMINI_API_KEY (Google)
STOCK_API_KEY = os.getenv('STOCK_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not STOCK_API_KEY:
    print('Warning: STOCK_API_KEY not set. Using fallback demo stock data.')
if not NEWS_API_KEY:
    print('Warning: NEWS_API_KEY not set. Using fallback demo news.')
if not GEMINI_API_KEY:
    print('Warning: GEMINI_API_KEY not set. AI analysis will not be available.')
else:
    genai.configure(api_key=GEMINI_API_KEY)

# Finnhub API endpoint
FINNHUB_BASE_URL = 'https://finnhub.io/api/v1/quote'

# Cache for analysis (in-memory, 4-hour TTL)
analysis_cache = {}
CACHE_TTL_SECONDS = 4 * 60 * 60  # 4 hours

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stocks')
def get_stocks():
    """Fetch current stock prices from Finnhub API"""
    stocks_data = {}
    
    if not STOCK_API_KEY:
        print('STOCK_API_KEY not set. Using fallback data for all stocks.')
        for symbol in STOCKS:
            stocks_data[symbol] = get_fallback_stock_data(symbol)
        return jsonify(stocks_data)
    
    for symbol in STOCKS:
        try:
            # Call Finnhub quote endpoint
            params = {
                'symbol': symbol,
                'token': STOCK_API_KEY
            }
            response = requests.get(FINNHUB_BASE_URL, params=params, timeout=5)
            
            if response.status_code == 200:
                quote = response.json()
                
                # Check for API error messages
                if isinstance(quote, dict) and 'error' in quote:
                    print(f"Finnhub error for {symbol}: {quote['error']}")
                    stocks_data[symbol] = get_fallback_stock_data(symbol)
                    continue
                
                # Finnhub response keys: c = current price, pc = previous close
                current_price = quote.get('c')
                prev_close = quote.get('pc')
                
                if current_price is not None and prev_close is not None:
                    try:
                        current_price = float(current_price)
                        previous_close = float(prev_close)
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
                    except (ValueError, TypeError) as ve:
                        print(f"Error parsing price data for {symbol}: {ve}")
                        stocks_data[symbol] = get_fallback_stock_data(symbol)
                else:
                    print(f"No price data for {symbol}. Using fallback.")
                    stocks_data[symbol] = get_fallback_stock_data(symbol)
            else:
                print(f"HTTP error {response.status_code} for {symbol}")
                stocks_data[symbol] = get_fallback_stock_data(symbol)
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
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

@app.route('/api/analysis/<symbol>')
def get_analysis(symbol):
    """Get AI-powered analysis of why a stock is up or down"""
    
    # Check cache first
    if symbol in analysis_cache:
        cached_data, timestamp = analysis_cache[symbol]
        if datetime.now() - timestamp < timedelta(seconds=CACHE_TTL_SECONDS):
            print(f"Returning cached analysis for {symbol}")
            return jsonify({'success': True, 'analysis': cached_data, 'cached': True})
        else:
            # Cache expired, remove it
            del analysis_cache[symbol]
    
    if not GEMINI_API_KEY:
        return jsonify({
            'success': False,
            'error': 'GEMINI_API_KEY not configured',
            'analysis': 'AI analysis not available. Please configure GEMINI_API_KEY.'
        }), 503
    
    try:
        # Create Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Get current stock data to include in prompt
        stock_info = stocks_data.get(symbol) if 'stocks_data' in globals() else {}
        
        # Prompt Gemini to search for recent news and provide analysis
        prompt = f"""Please perform a web search and analyze recent news about {symbol} stock. 

Provide a comprehensive analysis including:
1. **Key News**: Recent significant developments from major business news sources (Bloomberg, CNBC, Reuters, MarketWatch, etc.)
2. **Market Context**: How {symbol} is performing relative to its sector and the broader market indices (S&P 500, NASDAQ if applicable)
3. **Why Up/Down**: Key drivers of the stock's recent price movement
4. **Analyst Sentiment**: Any analyst upgrades/downgrades or consensus opinions if available
5. **Short Analysis**: A 2-3 sentence summary of the current situation

Format your response in clear sections with markdown formatting. Keep it concise but informative."""
        
        print(f"Generating AI analysis for {symbol}...")
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=800,
            ),
            safety_settings=[
                {
                    "category": genai.types.HarmCategory.HARM_CATEGORY_UNSPECIFIED,
                    "threshold": genai.types.HarmBlockThreshold.BLOCK_NONE,
                }
            ]
        )
        
        analysis_text = response.text
        
        # Cache the result
        analysis_cache[symbol] = (analysis_text, datetime.now())
        
        return jsonify({
            'success': True,
            'analysis': analysis_text,
            'cached': False
        })
    
    except Exception as e:
        print(f"Error generating analysis for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'analysis': f'Could not generate AI analysis: {str(e)}'
        }), 500

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


@app.route('/api/health')
def health():
    """Lightweight health/config endpoint that does NOT expose secrets.

    Returns booleans indicating whether required API keys are configured,
    plus a few internal stats useful for debugging deployments.
    """
    try:
        gemini_ok = bool(GEMINI_API_KEY)
    except NameError:
        gemini_ok = False

    try:
        stock_ok = bool(STOCK_API_KEY)
    except NameError:
        stock_ok = False

    try:
        news_ok = bool(NEWS_API_KEY)
    except NameError:
        news_ok = False

    cache_count = len(analysis_cache) if 'analysis_cache' in globals() else 0

    return jsonify({
        'success': True,
        'gemini_configured': gemini_ok,
        'stock_api_configured': stock_ok,
        'news_api_configured': news_ok,
        'analysis_cache_entries': cache_count,
        'cache_ttl_seconds': CACHE_TTL_SECONDS
    })

if __name__ == '__main__':
    # Use the PORT environment variable provided by Render (or default to 5000)
    port = int(os.environ.get('PORT', 5000))
    # Bind to 0.0.0.0 so the service is reachable from outside the container
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')
