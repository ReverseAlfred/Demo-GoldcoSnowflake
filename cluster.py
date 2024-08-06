import os
from flask import Blueprint, render_template, request, jsonify
import snowflake.connector
from config import Config

cluster_bp = Blueprint('cluster', __name__)

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

# Fetch all clusters
def fetch_clusters(user, password):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("SELECT CLUSTERID, CLUSTERNAME FROM cluster")
        return cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Fetch cluster by ID
def fetch_cluster_by_id(user, password, cluster_id):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("SELECT CLUSTERID, CLUSTERNAME FROM cluster WHERE CLUSTERID = %s", (cluster_id,))
        return cursor.fetchone()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Insert a new cluster
def insert_cluster(user, password, cluster_name):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cluster (CLUSTERNAME) 
            VALUES (%s)
        """, (cluster_name,))
        conn.commit()
        print(f"Inserted cluster")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Update an existing cluster
def update_cluster(user, password, cluster_id, cluster_name):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE cluster
            SET CLUSTERNAME = %s
            WHERE CLUSTERID = %s
        """, (cluster_name, cluster_id))
        conn.commit()
        print(f"Updated cluster ID: {cluster_id}")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Delete a cluster
def delete_cluster(user, password, cluster_id):
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cluster WHERE CLUSTERID = %s", (cluster_id,))
        conn.commit()
        print(f"Deleted cluster ID: {cluster_id}")
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

# Route to display all clusters
@cluster_bp.route('/dscluster')
def dscluster():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return "Error: Missing credentials", 401
    
    try:
        clusters = fetch_clusters(user, password)
    except Exception as e:
        return f"Error: {str(e)}", 500

    return render_template('dscluster.html', clusters=clusters)

# Route to get a cluster by ID
@cluster_bp.route('/get_cluster', methods=['GET'])
def get_cluster():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    cluster_id = request.args.get('clusterId')
    if not cluster_id:
        return jsonify({"success": False, "message": "Cluster ID is required"}), 400

    try:
        cluster = fetch_cluster_by_id(user, password, cluster_id)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    if cluster:
        return jsonify({
            "success": True,
            "cluster": {
                "clusterId": cluster[0],
                "clusterName": cluster[1]
            }
        })
    else:
        return jsonify({"success": False, "message": "Cluster not found"}), 404

# Route to add a new cluster
@cluster_bp.route('/dscluster/add', methods=['POST'])
def add_cluster():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    cluster_name = data.get('clusterName')
    
    if not cluster_name:
        return jsonify({"success": False, "message": "Cluster name is required"}), 400

    try:
        insert_cluster(user, password, cluster_name)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200

# Route to update an existing cluster
@cluster_bp.route('/dscluster/update_cluster', methods=['POST'])
def update_cluster_route():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    cluster_id = data.get('clusterId')
    cluster_name = data.get('clusterName')

    if not (cluster_id and cluster_name):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        update_cluster(user, password, cluster_id, cluster_name)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200

# Route to delete a cluster
@cluster_bp.route('/dscluster/delete_cluster', methods=['POST'])
def delete_cluster_route():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    cluster_id = data.get('clusterId')

    if not cluster_id:
        return jsonify({"success": False, "message": "Cluster ID is required"}), 400

    try:
        delete_cluster(user, password, cluster_id)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200
