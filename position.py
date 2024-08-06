import os
from flask import Blueprint, render_template, request, jsonify
import snowflake.connector
from config import Config

position_bp = Blueprint('position', __name__)

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

# Fetch all positions
def fetch_positions(user, password):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT POSITIONID, PLANOGRAMID, UPC, XCOORDINATE, YCOORDINATE, ZCOORDINATE, FACING, SHELFLEVEL 
            FROM POSITIONS
        """)
        return cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Fetch position by ID
def fetch_position_by_id(user, password, position_id):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT POSITIONID, PLANOGRAMID, UPC, XCOORDINATE, YCOORDINATE, ZCOORDINATE, FACING, SHELFLEVEL 
            FROM POSITIONS 
            WHERE POSITIONID = %s
        """, (position_id,))
        return cursor.fetchone()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Insert a new position
def insert_position(user, password, planogram_id, upc, x_coordinate, y_coordinate, z_coordinate, facing, shelf_level):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO POSITIONS (PLANOGRAMID, UPC, XCOORDINATE, YCOORDINATE, ZCOORDINATE, FACING, SHELFLEVEL) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (planogram_id, upc, x_coordinate, y_coordinate, z_coordinate, facing, shelf_level))
        conn.commit()
        print(f"Inserted position")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Update an existing position
def update_position(user, password, position_id, planogram_id, upc, x_coordinate, y_coordinate, z_coordinate, facing, shelf_level):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE POSITIONS
            SET PLANOGRAMID = %s, UPC = %s, XCOORDINATE = %s, YCOORDINATE = %s, ZCOORDINATE = %s, FACING = %s, SHELFLEVEL = %s
            WHERE POSITIONID = %s
        """, (planogram_id, upc, x_coordinate, y_coordinate, z_coordinate, facing, shelf_level, position_id))
        conn.commit()
        print(f"Updated position ID: {position_id}")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Delete a position
def delete_position(user, password, position_id):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM POSITIONS WHERE POSITIONID = %s", (position_id,))
        conn.commit()
        print(f"Deleted position ID: {position_id}")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Route to display all positions
@position_bp.route('/dsposition')
def dsposition():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return "Error: Missing credentials", 401
    
    try:
        positions = fetch_positions(user, password)
    except Exception as e:
        return f"Error: {str(e)}", 500

    return render_template('dsposition.html', positions=positions)

# Route to get a position by ID
@position_bp.route('/get_position', methods=['GET'])
def get_position():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    position_id = request.args.get('positionId')
    if not position_id:
        return jsonify({"success": False, "message": "Position ID is required"}), 400

    try:
        position = fetch_position_by_id(user, password, position_id)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    if position:
        return jsonify({
            "success": True,
            "position": {
                "positionId": position[0],
                "planogramId": position[1],
                "upc": position[2],
                "xCoordinate": position[3],
                "yCoordinate": position[4],
                "zCoordinate": position[5],
                "facing": position[6],
                "shelfLevel": position[7]
            }
        })
    else:
        return jsonify({"success": False, "message": "Position not found"}), 404

# Route to add a new position
@position_bp.route('/dsposition/add', methods=['POST'])
def add_position():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    planogram_id = data.get('planogramId')
    upc = data.get('upc')
    x_coordinate = data.get('xCoordinate')
    y_coordinate = data.get('yCoordinate')
    z_coordinate = data.get('zCoordinate')
    facing = data.get('facing')
    shelf_level = data.get('shelfLevel')
    
    if not (planogram_id and upc and x_coordinate and y_coordinate and z_coordinate and facing and shelf_level):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        insert_position(user, password, planogram_id, upc, x_coordinate, y_coordinate, z_coordinate, facing, shelf_level)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200

# Route to update an existing position
@position_bp.route('/dsposition/update_position', methods=['POST'])
def update_position_route():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    position_id = data.get('positionId')
    planogram_id = data.get('planogramId')
    upc = data.get('upc')
    x_coordinate = data.get('xCoordinate')
    y_coordinate = data.get('yCoordinate')
    z_coordinate = data.get('zCoordinate')
    facing = data.get('facing')
    shelf_level = data.get('shelfLevel')

    if not (position_id and planogram_id and upc and x_coordinate and y_coordinate and z_coordinate and facing and shelf_level):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        update_position(user, password, position_id, planogram_id, upc, x_coordinate, y_coordinate, z_coordinate, facing, shelf_level)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200

# Route to delete a position
@position_bp.route('/dsposition/delete_position', methods=['POST'])
def delete_position_route():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    position_id = data.get('positionId')

    if not position_id:
        return jsonify({"success": False, "message": "Position ID is required"}), 400

    try:
        delete_position(user, password, position_id)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200
