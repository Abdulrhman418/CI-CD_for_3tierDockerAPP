import os
from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_NAME = os.getenv("DB_NAME", "products_db")

    DB_PASSWORD = os.getenv("DB_PASSWORD")
    password_file = os.getenv("DB_PASSWORD_FILE")
    if password_file:
        with open(password_file) as f:
            DB_PASSWORD = f.read().strip()

    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

@app.route("/products", methods=["GET"])
def get_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price FROM products")
        rows = cursor.fetchall()
        rows_serializable = [{"id": r[0], "name": r[1], "price": float(r[2])} for r in rows]
        return jsonify(rows_serializable)
    except Exception as e:
        print(f"DB error: {e}")
        return jsonify([]), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/products", methods=["POST"])
def add_product():
    try:
        data = request.get_json()
        if not data or "name" not in data or "price" not in data:
            return jsonify({"error": "Missing name or price"}), 400
        
        name = data["name"]
        price = float(data["price"])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, price) VALUES (%s, %s)", (name, price))
        conn.commit()
        
        return jsonify({
            "id": cursor.lastrowid,
            "name": name,
            "price": price,
            "message": "Product added successfully"
        }), 201
    except ValueError:
        return jsonify({"error": "Invalid price format"}), 400
    except Exception as e:
        print(f"DB error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/health")
def health():
    return jsonify({"status": "API is running"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

