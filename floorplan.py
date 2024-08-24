import snowflake.connector
from flask import Blueprint, render_template, request, jsonify
from config import Config

floorplan_bp = Blueprint('floorplan', __name__)

# Helper function to establish a Snowflake connection
def get_snowflake_connection(user, password):
    """Establish a connection to Snowflake using provided credentials."""
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
    """Execute a query on Snowflake and return the results."""
    with get_snowflake_connection(user, password) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone() if fetchone else cursor.fetchall()

# Fetch all floor plans
def fetch_floor_plans(user, password):
    """Retrieve all floor plans from the database."""
    query = """
        SELECT DBKEY, FLOORPLANNAME, DBSTATUS 
        FROM IX_FLR_FLOORPLAN
    """
    return execute_query(user, password, query)

# Fetch a floor plan by ID
def fetch_floor_plan_by_id(user, password, floor_plan_id):
    """Retrieve a specific floor plan by its ID."""
    query = """
        SELECT DBKEY, FLOORPLANNAME, DBSTATUS 
        FROM IX_FLR_FLOORPLAN 
        WHERE DBKEY = %s
    """
    return execute_query(user, password, query, (floor_plan_id,), fetchone=True)

# Insert a new floor plan
def insert_floor_plan(user, password, name, status):
    """Insert a new floor plan into the database."""
    query = """
        INSERT INTO IX_FLR_FLOORPLAN (FLOORPLANNAME, DBSTATUS) 
        VALUES (%s, %s)
    """
    execute_query(user, password, query, (name, status))
    # Commit is handled by the context manager

# Update an existing floor plan
def update_floor_plan(user, password, floor_plan_id, name, status):
    """Update an existing floor plan in the database."""
    query = """
        UPDATE IX_FLR_FLOORPLAN
        SET FLOORPLANNAME = %s, DBSTATUS = %s
        WHERE DBKEY = %s
    """
    execute_query(user, password, query, (name, status, floor_plan_id))
    # Commit is handled by the context manager

# Delete a floor plan
def delete_floor_plan(user, password, floor_plan_id):
    """Delete a floor plan from the database."""
    query = """
        DELETE FROM IX_FLR_FLOORPLAN WHERE DBKEY = %s
    """
    execute_query(user, password, query, (floor_plan_id,))
    # Commit is handled by the context manager

# Route to display all floor plans
@floorplan_bp.route('/dsfloorplan')
def dsfloorplan():
    """Display all floor plans."""
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')

    if not user or not password:
        return "Error: Missing credentials", 401

    try:
        floor_plans = fetch_floor_plans(user, password)
        return render_template('dsfloorplan.html', floor_plans=floor_plans)
    except Exception as e:
        return f"Error: {str(e)}", 500

# Route to get a floor plan by ID
@floorplan_bp.route('/get_floor_plan', methods=['GET'])
def get_floor_plan():
    """Get a specific floor plan by its ID."""
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')

    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    floor_plan_id = request.args.get('floorPlanId')
    if not floor_plan_id:
        return jsonify({"success": False, "message": "Floor Plan ID is required"}), 400

    try:
        floor_plan = fetch_floor_plan_by_id(user, password, floor_plan_id)
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
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Route to add a new floor plan
@floorplan_bp.route('/dsfloorplan/add', methods=['POST'])
def add_floor_plan():
    """Add a new floor plan."""
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
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Route to update an existing floor plan
@floorplan_bp.route('/dsfloorplan/update_floor_plan', methods=['POST'])
def update_floor_plan_route():
    """Update an existing floor plan."""
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
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Route to delete a floor plan
@floorplan_bp.route('/dsfloorplan/delete_floor_plan', methods=['POST'])
def delete_floor_plan_route():
    """Delete a floor plan."""
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
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Route to display floor plans for a store
@floorplan_bp.route('/stfloorplan')
def stfloorplan():
    """Display floor plans associated with a specific store."""
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')

    if not user or not password:
        return "Error: Missing credentials", 401

    store_id = request.args.get('storeId')
    if not store_id:
        return "Error: Store ID is required", 400

    try:
        # Fetch floor plans associated with the store
        query_store_floor_plans = """
            SELECT F.DBKEY, F.FLOORPLANNAME, F.DBSTATUS
            FROM IX_FLR_FLOORPLAN F
            JOIN IX_STR_STORE_FLOORPLAN SF
            ON F.DBKEY = SF.DBFLOORPLANPARENTKEY
            WHERE SF.DBSTOREPARENTKEY = %s
        """
        # Fetch all floor plans
        query_all_floor_plans = "SELECT DBKEY, FLOORPLANNAME, DBSTATUS FROM IX_FLR_FLOORPLAN"

        with get_snowflake_connection(user, password) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query_store_floor_plans, (store_id,))
                floorplans = cursor.fetchall()
                cursor.execute(query_all_floor_plans)
                all_floorplans = cursor.fetchall()

        return render_template('stfloorplan.html', floorplans=floorplans, all_floorplans=all_floorplans, store_id=store_id)
    except Exception as e:
        return f"Error: {str(e)}", 500

# Route to add a floor plan to a store
@floorplan_bp.route('/stfloorplan/add_floorplan', methods=['POST'])
def add_floorplan_to_store():
    """Associate a floor plan with a store."""
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')

    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    store_id = data.get('storeId')
    floorplan_id = data.get('floorplanId')

    if not (store_id and floorplan_id):
        return jsonify({"success": False, "message": "Store ID and Floorplan ID are required"}), 400

    query_check_exists = """
        SELECT COUNT(*) 
        FROM IX_STR_STORE_FLOORPLAN 
        WHERE DBStoreParentKey = %s AND DBFloorplanParentKey = %s
    """
    query_insert = """
        INSERT INTO IX_STR_STORE_FLOORPLAN (DBStoreParentKey, DBFloorplanParentKey) 
        VALUES (%s, %s)
    """

    try:
        with get_snowflake_connection(user, password) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query_check_exists, (store_id, floorplan_id))
                if cursor.fetchone()[0] > 0:
                    return jsonify({'message': 'Floorplan already associated with this store.'}), 400

                cursor.execute(query_insert, (store_id, floorplan_id))
        return jsonify({'message': 'Floorplan added successfully.'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Route to remove a floor plan from a store
@floorplan_bp.route('/stfloorplan/delete_floorplan', methods=['POST'])
def remove_floorplan_from_store():
    """Remove a floor plan from a store."""
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')

    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    store_id = data.get('storeId')
    floorplan_id = data.get('floorplanId')

    if not (store_id and floorplan_id):
        return jsonify({"success": False, "message": "Store ID and Floorplan ID are required"}), 400

    query_delete = """
        DELETE FROM IX_STR_STORE_FLOORPLAN 
        WHERE DBStoreParentKey = %s AND DBFloorplanParentKey = %s
    """

    try:
        with get_snowflake_connection(user, password) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query_delete, (store_id, floorplan_id))
                if cursor.rowcount == 0:
                    return jsonify({"success": False, "message": "No matching record found to delete."}), 404
        return jsonify({"success": True, "message": "Floorplan removed successfully."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to remove floorplan from store."}), 500
