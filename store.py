import os
from flask import Blueprint, render_template, request, jsonify
import snowflake.connector
from config import Config

store_bp = Blueprint('store', __name__)

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

# Fetch all stores
def fetch_stores(user, password):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("SELECT STOREID, STORENAME, LOCATION, SIZE, MANAGER, CONTACTINFO FROM stores")
        return cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Fetch store by ID
def fetch_store_by_id(user, password, store_id):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("SELECT STOREID, STORENAME, LOCATION, SIZE, MANAGER, CONTACTINFO FROM stores WHERE STOREID = %s", (store_id,))
        return cursor.fetchone()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Fetch the maximum store ID
def fetch_max_store_id(user, password):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(STOREID) FROM stores")
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Insert a new store
def insert_store(user, password, store_id, store_name, location, size, manager, contact_info):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO stores (STOREID, STORENAME, LOCATION, SIZE, MANAGER, CONTACTINFO) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (store_id, store_name, location, size, manager, contact_info))
        conn.commit()
        print(f"Inserted store ID: {store_id}")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Update an existing store
def update_store(user, password, store_id, store_name, location, size, manager, contact_info):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE stores
            SET STORENAME = %s, LOCATION = %s, SIZE = %s, MANAGER = %s, CONTACTINFO = %s
            WHERE STOREID = %s
        """, (store_name, location, size, manager, contact_info, store_id))
        conn.commit()
        print(f"Updated store ID: {store_id}")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Delete a store
def delete_store(user, password, store_id):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM stores WHERE STOREID = %s", (store_id,))
        conn.commit()
        print(f"Deleted store ID: {store_id}")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Route to display all stores
@store_bp.route('/dsstore')
def dsstore():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return "Error: Missing credentials", 401
    
    try:
        stores = fetch_stores(user, password)
    except Exception as e:
        return f"Error: {str(e)}", 500

    return render_template('dsstore.html', stores=stores)

# Route to get a store by ID
@store_bp.route('/get_store', methods=['GET'])
def get_store():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    store_id = request.args.get('storeId')
    if not store_id:
        return jsonify({"success": False, "message": "Store ID is required"}), 400

    try:
        store = fetch_store_by_id(user, password, store_id)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    if store:
        return jsonify({
            "success": True,
            "store": {
                "storeId": store[0],
                "storeName": store[1],
                "location": store[2],
                "size": store[3],
                "manager": store[4],
                "contactInfo": store[5]
            }
        })
    else:
        return jsonify({"success": False, "message": "Store not found"}), 404

# Route to add a new store
@store_bp.route('/dsstore/add', methods=['POST'])
def add_store():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    store_name = data.get('storeName')
    location = data.get('location')
    size = data.get('size')
    manager = data.get('manager')
    contact_info = data.get('contactInfo')
    
    if not (store_name and location and size and manager and contact_info):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        max_id = fetch_max_store_id(user, password)
        new_store_id = max_id + 1
        insert_store(user, password, new_store_id, store_name, location, size, manager, contact_info)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200

# Route to update an existing store
@store_bp.route('/dsstore/update_store', methods=['POST'])
def update_store_route():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    store_id = data.get('storeId')
    store_name = data.get('storeName')
    location = data.get('location')
    size = data.get('size')
    manager = data.get('manager')
    contact_info = data.get('contactInfo')

    if not (store_id and store_name and location and size and manager and contact_info):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        update_store(user, password, store_id, store_name, location, size, manager, contact_info)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200

# Route to delete a store
@store_bp.route('/dsstore/delete_store', methods=['POST'])
def delete_store_route():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    store_id = data.get('storeId')

    if not store_id:
        return jsonify({"success": False, "message": "Store ID is required"}), 400

    try:
        delete_store(user, password, store_id)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200
