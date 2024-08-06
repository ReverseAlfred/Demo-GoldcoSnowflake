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
            SELECT FloorPlanID, StoreID, FloorPlanDescription, LayoutImage, Dimensions 
            FROM FloorPlans
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
            SELECT FloorPlanID, StoreID, FloorPlanDescription, LayoutImage, Dimensions 
            FROM FloorPlans 
            WHERE FloorPlanID = %s
        """, (floor_plan_id,))
        return cursor.fetchone()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Insert a new floor plan
def insert_floor_plan(user, password, store_id, description, layout_image, dimensions):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO FloorPlans (StoreID, FloorPlanDescription, LayoutImage, Dimensions) 
            VALUES (%s, %s, %s, %s)
        """, (store_id, description, layout_image, dimensions))
        conn.commit()
        print(f"Inserted floor plan")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Update an existing floor plan
def update_floor_plan(user, password, floor_plan_id, store_id, description, layout_image, dimensions):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE FloorPlans
            SET StoreID = %s, FloorPlanDescription = %s, LayoutImage = %s, Dimensions = %s
            WHERE FloorPlanID = %s
        """, (store_id, description, layout_image, dimensions, floor_plan_id))
        conn.commit()
        print(f"Updated floor plan ID: {floor_plan_id}")
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
        cursor.execute("DELETE FROM FloorPlans WHERE FloorPlanID = %s", (floor_plan_id,))
        conn.commit()
        print(f"Deleted floor plan ID: {floor_plan_id}")
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
                "storeId": floor_plan[1],
                "description": floor_plan[2],
                "layoutImage": floor_plan[3],
                "dimensions": floor_plan[4]
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
    store_id = data.get('storeId')
    description = data.get('description')
    layout_image = data.get('layoutImage')
    dimensions = data.get('dimensions')
    
    if not (store_id and description and layout_image and dimensions):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        insert_floor_plan(user, password, store_id, description, layout_image, dimensions)
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
    store_id = data.get('storeId')
    description = data.get('description')
    layout_image = data.get('layoutImage')
    dimensions = data.get('dimensions')

    if not (floor_plan_id and store_id and description and layout_image and dimensions):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        update_floor_plan(user, password, floor_plan_id, store_id, description, layout_image, dimensions)
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
