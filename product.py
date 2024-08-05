import os
from flask import Blueprint, render_template, request, jsonify
import snowflake.connector
from config import Config

product_bp = Blueprint('product', __name__)

# Helper function to get Snowflake connection
def get_snowflake_connection(user, password):
    return snowflake.connector.connect(
        user=user,
        password=password,
        account=Config.SNOWFLAKE_ACCOUNT,
        warehouse=Config.SNOWFLAKE_WAREHOUSE,
        database=Config.SNOWFLAKE_DATABASE,
        schema=Config.SNOWFLAKE_SCHEMA
    )

# Fetch all products
def fetch_products(user, password):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("SELECT PRODUCTID, PRODUCTNAME, CATEGORY, BRAND, PRICE, DESCRIPTION, SKU, DIMENSIONS, WEIGHT FROM products")
        return cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Fetch product by ID
def fetch_product_by_id(user, password, product_id):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("SELECT PRODUCTID, PRODUCTNAME, CATEGORY, BRAND, PRICE, DESCRIPTION, SKU, DIMENSIONS, WEIGHT FROM products WHERE PRODUCTID = %s", (product_id,))
        return cursor.fetchone()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Fetch the maximum product ID
def fetch_max_product_id(user, password):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(PRODUCTID) FROM products")
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Insert a new product
def insert_product(user, password, product_id, product_name, category, brand, price, description, sku, dimensions, weight):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (PRODUCTID, PRODUCTNAME, CATEGORY, BRAND, PRICE, DESCRIPTION, SKU, DIMENSIONS, WEIGHT) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (product_id, product_name, category, brand, price, description, sku, dimensions, weight))
        conn.commit()
        print(f"Inserted product ID: {product_id}")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Update an existing product
def update_product(user, password, product_id, product_name, category, brand, price, description, sku, dimensions, weight):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE products
            SET PRODUCTNAME = %s, CATEGORY = %s, BRAND = %s, PRICE = %s, DESCRIPTION = %s, SKU = %s, DIMENSIONS = %s, WEIGHT = %s
            WHERE PRODUCTID = %s
        """, (product_name, category, brand, price, description, sku, dimensions, weight, product_id))
        conn.commit()
        print(f"Updated product ID: {product_id}")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Delete a product
def delete_product(user, password, product_id):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE PRODUCTID = %s", (product_id,))
        conn.commit()
        print(f"Deleted product ID: {product_id}")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Route to display all products
@product_bp.route('/dsproduct')
def dsproduct():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return "Error: Missing credentials", 401
    
    try:
        products = fetch_products(user, password)
    except Exception as e:
        return f"Error: {str(e)}", 500

    return render_template('dsproduct.html', products=products)

# Route to get a product by ID
@product_bp.route('/get_product', methods=['GET'])
def get_product():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    product_id = request.args.get('productId')
    if not product_id:
        return jsonify({"success": False, "message": "Product ID is required"}), 400

    try:
        product = fetch_product_by_id(user, password, product_id)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    if product:
        return jsonify({
            "success": True,
            "product": {
                "productId": product[0],
                "productName": product[1],
                "category": product[2],
                "brand": product[3],
                "price": product[4],
                "description": product[5],
                "sku": product[6],
                "dimensions": product[7],
                "weight": product[8]
            }
        })
    else:
        return jsonify({"success": False, "message": "Product not found"}), 404

# Route to add a new product
@product_bp.route('/dsproduct/add', methods=['POST'])
def add_product():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    product_name = data.get('productName')
    category = data.get('category')
    brand = data.get('brand')
    price = data.get('price')
    description = data.get('description')
    sku = data.get('sku')
    dimensions = data.get('dimensions')
    weight = data.get('weight')
    
    if not (product_name and category and brand and price and description and sku and dimensions and weight):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        max_id = fetch_max_product_id(user, password)
        new_product_id = max_id + 1
        insert_product(user, password, new_product_id, product_name, category, brand, price, description, sku, dimensions, weight)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 201

# Route to update an existing product
@product_bp.route('/dsproduct/update_product', methods=['POST'])
def update_product_route():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    product_id = data.get('productId')
    product_name = data.get('productName')
    category = data.get('category')
    brand = data.get('brand')
    price = data.get('price')
    description = data.get('description')
    sku = data.get('sku')
    dimensions = data.get('dimensions')
    weight = data.get('weight')

    if not (product_id and product_name and category and brand and price and description and sku and dimensions and weight):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        update_product(user, password, product_id, product_name, category, brand, price, description, sku, dimensions, weight)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True})

# Route to delete a product
@product_bp.route('/dsproduct/delete_product', methods=['POST'])
def delete_product_route():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    product_id = data.get('productId')

    if not product_id:
        return jsonify({"success": False, "message": "Product ID is required"}), 400

    try:
        delete_product(user, password, product_id)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True})
