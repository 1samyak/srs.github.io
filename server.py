from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
CORS(app)  # Allows your HTML file to talk to this server

# Map your dashboard symbols to Yahoo Finance Tickers
# NSE stocks need '.NS', BSE stocks need '.BO'
SYMBOL_MAP = {
    "NIFTY50": "^NSEI",
    "SENSEX": "^BSESN",
    "ELCID": "ELCIDIN.BO",       # BSE Specific
    "NIPPON": "NAM-INDIA.NS",
    "ORCHID": "ORCHPHARMA.NS",
    "KOTAK": "KOTAKBANK.NS",
    "ZEEL": "ZEEL.NS",
    "JIOFIN": "JIOFIN.NS",
    "RVNL": "RVNL.NS",
    "IRFC": "IRFC.NS",
    "ZOMATO": "ZOMATO.NS",
    "TRENT": "TRENT.NS",
    "TATAELXSI": "TATAELXSI.NS"
}

@app.route('/api/market_data', methods=['POST'])
def get_market_data():
    try:
        # 1. Get symbols requested by the frontend
        payload = request.json
        symbols = payload.get('symbols', [])
        
        # 2. Convert to Yahoo Tickers
        yahoo_symbols = [SYMBOL_MAP.get(s, f"{s}.NS") for s in symbols]
        
        # 3. Fetch Real-Time Data (Batch fetch is faster)
        tickers = yf.Tickers(" ".join(yahoo_symbols))
        
        results = []
        for i, sym in enumerate(symbols):
            y_sym = yahoo_symbols[i]
            try:
                # Get data safely
                info = tickers.tickers[y_sym].info
                
                # Priority: Current Price -> Regular Market Price -> Previous Close
                price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
                prev_close = info.get('previousClose') or price
                
                if price:
                    change_pct = ((price - prev_close) / prev_close) * 100
                    results.append({
                        "symbol": sym,
                        "price": round(price, 2),
                        "change": round(change_pct, 2)
                    })
            except Exception as e:
                print(f"Error fetching {y_sym}: {e}")
                # Return 0 if data fails so dashboard doesn't crash
                results.append({"symbol": sym, "price": 0, "change": 0})

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("✅ Server is running! Open index.html now.")
    app.run(port=5000, debug=True)
