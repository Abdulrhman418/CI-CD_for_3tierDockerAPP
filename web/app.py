import os
from flask import Flask, render_template_string
import requests

app = Flask(__name__)

@app.route("/")
def home():
    API_HOST = os.getenv("API_HOST", "api-tair")
    products = []

    try:
        res = requests.get(f"http://{API_HOST}:5000/products", timeout=5)
        if res.status_code == 200:
            products = res.json()
    except requests.RequestException:
        products = []

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Product Store</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f7f7f7;
                margin: 0;
                padding: 0;
            }
            header {
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                text-align: center;
            }
            h1 {
                margin: 0;
            }
            .container {
                padding: 30px;
                max-width: 900px;
                margin: auto;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                background-color: white;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            th, td {
                padding: 15px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #f2f2f2;
            }
            tr:hover {
                background-color: #f1f1f1;
            }
            .no-products {
                text-align: center;
                padding: 20px;
                font-style: italic;
                color: #666;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Our Products</h1>
        </header>
        <div class="container">
            {% if products %}
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Price ($)</th>
                    </tr>
                </thead>
                <tbody>
                    {% for p in products %}
                    <tr>
                        <td>{{ p['id'] }}</td>
                        <td>{{ p['name'] }}</td>
                        <td>{{ "%.2f"|format(p['price']) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <div class="no-products">No products available</div>
            {% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html, products=products)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

