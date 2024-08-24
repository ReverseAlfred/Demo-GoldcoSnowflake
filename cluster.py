import snowflake.connector
from flask import Blueprint, render_template, request, jsonify
from config import Config

cluster_bp = Blueprint('cluster', __name__)

# Helper function to establish a Snowflake connection
def get_snowflake_connection(user, password):
    return snowflake.connector.connect(
        user=user,
        password=password,
        account=Config.SNOWFLAKE_ACCOUNT,
        warehouse=Config.SNOWFLAKE_WAREHOUSE,
        database=Config.SNOWFLAKE_DATABASE,
        schema=Config.SNOWFLAKE_SCHEMA
    )

# Helper function to execute a query and fetch results
def execute_query(user, password, query, params=None, fetchone=False):
    with get_snowflake_connection(user, password) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone() if fetchone else cursor.fetchall()

# Fetch all clusters
def fetch_clusters(user, password):
    query = "SELECT DBKEY, CLUSTERNAME FROM NEWCKB.PUBLIC.IX_EIA_CLUSTER"
    return execute_query(user, password, query)

# Fetch a cluster by its ID
def fetch_cluster_by_id(user, password, cluster_id):
    query = "SELECT DBKEY, CLUSTERNAME FROM NEWCKB.PUBLIC.IX_EIA_CLUSTER WHERE DBKEY = %s"
    return execute_query(user, password, query, (cluster_id,), fetchone=True)

# Insert a new cluster
def insert_cluster(user, password, cluster_name):
    query = "INSERT INTO NEWCKB.PUBLIC.IX_EIA_CLUSTER (CLUSTERNAME) VALUES (%s)"
    execute_query(user, password, query, (cluster_name,))
    # Commit is handled by the context manager

# Update an existing cluster
def update_cluster(user, password, cluster_id, cluster_name):
    query = "UPDATE NEWCKB.PUBLIC.IX_EIA_CLUSTER SET CLUSTERNAME = %s WHERE DBKEY = %s"
    execute_query(user, password, query, (cluster_name, cluster_id))
    # Commit is handled by the context manager

# Delete a cluster
def delete_cluster(user, password, cluster_id):
    query = "DELETE FROM NEWCKB.PUBLIC.IX_EIA_CLUSTER WHERE DBKEY = %s"
    execute_query(user, password, query, (cluster_id,))
    # Commit is handled by the context manager

# Route to display all clusters
@cluster_bp.route('/dscluster')
def dscluster():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return "Error: Missing credentials", 401
    
    try:
        clusters = fetch_clusters(user, password)
        return render_template('dscluster.html', clusters=clusters)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

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
        if cluster:
            return jsonify({
                "success": True,
                "cluster": {
                    "dbkey": cluster[0],
                    "clusterName": cluster[1]
                }
            })
        else:
            return jsonify({"success": False, "message": "Cluster not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

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
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

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
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

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
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
