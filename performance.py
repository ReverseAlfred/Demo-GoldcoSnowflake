import os
from flask import Blueprint, render_template, request, jsonify
import snowflake.connector
from config import Config
from datetime import datetime

performance_bp = Blueprint('performance', __name__)

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

# Fetch all performance records
def fetch_performances(user, password):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DBKEY, DBPLANOGRAMPARENTKEY, DBPRODUCTPARENTKEY, FACTINGS, CAPACITY, UNITMOVEMENT, SALES, MARGEN, COST
            FROM NEWCKB.PUBLIC.IX_SPC_PERFORMANCE
        """)
        return cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Fetch performance record by ID
def fetch_performance_by_id(user, password, performance_id):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DBKEY, DBPLANOGRAMPARENTKEY, DBPRODUCTPARENTKEY, FACTINGS, CAPACITY, UNITMOVEMENT, SALES, MARGEN, COST
            FROM NEWCKB.PUBLIC.IX_SPC_PERFORMANCE
            WHERE DBKEY = %s
        """, (performance_id,))
        return cursor.fetchone()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Insert a new performance record
def insert_performance(user, password, dbplanogramparentkey, dbproductparentkey, factings, capacity, unitmovement, sales, margen, cost):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO NEWCKB.PUBLIC.IX_SPC_PERFORMANCE (DBPLANOGRAMPARENTKEY, DBPRODUCTPARENTKEY, FACTINGS, CAPACITY, UNITMOVEMENT, SALES, MARGEN, COST)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (dbplanogramparentkey, dbproductparentkey, factings, capacity, unitmovement, sales, margen, cost))
        conn.commit()
        print(f"Inserted performance record")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Update an existing performance record
def update_performance(user, password, dbkey, dbplanogramparentkey, dbproductparentkey, factings, capacity, unitmovement, sales, margen, cost):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE NEWCKB.PUBLIC.IX_SPC_PERFORMANCE
            SET DBPLANOGRAMPARENTKEY = %s, DBPRODUCTPARENTKEY = %s, FACTINGS = %s, CAPACITY = %s, UNITMOVEMENT = %s, SALES = %s, MARGEN = %s, COST = %s
            WHERE DBKEY = %s
        """, (dbplanogramparentkey, dbproductparentkey, factings, capacity, unitmovement, sales, margen, cost, dbkey))
        conn.commit()
        print(f"Updated performance record ID: {dbkey}")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Delete a performance record
def delete_performance(user, password, performance_id):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM NEWCKB.PUBLIC.IX_SPC_PERFORMANCE WHERE DBKEY = %s", (performance_id,))
        conn.commit()
        print(f"Deleted performance record ID: {performance_id}")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Route to display all performance records
@performance_bp.route('/dsperformance')
def dsperformance():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return "Error: Missing credentials", 401
    
    try:
        performances = fetch_performances(user, password)
    except Exception as e:
        return f"Error: {str(e)}", 500

    return render_template('dsperformance.html', performances=performances)

# Route to get a performance record by ID
@performance_bp.route('/get_performance', methods=['GET'])
def get_performance():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    performance_id = request.args.get('performanceId')
    if not performance_id:
        return jsonify({"success": False, "message": "Performance ID is required"}), 400

    try:
        performance = fetch_performance_by_id(user, password, performance_id)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    if performance:
        return jsonify({
            "success": True,
            "performance": {
                "dbKey": performance[0],
                "dbPlanogramParentKey": performance[1],
                "dbProductParentKey": performance[2],
                "factings": performance[3],
                "capacity": performance[4],
                "unitMovement": performance[5],
                "sales": performance[6],
                "margen": performance[7],
                "cost": performance[8]
            }
        })
    else:
        return jsonify({"success": False, "message": "Performance record not found"}), 404

# Route to add a new performance record
@performance_bp.route('/dsperformance/add', methods=['POST'])
def add_performance():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    dbplanogramparentkey = data.get('dbPlanogramParentKey')
    dbproductparentkey = data.get('dbProductParentKey')
    factings = data.get('factings')
    capacity = data.get('capacity')
    unitmovement = data.get('unitMovement')
    sales = data.get('sales')
    margen = data.get('margen')
    cost = data.get('cost')
    
    if not (dbplanogramparentkey and dbproductparentkey and factings is not None and capacity is not None and unitmovement is not None and sales is not None and margen is not None and cost is not None):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        insert_performance(user, password, dbplanogramparentkey, dbproductparentkey, factings, capacity, unitmovement, sales, margen, cost)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200

# Route to update an existing performance record
@performance_bp.route('/dsperformance/update_performance', methods=['POST'])
def update_performance_route():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    dbkey = data.get('dbKey')
    dbplanogramparentkey = data.get('dbPlanogramParentKey')
    dbproductparentkey = data.get('dbProductParentKey')
    factings = data.get('factings')
    capacity = data.get('capacity')
    unitmovement = data.get('unitMovement')
    sales = data.get('sales')
    margen = data.get('margen')
    cost = data.get('cost')

    if not (dbkey and dbplanogramparentkey and dbproductparentkey and factings is not None and capacity is not None and unitmovement is not None and sales is not None and margen is not None and cost is not None):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        update_performance(user, password, dbkey, dbplanogramparentkey, dbproductparentkey, factings, capacity, unitmovement, sales, margen, cost)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200

# Route to delete a performance record
@performance_bp.route('/dsperformance/delete_performance', methods=['POST'])
def delete_performance_route():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    performance_id = data.get('dbKey')
    if not performance_id:
        return jsonify({"success": False, "message": "Performance ID is required"}), 400

    try:
        delete_performance(user, password, performance_id)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200
