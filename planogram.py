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

# Fetch all planogram records
def fetch_planograms(user, password):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DBKEY, PLANOGRAMNAME, PDFPATH, DBSTATUS
            FROM NEWCKB.PUBLIC.IX_SPC_PLANOGRAM
        """)
        return cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Fetch planogram record by ID
def fetch_planogram_by_id(user, password, planogram_id):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DBKEY, PLANOGRAMNAME, PDFPATH, DBSTATUS
            FROM NEWCKB.PUBLIC.IX_SPC_PLANOGRAM
            WHERE DBKEY = %s
        """, (planogram_id,))
        return cursor.fetchone()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Insert a new planogram record
def insert_planogram(user, password, planogramname, pdfpath, dbstatus):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO NEWCKB.PUBLIC.IX_SPC_PLANOGRAM (PLANOGRAMNAME, PDFPATH, DBSTATUS)
            VALUES (%s, %s, %s)
        """, (planogramname, pdfpath, dbstatus))
        conn.commit()
        print(f"Inserted planogram record")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Update an existing planogram record
def update_planogram(user, password, planogram_id, planogramname, pdfpath, dbstatus):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE NEWCKB.PUBLIC.IX_SPC_PLANOGRAM
            SET PLANOGRAMNAME = %s, PDFPATH = %s, DBSTATUS = %s
            WHERE DBKEY = %s
        """, (planogramname, pdfpath, dbstatus, planogram_id))
        conn.commit()
        print(f"Updated planogram record ID: {planogram_id}")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Delete a planogram record
def delete_planogram(user, password, planogram_id):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM NEWCKB.PUBLIC.IX_SPC_PLANOGRAM WHERE DBKEY = %s", (planogram_id,))
        conn.commit()
        print(f"Deleted planogram record ID: {planogram_id}")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Route to display all planogram records
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

# Route to get a planogram record by ID
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
                "dbKey": planogram[0],
                "planogramName": planogram[1],
                "pdfPath": planogram[2],
                "dbStatus": planogram[3]
            }
        })
    else:
        return jsonify({"success": False, "message": "Planogram record not found"}), 404

# Route to add a new planogram record
@planogram_bp.route('/dsplanogram/add', methods=['POST'])
def add_planogram():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    planogramname = data.get('planogramName')
    pdfpath = data.get('pdfPath')
    dbstatus = data.get('dbStatus', 1)  # Default to 1 if not provided

    if not (planogramname and pdfpath and dbstatus is not None):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        insert_planogram(user, password, planogramname, pdfpath, dbstatus)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200

# Route to update an existing planogram record
@planogram_bp.route('/dsplanogram/update_planogram', methods=['POST'])
def update_planogram_route():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    dbkey = data.get('dbKey')
    planogramname = data.get('planogramName')
    pdfpath = data.get('pdfPath')
    dbstatus = data.get('dbStatus')

    if not (dbkey and planogramname and pdfpath and dbstatus is not None):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        update_planogram(user, password, dbkey, planogramname, pdfpath, dbstatus)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200

# Route to delete a planogram record
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

@planogram_bp.route('/flplanogram')
def flplanogram():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')

    if not user or not password:
        return "Error: Missing credentials", 401

    floorplan_id = request.args.get('floorplanId')
    if not floorplan_id:
        return "Error: Floorplan ID is required", 400
    
    try:
        # Establish Snowflake connection
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()

        # Query to get the planograms associated with the given floorplan
        cursor.execute("""
            SELECT P.DBKEY, P.PLANOGRAMNAME, P.PDFPATH, P.DBSTATUS
            FROM NEWCKB.PUBLIC.IX_SPC_PLANOGRAM P
            JOIN NEWCKB.PUBLIC.IX_FLR_PERFORMANCE FP
            ON P.DBKEY = FP.DBPLANOGRAMPARENTKEY
            WHERE FP.DBFLOORPLANPARENTKEY = %s
        """, (floorplan_id,))
        planograms = cursor.fetchall()

        # Query to get all planograms (possibly for display or selection purposes)
        cursor.execute("SELECT DBKEY, PLANOGRAMNAME, PDFPATH, DBSTATUS FROM NEWCKB.PUBLIC.IX_SPC_PLANOGRAM")
        all_planograms = cursor.fetchall()

        # Render the template with the retrieved data
        return render_template('flplanogram.html', planograms=planograms, all_planograms=all_planograms, floorplan_id=floorplan_id)

    except Exception as e:
        return f"Error: {str(e)}", 500

@planogram_bp.route('/flplanogram/add_planogram', methods=['POST'])
def add_planogram_to_floorplan():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')

    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    floorplan_id = data.get('floorplanId')
    planogram_id = data.get('planogramId')

    if not (floorplan_id and planogram_id):
        return jsonify({"success": False, "message": "Floorplan ID and Planogram ID are required"}), 400

    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()

        # Check if the planogram is already associated with the floorplan
        cursor.execute("""
            SELECT COUNT(*)
            FROM NEWCKB.PUBLIC.IX_FLR_PERFORMANCE
            WHERE DBFLOORPLANPARENTKEY = %s AND DBPLANOGRAMPARENTKEY = %s
        """, (floorplan_id, planogram_id))
        exists = cursor.fetchone()[0] > 0

        if exists:
            return jsonify({"success": False, "message": "The planogram is already associated with the floorplan"}), 400

        # Insert the new association if it doesn't exist
        cursor.execute("""
            INSERT INTO NEWCKB.PUBLIC.IX_FLR_PERFORMANCE (DBFLOORPLANPARENTKEY, DBPLANOGRAMPARENTKEY, CAPACITY)
            VALUES (%s, %s, 0)
        """, (floorplan_id, planogram_id))
        conn.commit()

        return jsonify({"success": True}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        if conn:
            conn.close()

@planogram_bp.route('/flplanogram/delete_planogram', methods=['POST'])
def delete_planogram_from_floorplan():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    floorplan_id = data.get('floorplanId')
    planogram_id = data.get('planogramId')

    if not (floorplan_id and planogram_id):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        delete_planogram_from_floorplan(user, password, floorplan_id, planogram_id)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def insert_planogram_to_floorplan(user, password, floorplan_id, planogram_id):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()

        # Check if the relationship already exists
        cursor.execute("""
            SELECT COUNT(*)
            FROM NEWCKB.PUBLIC.IX_FLR_PERFORMANCE
            WHERE DBFLOORPLANPARENTKEY = %s AND DBPLANOGRAMPARENTKEY = %s
        """, (floorplan_id, planogram_id))
        exists = cursor.fetchone()[0] > 0

        if exists:
            raise ValueError("The relationship already exists")

        # Insert the new entry if it doesn't exist
        cursor.execute("""
            INSERT INTO NEWCKB.PUBLIC.IX_FLR_PERFORMANCE (DBFLOORPLANPARENTKEY, DBPLANOGRAMPARENTKEY, CAPACITY)
            VALUES (%s, %s, 0)
        """, (floorplan_id, planogram_id))
        conn.commit()

    except Exception as e:
        raise e

    finally:
        if conn:
            conn.close()

def delete_planogram_from_floorplan(user, password, floorplan_id, planogram_id):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM NEWCKB.PUBLIC.IX_FLR_PERFORMANCE
            WHERE DBFLOORPLANPARENTKEY = %s AND DBPLANOGRAMPARENTKEY = %s
        """, (floorplan_id, planogram_id))
        conn.commit()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()
