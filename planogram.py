import os
from flask import Blueprint, render_template, request, jsonify
import snowflake.connector
from config import Config

planogram_bp = Blueprint('planogram', __name__)

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

# Fetch all planograms
def fetch_planograms(user, password):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT PlanogramID, StoreID, FloorPlanID, PlanogramDescription, PlanogramImage, EffectiveDate, PDFPath 
            FROM Planograms
        """)
        return cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Fetch planogram by ID
def fetch_planogram_by_id(user, password, planogram_id):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT PlanogramID, StoreID, FloorPlanID, PlanogramDescription, PlanogramImage, EffectiveDate, PDFPath 
            FROM Planograms 
            WHERE PlanogramID = %s
        """, (planogram_id,))
        return cursor.fetchone()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Fetch the maximum planogram ID
def fetch_max_planogram_id(user, password):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(PlanogramID) FROM Planograms")
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Insert a new planogram
def insert_planogram(user, password, store_id, floor_plan_id, description, image, effective_date, pdf_path):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Planograms (StoreID, FloorPlanID, PlanogramDescription, PlanogramImage, EffectiveDate, PDFPath) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (store_id, floor_plan_id, description, image, effective_date, pdf_path))
        conn.commit()
        print(f"Inserted planogram")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Update an existing planogram
def update_planogram(user, password, planogram_id, store_id, floor_plan_id, description, image, effective_date, pdf_path):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Planograms
            SET StoreID = %s, FloorPlanID = %s, PlanogramDescription = %s, PlanogramImage = %s, EffectiveDate = %s, PDFPath = %s
            WHERE PlanogramID = %s
        """, (store_id, floor_plan_id, description, image, effective_date, pdf_path, planogram_id))
        conn.commit()
        print(f"Updated planogram ID: {planogram_id}")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Delete a planogram
def delete_planogram(user, password, planogram_id):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Planograms WHERE PlanogramID = %s", (planogram_id,))
        conn.commit()
        print(f"Deleted planogram ID: {planogram_id}")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Route to display all planograms
@planogram_bp.route('/dsplanogram')
def dsplanogram():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return "Error: Missing credentials", 401
    
    try:
        planograms = fetch_planograms(user, password)
    except Exception as e:
        return f"Error: {str(e)}", 500

    return render_template('dsplanogram.html', planograms=planograms)

# Route to get a planogram by ID
@planogram_bp.route('/get_planogram', methods=['GET'])
def get_planogram():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    planogram_id = request.args.get('planogramId')
    if not planogram_id:
        return jsonify({"success": False, "message": "Planogram ID is required"}), 400

    try:
        planogram = fetch_planogram_by_id(user, password, planogram_id)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    if planogram:
        return jsonify({
            "success": True,
            "planogram": {
                "planogramId": planogram[0],
                "storeId": planogram[1],
                "floorPlanId": planogram[2],
                "description": planogram[3],
                "image": planogram[4],
                "effectiveDate": planogram[5],
                "pdfPath": planogram[6]
            }
        })
    else:
        return jsonify({"success": False, "message": "Planogram not found"}), 404

# Route to add a new planogram
@planogram_bp.route('/dsplanogram/add', methods=['POST'])
def add_planogram():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    store_id = data.get('storeId')
    floor_plan_id = data.get('floorPlanId')
    description = data.get('description')
    image = data.get('image')
    effective_date = data.get('effectiveDate')
    pdf_path = data.get('pdfPath')
    
    if not (store_id and floor_plan_id and description and image and effective_date and pdf_path):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        insert_planogram(user, password, store_id, floor_plan_id, description, image, effective_date, pdf_path)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200

# Route to update an existing planogram
@planogram_bp.route('/dsplanogram/update_planogram', methods=['POST'])
def update_planogram_route():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    planogram_id = data.get('planogramId')
    store_id = data.get('storeId')
    floor_plan_id = data.get('floorPlanId')
    description = data.get('description')
    image = data.get('image')
    effective_date = data.get('effectiveDate')
    pdf_path = data.get('pdfPath')

    if not (planogram_id and store_id and floor_plan_id and description and image and effective_date and pdf_path):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        update_planogram(user, password, planogram_id, store_id, floor_plan_id, description, image, effective_date, pdf_path)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200

# Route to delete a planogram
@planogram_bp.route('/dsplanogram/delete_planogram', methods=['POST'])
def delete_planogram_route():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    planogram_id = data.get('planogramId')

    if not planogram_id:
        return jsonify({"success": False, "message": "Planogram ID is required"}), 400

    try:
        delete_planogram(user, password, planogram_id)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200
