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
        cursor.execute("SELECT DBKEY, STORENAME, DESCRIPTIVO1, DBSTATUS FROM IX_STR_STORE")
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
        cursor.execute("SELECT DBKEY, STORENAME, DESCRIPTIVO1, DBSTATUS FROM IX_STR_STORE WHERE DBKEY = %s", (store_id,))
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
        cursor.execute("SELECT MAX(DBKEY) FROM IX_STR_STORE")
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Insert a new store
def insert_store(user, password, store_name, descriptivo1, dbstatus):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO IX_STR_STORE (STORENAME, DESCRIPTIVO1, DBSTATUS) 
            VALUES (%s, %s, %s)
        """, (store_name, descriptivo1, dbstatus))
        conn.commit()
        print(f"Inserted store")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Update an existing store
def update_store(user, password, store_id, store_name, descriptivo1, dbstatus):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE IX_STR_STORE
            SET STORENAME = %s, DESCRIPTIVO1 = %s, DBSTATUS = %s
            WHERE DBKEY = %s
        """, (store_name, descriptivo1, dbstatus, store_id))
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
        cursor.execute("DELETE FROM IX_STR_STORE WHERE DBKEY = %s", (store_id,))
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
                "descriptivo1": store[2],
                "dbStatus": store[3]
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
    descriptivo1 = data.get('descriptivo1')
    dbstatus = data.get('dbStatus')
    
    if not (store_name and descriptivo1 is not None and dbstatus is not None):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        insert_store(user, password, store_name, descriptivo1, dbstatus)
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
    descriptivo1 = data.get('descriptivo1')
    dbstatus = data.get('dbStatus')

    if not (store_id and store_name and descriptivo1 is not None and dbstatus is not None):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        update_store(user, password, store_id, store_name, descriptivo1, dbstatus)
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
