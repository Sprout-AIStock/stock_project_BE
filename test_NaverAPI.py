from flask import Flask, jsonify, render_template
from urllib.request import Request, urlopen
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/api/chart-data/<item_code>')
def chart_data(item_code):
    try:
        url = f"https://m.stock.naver.com/api/stock/{item_code}/integration"
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        raw = urlopen(req).read()
        data = json.loads(raw)

        trend = data.get("dealTrendInfos", [])
        result = {
            "labels": [],
            "prices": []
        }

        for entry in trend:
            date = entry.get("bizdate")
            price = entry.get("closePrice")
            if date and price:
                result["labels"].append(f"{date[:4]}-{date[4:6]}-{date[6:]}")  # YYYY-MM-DD
                result["prices"].append(int(price.replace(',', '')))

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
