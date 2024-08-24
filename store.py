import snowflake.connector
from flask import Blueprint, render_template, request, jsonify
from config import Config

store_bp = Blueprint('store', __name__)

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

# Fetch all stores
def fetch_stores(user, password):
    query = "SELECT DBKEY, STORENAME, DESCRIPTIVO1, DBSTATUS FROM NEWCKB.PUBLIC.IX_STR_STORE"
    return execute_query(user, password, query)

# Fetch a store by ID
def fetch_store_by_id(user, password, store_id):
    query = "SELECT DBKEY, STORENAME, DESCRIPTIVO1, DBSTATUS FROM NEWCKB.PUBLIC.IX_STR_STORE WHERE DBKEY = %s"
    return execute_query(user, password, query, (store_id,), fetchone=True)

# Fetch the maximum store ID
def fetch_max_store_id(user, password):
    query = "SELECT MAX(DBKEY) FROM NEWCKB.PUBLIC.IX_STR_STORE"
    result = execute_query(user, password, query, fetchone=True)
    return result[0] if result and result[0] is not None else 0

# Insert a new store
def insert_store(user, password, store_name, descriptivo1, dbstatus):
    query = """
        INSERT INTO NEWCKB.PUBLIC.IX_STR_STORE (STORENAME, DESCRIPTIVO1, DBSTATUS)
        VALUES (%s, %s, %s)
    """
    execute_query(user, password, query, (store_name, descriptivo1, dbstatus))
    # Commit is handled by the context manager

# Update an existing store
def update_store(user, password, store_id, store_name, descriptivo1, dbstatus):
    query = """
        UPDATE NEWCKB.PUBLIC.IX_STR_STORE
        SET STORENAME = %s, DESCRIPTIVO1 = %s, DBSTATUS = %s
        WHERE DBKEY = %s
    """
    execute_query(user, password, query, (store_name, descriptivo1, dbstatus, store_id))
    # Commit is handled by the context manager

# Delete a store
def delete_store(user, password, store_id):
    query = "DELETE FROM NEWCKB.PUBLIC.IX_STR_STORE WHERE DBKEY = %s"
    execute_query(user, password, query, (store_id,))
    # Commit is handled by the context manager

# Route to display all stores
@store_bp.route('/dsstore')
def dsstore():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')

    if not user or not password:
        return "Error: Missing credentials", 401

    try:
        stores = fetch_stores(user, password)
        return render_template('dsstore.html', stores=stores)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Route to get a store by ID
@store_bp.route('/get_store', methods=['GET'])
def get_store():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')

    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    store_id = request.args.get('storeId')
    if not store_id:
        return jsonify({"success": False, "message": "Store ID is required"}), 400

    try:
        store = fetch_store_by_id(user, password, store_id)
        if store:
            return jsonify({
                "success": True,
                "store": {
                    "storeId": store[0],
                    "storeName": store[1],
                    "descriptivo1": store[2],
                    "dbStatus": store[3]
                }
            })
        else:
            return jsonify({"success": False, "message": "Store not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Route to add a new store
@store_bp.route('/dsstore/add', methods=['POST'])
def add_store():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')

    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    store_name = data.get('storeName')
    descriptivo1 = data.get('descriptivo1')
    dbstatus = data.get('dbStatus')

    if not (store_name and descriptivo1 and dbstatus is not None):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        insert_store(user, password, store_name, descriptivo1, dbstatus)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Route to update an existing store
@store_bp.route('/dsstore/update_store', methods=['POST'])
def update_store_route():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')

    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    store_id = data.get('storeId')
    store_name = data.get('storeName')
    descriptivo1 = data.get('descriptivo1')
    dbstatus = data.get('dbStatus')

    if not (store_id and store_name and descriptivo1 and dbstatus is not None):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        update_store(user, password, store_id, store_name, descriptivo1, dbstatus)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Route to delete a store
@store_bp.route('/dsstore/delete_store', methods=['POST'])
def delete_store_route():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')

    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    store_id = data.get('storeId')

    if not store_id:
        return jsonify({"success": False, "message": "Store ID is required"}), 400

    try:
        delete_store(user, password, store_id)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Route to display stores in a cluster
@store_bp.route('/clstore')
def clstore():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')

    if not user or not password:
        return "Error: Missing credentials", 401

    cluster_id = request.args.get('clusterId')
    if not cluster_id:
        return "Error: Cluster ID is required", 400

    try:
        # Fetch stores in the cluster and all stores
        query_stores_in_cluster = """
            SELECT S.DBKEY, S.STORENAME, S.DESCRIPTIVO1, S.DBSTATUS
            FROM NEWCKB.PUBLIC.IX_STR_STORE S
            JOIN NEWCKB.PUBLIC.IX_EIA_CLUSTER_STORE CS
            ON S.DBKEY = CS.DBSTOREPARENTKEY
            WHERE CS.DBCLUSTERPARENTKEY = %s
        """
        query_all_stores = "SELECT DBKEY, STORENAME, DESCRIPTIVO1, DBSTATUS FROM NEWCKB.PUBLIC.IX_STR_STORE"

        with get_snowflake_connection(user, password) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query_stores_in_cluster, (cluster_id,))
                stores = cursor.fetchall()
                cursor.execute(query_all_stores)
                all_stores = cursor.fetchall()

        return render_template('clstore.html', stores=stores, all_stores=all_stores, cluster_id=cluster_id)
    except Exception as e:
        return f"Error: {str(e)}", 500

# Route to add a store to a cluster
@store_bp.route('/clstore/add_store', methods=['POST'])
def add_store_to_cluster():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')

    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    cluster_id = data.get('clusterId')
    store_id = data.get('storeId')

    if not (cluster_id and store_id):
        return jsonify({"success": False, "message": "Cluster ID and Store ID are required"}), 400

    try:
        insert_store_to_cluster(user, password, cluster_id, store_id)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Route to remove a store from a cluster
@store_bp.route('/clstore/delete_store', methods=['POST'])
def delete_store_from_cluster_route():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')

    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    store_id = data.get('storeId')
    cluster_id = data.get('clusterId')

    if not (store_id and cluster_id):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        delete_store_from_cluster(user, password, cluster_id, store_id)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Helper function to insert a store into a cluster
def insert_store_to_cluster(user, password, cluster_id, store_id):
    query_check_exists = """
        SELECT COUNT(*)
        FROM NEWCKB.PUBLIC.IX_EIA_CLUSTER_STORE
        WHERE DBCLUSTERPARENTKEY = %s AND DBSTOREPARENTKEY = %s
    """
    query_insert = """
        INSERT INTO NEWCKB.PUBLIC.IX_EIA_CLUSTER_STORE (DBCLUSTERPARENTKEY, DBSTOREPARENTKEY)
        VALUES (%s, %s)
    """

    with get_snowflake_connection(user, password) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query_check_exists, (cluster_id, store_id))
            if cursor.fetchone()[0] > 0:
                raise ValueError("The relationship already exists")

            cursor.execute(query_insert, (cluster_id, store_id))
            conn.commit()

# Helper function to delete a store from a cluster
def delete_store_from_cluster(user, password, cluster_id, store_id):
    query = """
        DELETE FROM NEWCKB.PUBLIC.IX_EIA_CLUSTER_STORE
        WHERE DBCLUSTERPARENTKEY = %s AND DBSTOREPARENTKEY = %s
    """
    with get_snowflake_connection(user, password) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (cluster_id, store_id))
            conn.commit()
