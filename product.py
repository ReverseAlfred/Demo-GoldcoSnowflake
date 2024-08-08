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
        cursor.execute("SELECT UPC, PRODUCTNAME, CATEGORY, SUBCATEGORY, DIMENSIONS, WEIGHT, DBSTATUS FROM ITX_SPC_PRODUCT")
        return cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Fetch product by UPC
def fetch_product_by_upc(user, password, upc):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("SELECT UPC, PRODUCTNAME, CATEGORY, SUBCATEGORY, DIMENSIONS, WEIGHT, DBSTATUS FROM ITX_SPC_PRODUCT WHERE UPC = %s", (upc,))
        return cursor.fetchone()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Insert a new product
def insert_product(user, password, upc, product_name, category, subcategory, dimensions, weight, dbstatus):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ITX_SPC_PRODUCT (UPC, PRODUCTNAME, CATEGORY, SUBCATEGORY, DIMENSIONS, WEIGHT, DBSTATUS) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (upc, product_name, category, subcategory, dimensions, weight, dbstatus))
        conn.commit()
        print(f"Inserted product UPC: {upc}")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Update an existing product
def update_product(user, password, upc, product_name, category, subcategory, dimensions, weight, dbstatus):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE ITX_SPC_PRODUCT
            SET PRODUCTNAME = %s, CATEGORY = %s, SUBCATEGORY = %s, DIMENSIONS = %s, WEIGHT = %s, DBSTATUS = %s
            WHERE UPC = %s
        """, (product_name, category, subcategory, dimensions, weight, dbstatus, upc))
        conn.commit()
        print(f"Updated product UPC: {upc}")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Delete a product
def delete_product(user, password, upc):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ITX_SPC_PRODUCT WHERE UPC = %s", (upc,))
        conn.commit()
        print(f"Deleted product UPC: {upc}")
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

# Route to get a product by UPC
@product_bp.route('/get_product', methods=['GET'])
def get_product():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    upc = request.args.get('upc')
    if not upc:
        return jsonify({"success": False, "message": "UPC is required"}), 400

    try:
        product = fetch_product_by_upc(user, password, upc)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    if product:
        return jsonify({
            "success": True,
            "product": {
                "upc": product[0],
                "productName": product[1],
                "category": product[2],
                "subcategory": product[3],
                "dimensions": product[4],
                "weight": product[5],
                "dbstatus": product[6]
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
    upc = data.get('upc')
    product_name = data.get('productName')
    category = data.get('category')
    subcategory = data.get('subcategory')
    dimensions = data.get('dimensions')
    weight = data.get('weight')
    dbstatus = data.get('dbstatus')
    
    if not (upc and product_name and category and subcategory and dimensions and weight and dbstatus):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        insert_product(user, password, upc, product_name, category, subcategory, dimensions, weight, dbstatus)
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
    upc = data.get('upc')
    product_name = data.get('productName')
    category = data.get('category')
    subcategory = data.get('subcategory')
    dimensions = data.get('dimensions')
    weight = data.get('weight')
    dbstatus = data.get('dbstatus')

    if not (upc and product_name and category and subcategory and dimensions and weight and dbstatus):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        update_product(user, password, upc, product_name, category, subcategory, dimensions, weight, dbstatus)
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
    upc = data.get('upc')

    if not upc:
        return jsonify({"success": False, "message": "UPC is required"}), 400

    try:
        delete_product(user, password, upc)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True})
