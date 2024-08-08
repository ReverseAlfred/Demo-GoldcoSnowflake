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
            SELECT DBKEY, DBPRODUCTPARENTKEY, DBPLANOGRAMPARENTKEY, DBFIXTUREPARENTKEY, HFACING, VFACING, DFACING 
            FROM NEWCKB.PUBLIC.IX_SPC_POSITION
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
            SELECT DBKEY, DBPRODUCTPARENTKEY, DBPLANOGRAMPARENTKEY, DBFIXTUREPARENTKEY, HFACING, VFACING, DFACING 
            FROM NEWCKB.PUBLIC.IX_SPC_POSITION 
            WHERE DBKEY = %s
        """, (position_id,))
        return cursor.fetchone()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Insert a new position
def insert_position(user, password, db_product_parent_key, db_planogram_parent_key, db_fixture_parent_key, h_facing, v_facing, d_facing):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO NEWCKB.PUBLIC.IX_SPC_POSITION (DBPRODUCTPARENTKEY, DBPLANOGRAMPARENTKEY, DBFIXTUREPARENTKEY, HFACING, VFACING, DFACING) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (db_product_parent_key, db_planogram_parent_key, db_fixture_parent_key, h_facing, v_facing, d_facing))
        conn.commit()
        print(f"Inserted position")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Update an existing position
def update_position(user, password, position_id, db_product_parent_key, db_planogram_parent_key, db_fixture_parent_key, h_facing, v_facing, d_facing):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE NEWCKB.PUBLIC.IX_SPC_POSITION
            SET DBPRODUCTPARENTKEY = %s, DBPLANOGRAMPARENTKEY = %s, DBFIXTUREPARENTKEY = %s, HFACING = %s, VFACING = %s, DFACING = %s
            WHERE DBKEY = %s
        """, (db_product_parent_key, db_planogram_parent_key, db_fixture_parent_key, h_facing, v_facing, d_facing, position_id))
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
        cursor.execute("DELETE FROM NEWCKB.PUBLIC.IX_SPC_POSITION WHERE DBKEY = %s", (position_id,))
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
                "dbProductParentKey": position[1],
                "dbPlanogramParentKey": position[2],
                "dbFixtureParentKey": position[3],
                "hFacing": position[4],
                "vFacing": position[5],
                "dFacing": position[6]
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
    db_product_parent_key = data.get('dbProductParentKey')
    db_planogram_parent_key = data.get('dbPlanogramParentKey')
    db_fixture_parent_key = data.get('dbFixtureParentKey')
    h_facing = data.get('hFacing')
    v_facing = data.get('vFacing')
    d_facing = data.get('dFacing')
    
    if not (db_product_parent_key and db_planogram_parent_key and db_fixture_parent_key and h_facing and v_facing and d_facing):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        insert_position(user, password, db_product_parent_key, db_planogram_parent_key, db_fixture_parent_key, h_facing, v_facing, d_facing)
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
    db_product_parent_key = data.get('dbProductParentKey')
    db_planogram_parent_key = data.get('dbPlanogramParentKey')
    db_fixture_parent_key = data.get('dbFixtureParentKey')
    h_facing = data.get('hFacing')
    v_facing = data.get('vFacing')
    d_facing = data.get('dFacing')

    if not (position_id and db_product_parent_key and db_planogram_parent_key and db_fixture_parent_key and h_facing and v_facing and d_facing):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        update_position(user, password, position_id, db_product_parent_key, db_planogram_parent_key, db_fixture_parent_key, h_facing, v_facing, d_facing)
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
