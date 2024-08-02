import os
from flask import Blueprint, render_template, request, jsonify
import snowflake.connector
from config import Config

store_bp = Blueprint('store', __name__)

def get_snowflake_connection(user, password):
    conn = snowflake.connector.connect(
        user=user,
        password=password,
        account=Config.SNOWFLAKE_ACCOUNT,
        warehouse=Config.SNOWFLAKE_WAREHOUSE,
        database=Config.SNOWFLAKE_DATABASE,
        schema=Config.SNOWFLAKE_SCHEMA
    )
    return conn

@store_bp.route('/dsstore')
def dsstore():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return "Error: Missing credentials", 401
    
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("SELECT STOREID, STORENAME, LOCATION, SIZE, MANAGER, CONTACTINFO FROM stores")
        stores = cursor.fetchall()
    except Exception as e:
        return f"Error: {str(e)}", 500
    finally:
        if conn:
            conn.close()

    return render_template('dsstore.html', stores=stores)

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
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT STOREID, STORENAME, LOCATION, SIZE, MANAGER, CONTACTINFO 
            FROM stores 
            WHERE STOREID = %s
        """, (store_id,))
        store = cursor.fetchone()
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if conn:
            conn.close()

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

@store_bp.route('/dsstore/add', methods=['POST'])
def add_store():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()  # This method is more robust
    print(f"Received data: {data}")  # Log received data

    store_name = data.get('storeName')
    location = data.get('location')
    size = data.get('size')
    manager = data.get('manager')
    contact_info = data.get('contactInfo')
    
    if not (store_name and location and size and manager and contact_info):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO stores (STORENAME, LOCATION, SIZE, MANAGER, CONTACTINFO) 
            VALUES (%s, %s, %s, %s, %s)
        """, (store_name, location, size, manager, contact_info))
        conn.commit()
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if conn:
            conn.close()

    return jsonify({"success": True}), 200

@store_bp.route('/dsstore/update_store', methods=['POST'])
def update_store():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    print(f"Received data: {data}")  # Log received data

    store_id = data.get('storeId')
    store_name = data.get('storeName')
    location = data.get('location')
    size = data.get('size')
    manager = data.get('manager')
    contact_info = data.get('contactInfo')

    if not (store_id and store_name and location and size and manager and contact_info):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE stores
            SET STORENAME = %s, LOCATION = %s, SIZE = %s, MANAGER = %s, CONTACTINFO = %s
            WHERE STOREID = %s
        """, (store_name, location, size, manager, contact_info, store_id))
        conn.commit()
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if conn:
            conn.close()

    return jsonify({"success": True}), 200

@store_bp.route('/dsstore/delete_store', methods=['POST'])
def delete_store():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    print(f"Received data: {data}")  # Log received data

    store_id = data.get('storeId')

    if not store_id:
        return jsonify({"success": False, "message": "Store ID is required"}), 400

    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM stores 
            WHERE STOREID = %s
        """, (store_id,))
        conn.commit()
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if conn:
            conn.close()

    return jsonify({"success": True}), 200
