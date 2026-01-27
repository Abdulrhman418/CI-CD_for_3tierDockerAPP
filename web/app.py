import os
from flask import Flask, render_template_string, request, jsonify
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
            .form-section {
                background-color: white;
                padding: 20px;
                margin-bottom: 30px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            .form-section h2 {
                color: #4CAF50;
                margin-top: 0;
            }
            .form-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
                color: #333;
            }
            input[type="text"],
            input[type="number"] {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
                font-size: 14px;
            }
            input[type="text"]:focus,
            input[type="number"]:focus {
                outline: none;
                border-color: #4CAF50;
                box-shadow: 0 0 5px rgba(76, 175, 80, 0.3);
            }
            button {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
                font-weight: bold;
            }
            button:hover {
                background-color: #45a049;
            }
            button:active {
                background-color: #3d8b40;
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
                font-weight: bold;
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
            .success {
                color: #4CAF50;
                font-weight: bold;
            }
            .error {
                color: #f44336;
                font-weight: bold;
            }
        </style>
        <script>
            function addProduct() {
                const name = document.getElementById('productName').value;
                const price = document.getElementById('productPrice').value;
                
                if (!name || !price) {
                    alert('Please fill in all fields');
                    return;
                }
                
                fetch('/add-product', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        name: name,
                        price: parseFloat(price)
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Product added successfully!');
                        document.getElementById('productName').value = '';
                        document.getElementById('productPrice').value = '';
                        location.reload();
                    } else {
                        alert('Error: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error adding product');
                });
            }
        </script>
    </head>
    <body>
        <header>
            <h1>Our Products</h1>
        </header>
        <div class="container">
            <div class="form-section">
                <h2>Add New Product</h2>
                <div class="form-group">
                    <label for="productName">Product Name:</label>
                    <input type="text" id="productName" placeholder="Enter product name">
                </div>
                <div class="form-group">
                    <label for="productPrice">Price ($):</label>
                    <input type="number" id="productPrice" placeholder="Enter price" step="0.01" min="0">
                </div>
                <button onclick="addProduct()">Add Product</button>
            </div>
            
            <h2>Products List</h2>
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

@app.route("/add-product", methods=["POST"])
def add_product_handler():
    API_HOST = os.getenv("API_HOST", "api-tair")
    try:
        data = request.get_json()
        res = requests.post(
            f"http://{API_HOST}:5000/products",
            json=data,
            timeout=5
        )
        if res.status_code == 201:
            return jsonify({"success": True, "message": "Product added"}), 200
        else:
            return jsonify({"success": False, "error": res.json().get("error", "Failed to add product")}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

