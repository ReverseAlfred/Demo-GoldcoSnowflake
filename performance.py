import os
from flask import Blueprint, render_template, request, jsonify
import snowflake.connector
from config import Config

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
            SELECT PERFORMANCEID, POSITIONID, SALESVOLUME, SALESREVENUE, STOCKLEVEL, RESTOCKFREQUENCY, DATE
            FROM PERFORMANCE
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
            SELECT PERFORMANCEID, POSITIONID, SALESVOLUME, SALESREVENUE, STOCKLEVEL, RESTOCKFREQUENCY, DATE
            FROM PERFORMANCE
            WHERE PERFORMANCEID = %s
        """, (performance_id,))
        return cursor.fetchone()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Insert a new performance record
def insert_performance(user, password, position_id, sales_volume, sales_revenue, stock_level, restock_frequency, date):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO PERFORMANCE (POSITIONID, SALESVOLUME, SALESREVENUE, STOCKLEVEL, RESTOCKFREQUENCY, DATE)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (position_id, sales_volume, sales_revenue, stock_level, restock_frequency, date))
        conn.commit()
        print(f"Inserted performance record")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Update an existing performance record
def update_performance(user, password, performance_id, position_id, sales_volume, sales_revenue, stock_level, restock_frequency, date):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE PERFORMANCE
            SET POSITIONID = %s, SALESVOLUME = %s, SALESREVENUE = %s, STOCKLEVEL = %s, RESTOCKFREQUENCY = %s, DATE = %s
            WHERE PERFORMANCEID = %s
        """, (position_id, sales_volume, sales_revenue, stock_level, restock_frequency, date, performance_id))
        conn.commit()
        print(f"Updated performance record ID: {performance_id}")
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
        cursor.execute("DELETE FROM PERFORMANCE WHERE PERFORMANCEID = %s", (performance_id,))
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
                "performanceId": performance[0],
                "positionId": performance[1],
                "salesVolume": performance[2],
                "salesRevenue": performance[3],
                "stockLevel": performance[4],
                "restockFrequency": performance[5],
                "date": performance[6].strftime('%Y-%m-%d') if performance[6] else None
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
    position_id = data.get('positionId')
    sales_volume = data.get('salesVolume')
    sales_revenue = data.get('salesRevenue')
    stock_level = data.get('stockLevel')
    restock_frequency = data.get('restockFrequency')
    date = data.get('date')  # Expected to be in 'YYYY-MM-DD' format
    
    if not (position_id and sales_volume and sales_revenue and stock_level and restock_frequency and date):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        insert_performance(user, password, position_id, sales_volume, sales_revenue, stock_level, restock_frequency, date)
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
    performance_id = data.get('performanceId')
    position_id = data.get('positionId')
    sales_volume = data.get('salesVolume')
    sales_revenue = data.get('salesRevenue')
    stock_level = data.get('stockLevel')
    restock_frequency = data.get('restockFrequency')
    date = data.get('date')  # Expected to be in 'YYYY-MM-DD' format

    if not (performance_id and position_id and sales_volume and sales_revenue and stock_level and restock_frequency and date):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        update_performance(user, password, performance_id, position_id, sales_volume, sales_revenue, stock_level, restock_frequency, date)
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
    performance_id = data.get('performanceId')

    if not performance_id:
        return jsonify({"success": False, "message": "Performance ID is required"}), 400

    try:
        delete_performance(user, password, performance_id)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200
