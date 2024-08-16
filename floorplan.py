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

# Fetch all floor plans
def fetch_floor_plans(user, password):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DBKEY, FLOORPLANNAME, DBSTATUS 
            FROM IX_FLR_FLOORPLAN
        """)
        return cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Fetch floor plan by ID
def fetch_floor_plan_by_id(user, password, floor_plan_id):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DBKEY, FLOORPLANNAME, DBSTATUS 
            FROM IX_FLR_FLOORPLAN 
            WHERE DBKEY = :1
        """, (floor_plan_id,))
        return cursor.fetchone()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Insert a new floor plan
def insert_floor_plan(user, password, name, status):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO IX_FLR_FLOORPLAN (FLOORPLANNAME, DBSTATUS) 
            VALUES (:1, :2)
        """, (name, status))
        conn.commit()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Update an existing floor plan
def update_floor_plan(user, password, floor_plan_id, name, status):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE IX_FLR_FLOORPLAN
            SET FLOORPLANNAME = :1, DBSTATUS = :2
            WHERE DBKEY = :3
        """, (name, status, floor_plan_id))
        conn.commit()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Delete a floor plan
def delete_floor_plan(user, password, floor_plan_id):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM IX_FLR_FLOORPLAN WHERE DBKEY = :1
        """, (floor_plan_id,))
        conn.commit()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Route to display all floor plans
@floorplan_bp.route('/dsfloorplan')
def dsfloorplan():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return "Error: Missing credentials", 401
    
    try:
        floor_plans = fetch_floor_plans(user, password)
    except Exception as e:
        return f"Error: {str(e)}", 500

    return render_template('dsfloorplan.html', floor_plans=floor_plans)

# Route to get a floor plan by ID
@floorplan_bp.route('/get_floor_plan', methods=['GET'])
def get_floor_plan():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    floor_plan_id = request.args.get('floorPlanId')
    if not floor_plan_id:
        return jsonify({"success": False, "message": "Floor Plan ID is required"}), 400

    try:
        floor_plan = fetch_floor_plan_by_id(user, password, floor_plan_id)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    if floor_plan:
        return jsonify({
            "success": True,
            "floorPlan": {
                "floorPlanId": floor_plan[0],
                "floorPlanName": floor_plan[1],
                "dbStatus": floor_plan[2]
            }
        })
    else:
        return jsonify({"success": False, "message": "Floor Plan not found"}), 404

# Route to add a new floor plan
@floorplan_bp.route('/dsfloorplan/add', methods=['POST'])
def add_floor_plan():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    name = data.get('floorPlanName')
    status = data.get('dbStatus')
    
    if not (name and status is not None):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        insert_floor_plan(user, password, name, status)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200

# Route to update an existing floor plan
@floorplan_bp.route('/dsfloorplan/update_floor_plan', methods=['POST'])
def update_floor_plan_route():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    floor_plan_id = data.get('floorPlanId')
    name = data.get('floorPlanName')
    status = data.get('dbStatus')

    if not (floor_plan_id and name and status is not None):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        update_floor_plan(user, password, floor_plan_id, name, status)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200

# Route to delete a floor plan
@floorplan_bp.route('/dsfloorplan/delete_floor_plan', methods=['POST'])
def delete_floor_plan_route():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    floor_plan_id = data.get('floorPlanId')

    if not floor_plan_id:
        return jsonify({"success": False, "message": "Floor Plan ID is required"}), 400

    try:
        delete_floor_plan(user, password, floor_plan_id)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200

# Route to display floor plans for a store
@floorplan_bp.route('/stfloorplan')
def stfloorplan():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')

    if not user or not password:
        return "Error: Missing credentials", 401

    store_id = request.args.get('storeId')
    if not store_id:
        return "Error: Store ID is required", 400

    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()

        # Fetch floor plans associated with the store
        cursor.execute("""
            SELECT F.DBKEY, F.FLOORPLANNAME, F.DBSTATUS
            FROM IX_FLR_FLOORPLAN F
            JOIN IX_STR_STORE_FLOORPLAN SF
            ON F.DBKEY = SF.DBFLOORPLANPARENTKEY
            WHERE SF.DBSTOREPARENTKEY = %s
        """, (store_id,))
        floorplans = cursor.fetchall()

        # Fetch all floor plans for the dropdown or additional selections
        cursor.execute("SELECT DBKEY, FLOORPLANNAME, DBSTATUS FROM IX_FLR_FLOORPLAN")
        all_floorplans = cursor.fetchall()

        return render_template('stfloorplan.html', floorplans=floorplans, all_floorplans=all_floorplans, store_id=store_id)

    except Exception as e:
        return f"Error: {str(e)}", 500

    finally:
        if conn:
            conn.close()

# Route to add a floorplan to a store
@floorplan_bp.route('/stfloorplan/add_floorplan', methods=['POST'])
def add_floorplan_to_store():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    store_id = data.get('storeId')
    floorplan_id = data.get('floorplanId')
    
    if not (store_id and floorplan_id):
        return jsonify({"success": False, "message": "Store ID and Floorplan ID are required"}), 400

    conn = None
    cursor = None

    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        
        # Check if the relationship already exists
        check_query = """
        SELECT COUNT(*) 
        FROM IX_STR_STORE_FLOORPLAN 
        WHERE DBStoreParentKey = %s AND DBFloorplanParentKey = %s
        """
        cursor.execute(check_query, (store_id, floorplan_id))
        count = cursor.fetchone()[0]
        
        if count > 0:
            return jsonify({'message': 'Floorplan already associated with this store.'}), 400

        # Add the new floorplan to the store
        insert_query = """
        INSERT INTO IX_STR_STORE_FLOORPLAN (DBStoreParentKey, DBFloorplanParentKey) 
        VALUES (%s, %s)
        """
        cursor.execute(insert_query, (store_id, floorplan_id))

        return jsonify({'message': 'Floorplan added successfully.'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Route to remove a floorplan from a store
# Route to remove a floorplan from a store
@floorplan_bp.route('/stfloorplan/delete_floorplan', methods=['POST'])
def remove_floorplan_from_store():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    store_id = data.get('storeId')
    floorplan_id = data.get('floorplanId')

    if not (store_id and floorplan_id):
        return jsonify({"success": False, "message": "Store ID and Floorplan ID are required"}), 400

    conn = None
    cursor = None

    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        
        # Remove the floorplan from the store
        delete_query = """
        DELETE FROM IX_STR_STORE_FLOORPLAN 
        WHERE DBStoreParentKey = %s AND DBFloorplanParentKey = %s
        """
        cursor.execute(delete_query, (store_id, floorplan_id))
        conn.commit()

        # Check if any rows were affected
        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "No matching record found to delete."}), 404
        
        return jsonify({"success": True, "message": "Floorplan removed successfully."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to remove floorplan from store."}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()