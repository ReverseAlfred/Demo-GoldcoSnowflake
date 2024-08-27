import os
from flask import Blueprint, render_template, request, jsonify
import snowflake.connector
from config import Config

product_bp = Blueprint('product', __name__)

# Helper function to establish a Snowflake connection
def get_snowflake_connection(user, password):
    """Establishes a connection to the Snowflake database."""
    return snowflake.connector.connect(
        user=user,
        password=password,
        account=Config.SNOWFLAKE_ACCOUNT,
        warehouse=Config.SNOWFLAKE_WAREHOUSE,
        database=Config.SNOWFLAKE_DATABASE,
        schema=Config.SNOWFLAKE_SCHEMA
    )

# Database operation functions

def fetch_products(user, password):
    """Fetches all products from the database."""
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT UPC, PRODUCTNAME, CATEGORY, SUBCATEGORY, DIMENSIONS, WEIGHT, DBSTATUS 
            FROM ITX_SPC_PRODUCT
        """)
        return cursor.fetchall()
    finally:
        if conn:
            conn.close()

def fetch_product_by_upc(user, password, upc):
    """Fetches a single product by UPC."""
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT UPC, PRODUCTNAME, CATEGORY, SUBCATEGORY, DIMENSIONS, WEIGHT, DBSTATUS 
            FROM ITX_SPC_PRODUCT WHERE UPC = %s
        """, (upc,))
        return cursor.fetchone()
    finally:
        if conn:
            conn.close()

def fetch_dbkey_by_upc(user, password, upc):
    """Fetches the DBKEY of a product by its UPC."""
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("SELECT DBKEY FROM ITX_SPC_PRODUCT WHERE UPC = %s", (upc,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            raise ValueError("UPC not found")
    finally:
        if conn:
            conn.close()

def insert_product(user, password, upc, product_name, category, subcategory, dimensions, weight, dbstatus):
    """Inserts a new product into the database."""
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ITX_SPC_PRODUCT (UPC, PRODUCTNAME, CATEGORY, SUBCATEGORY, DIMENSIONS, WEIGHT, DBSTATUS) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (upc, product_name, category, subcategory, dimensions, weight, dbstatus))
        conn.commit()
    finally:
        if conn:
            conn.close()

def update_product(user, password, upc, product_name, category, subcategory, dimensions, weight, dbstatus):
    """Updates an existing product."""
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
    finally:
        if conn:
            conn.close()

def delete_product(user, password, upc):
    """Deletes a product from the database."""
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ITX_SPC_PRODUCT WHERE UPC = %s", (upc,))
        conn.commit()
    finally:
        if conn:
            conn.close()

def fetch_products_by_planogram(user, password, planogram_id):
    """Fetches products associated with a specific planogram."""
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.UPC, p.PRODUCTNAME, p.CATEGORY, p.SUBCATEGORY, p.DIMENSIONS, p.WEIGHT
            FROM IX_SPC_POSITION pos
            JOIN ITX_SPC_PRODUCT p ON pos.DBProductParentKey = p.DBKEY
            WHERE pos.DBPlanogramParentKey = %s
        """, (planogram_id,))
        return cursor.fetchall()
    finally:
        if conn:
            conn.close()

def fetch_all_products(user, password):
    """Fetches all products (for displaying alongside planogram-specific products)."""
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("SELECT DBKEY, UPC, PRODUCTNAME FROM ITX_SPC_PRODUCT")
        return cursor.fetchall()
    finally:
        if conn:
            conn.close()

def insert_product_to_planogram(user, password, planogram_id, product_id):
    """Inserts a product into a planogram."""
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        # Ensure the product isn't already in the planogram
        cursor.execute("""
            SELECT COUNT(*)
            FROM IX_SPC_POSITION
            WHERE DBPlanogramParentKey = %s AND DBProductParentKey = %s
        """, (planogram_id, product_id))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO IX_SPC_POSITION (DBPlanogramParentKey, DBProductParentKey, DBFixtureParentKey, HFacing, VFacing, DFacing)
                VALUES (%s, %s, 0, 0, 0, 0)
            """, (planogram_id, product_id))
            conn.commit()
    finally:
        if conn:
            conn.close()

def delete_product_from_planogram(user, password, planogram_id, product_id):
    """Deletes a product from a planogram."""
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM IX_SPC_POSITION
            WHERE DBPlanogramParentKey = %s AND DBProductParentKey = %s
        """, (planogram_id, product_id))
        conn.commit()
    finally:
        if conn:
            conn.close()

# Routes

@product_bp.route('/dsproduct')
def dsproduct():
    """Route to display all products."""
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return "Error: Missing credentials", 401
    
    try:
        products = fetch_products(user, password)
    except Exception as e:
        return f"Error: {str(e)}", 500

    return render_template('dsproduct.html', products=products)

@product_bp.route('/get_product', methods=['GET'])
def get_product():
    """Route to get a product by UPC."""
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

@product_bp.route('/dsproduct/add', methods=['POST'])
def add_product():
    """Route to add a new product."""
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

@product_bp.route('/dsproduct/update_product', methods=['POST'])
def update_product_route():
    """Route to update an existing product."""
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

    return jsonify({"success": True}), 200

@product_bp.route('/dsproduct/delete_product', methods=['DELETE'])
def delete_product_route():
    """Route to delete a product."""
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    upc = request.json.get('upc')
    if not upc:
        return jsonify({"success": False, "message": "UPC is required"}), 400

    try:
        delete_product(user, password, upc)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200

@product_bp.route('/planogram/<int:planogram_id>')
def get_planogram_products(planogram_id):
    """Route to get products associated with a specific planogram."""
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')

    if not user or not password:
        return "Error: Missing credentials", 401
    
    try:
        products = fetch_products_by_planogram(user, password, planogram_id)
    except Exception as e:
        return f"Error: {str(e)}", 500

    return render_template('planogram_products.html', products=products)

@product_bp.route('/planogram/add', methods=['POST'])
def add_product_to_planogram_route():
    """Route to add a product to a planogram."""
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    planogram_id = data.get('planogramId')
    product_id = data.get('productId')

    if not (planogram_id and product_id):
        return jsonify({"success": False, "message": "Planogram ID and Product ID are required"}), 400

    try:
        insert_product_to_planogram(user, password, planogram_id, product_id)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 201

@product_bp.route('/planogram/delete', methods=['DELETE'])
def delete_product_from_planogram_route():
    """Route to remove a product from a planogram."""
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    planogram_id = data.get('planogramId')
    product_id = data.get('productId')

    if not (planogram_id and product_id):
        return jsonify({"success": False, "message": "Planogram ID and Product ID are required"}), 400

    try:
        delete_product_from_planogram(user, password, planogram_id, product_id)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200
