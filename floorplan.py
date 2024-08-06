import os
from flask import Blueprint, render_template, request, jsonify
import snowflake.connector
from config import Config

floorplan_bp = Blueprint('floorplan', __name__)

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

# Fetch all floorplans
def fetch_floorplans(user, password):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT FLOORPLANID, STOREID, FLOORPLANDESCRIPTION, LAYOUTIMAGE, DIMENSIONS 
            FROM FLOORPLANS
        """)
        return cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Fetch floorplan by ID
def fetch_floorplan_by_id(user, password, floorplan_id):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT FLOORPLANID, STOREID, FLOORPLANDESCRIPTION, LAYOUTIMAGE, DIMENSIONS 
            FROM FLOORPLANS 
            WHERE FLOORPLANID = %s
        """, (floorplan_id,))
        return cursor.fetchone()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Fetch the maximum floorplan ID
def fetch_max_floorplan_id(user, password):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(FLOORPLANID) FROM FLOORPLANS")
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Insert a new floorplan
def insert_floorplan(user, password, store_id, floorplan_description, layout_image, dimensions):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO FLOORPLANS (STOREID, FLOORPLANDESCRIPTION, LAYOUTIMAGE, DIMENSIONS) 
            VALUES (%s, %s, %s, %s)
        """, (store_id, floorplan_description, layout_image, dimensions))
        conn.commit()
        print(f"Inserted floorplan")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Update an existing floorplan
def update_floorplan(user, password, floorplan_id, store_id, floorplan_description, layout_image, dimensions):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE FLOORPLANS
            SET STOREID = %s, FLOORPLANDESCRIPTION = %s, LAYOUTIMAGE = %s, DIMENSIONS = %s
            WHERE FLOORPLANID = %s
        """, (store_id, floorplan_description, layout_image, dimensions, floorplan_id))
        conn.commit()
        print(f"Updated floorplan ID: {floorplan_id}")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Delete a floorplan
def delete_floorplan(user, password, floorplan_id):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM FLOORPLANS WHERE FLOORPLANID = %s", (floorplan_id,))
        conn.commit()
        print(f"Deleted floorplan ID: {floorplan_id}")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Route to display all floorplans
@floorplan_bp.route('/dsfloorplan')
def dsfloorplan():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return "Error: Missing credentials", 401
    
    try:
        floorplans = fetch_floorplans(user, password)
    except Exception as e:
        return f"Error: {str(e)}", 500

    return render_template('dsfloorplan.html', floorplans=floorplans)

# Route to get a floorplan by ID
@floorplan_bp.route('/get_floorplan', methods=['GET'])
def get_floorplan():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    floorplan_id = request.args.get('floorplanId')
    if not floorplan_id:
        return jsonify({"success": False, "message": "Floorplan ID is required"}), 400

    try:
        floorplan = fetch_floorplan_by_id(user, password, floorplan_id)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    if floorplan:
        return jsonify({
            "success": True,
            "floorplan": {
                "floorplanId": floorplan[0],
                "storeId": floorplan[1],
                "floorplanDescription": floorplan[2],
                "layoutImage": floorplan[3],
                "dimensions": floorplan[4]
            }
        })
    else:
        return jsonify({"success": False, "message": "Floorplan not found"}), 404

# Route to add a new floorplan
@floorplan_bp.route('/dsfloorplan/add', methods=['POST'])
def add_floorplan():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    store_id = data.get('storeId')
    floorplan_description = data.get('floorplanDescription')
    layout_image = data.get('layoutImage')
    dimensions = data.get('dimensions')
    
    if not (store_id and floorplan_description and layout_image and dimensions):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        insert_floorplan(user, password, store_id, floorplan_description, layout_image, dimensions)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200

# Route to update an existing floorplan
@floorplan_bp.route('/dsfloorplan/update_floorplan', methods=['POST'])
def update_floorplan_route():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    floorplan_id = data.get('floorplanId')
    store_id = data.get('storeId')
    floorplan_description = data.get('floorplanDescription')
    layout_image = data.get('layoutImage')
    dimensions = data.get('dimensions')

    if not (floorplan_id and store_id and floorplan_description and layout_image and dimensions):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        update_floorplan(user, password, floorplan_id, store_id, floorplan_description, layout_image, dimensions)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200

# Route to delete a floorplan
@floorplan_bp.route('/dsfloorplan/delete_floorplan', methods=['POST'])
def delete_floorplan_route():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    floorplan_id = data.get('floorplanId')

    if not floorplan_id:
        return jsonify({"success": False, "message": "Floorplan ID is required"}), 400

    try:
        delete_floorplan(user, password, floorplan_id)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200
