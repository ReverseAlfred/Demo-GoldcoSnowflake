import io
import snowflake.connector
from flask import Blueprint, render_template, request, jsonify, send_file
from config import Config

planogram_bp = Blueprint('planogram', __name__)

def get_snowflake_connection(user, password):
    """
    Create a Snowflake connection using provided credentials and config settings.
    """
    return snowflake.connector.connect(
        user=user,
        password=password,
        account=Config.SNOWFLAKE_ACCOUNT,
        warehouse=Config.SNOWFLAKE_WAREHOUSE,
        database=Config.SNOWFLAKE_DATABASE,
        schema=Config.SNOWFLAKE_SCHEMA
    )

def execute_query(user, password, query, params=None, fetchone=False, commit=False):
    """
    Execute a query with optional commit and fetch operations.
    """
    conn = None
    try:
        conn = get_snowflake_connection(user, password)
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if commit:
                conn.commit()
            return cursor.fetchone() if fetchone else cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

@planogram_bp.route('/dsplanogram')
def dsplanogram():
    """
    Display all planogram records.
    """
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return "Error: Missing credentials", 401
    
    try:
        query = """
            SELECT p.DBKEY, p.PLANOGRAMNAME, p.DBSTATUS, pp.DBKEY AS pdfId
            FROM NEWCKB.PUBLIC.IX_SPC_PLANOGRAM p
            LEFT JOIN NEWCKB.PUBLIC.IX_SPC_PLANOGRAM_PDF pp 
            ON p.DBKEY = pp.DBPlanogramParentKey
        """
        planograms = execute_query(user, password, query)
    except Exception as e:
        return f"Error: {str(e)}", 500

    return render_template('dsplanogram.html', planograms=planograms)

@planogram_bp.route('/get_planogram', methods=['GET'])
def get_planogram():
    """
    Get a specific planogram record by ID.
    """
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    planogram_id = request.args.get('planogramId')
    if not planogram_id:
        return jsonify({"success": False, "message": "Planogram ID is required"}), 400

    query = """
        SELECT DBKEY, PLANOGRAMNAME, DBSTATUS
        FROM NEWCKB.PUBLIC.IX_SPC_PLANOGRAM
        WHERE DBKEY = %s
    """
    
    try:
        planogram = execute_query(user, password, query, (planogram_id,), fetchone=True)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    if planogram:
        return jsonify({
            "success": True,
            "planogram": {
                "dbKey": planogram[0],
                "planogramName": planogram[1],
                "dbStatus": planogram[2]
            }
        })
    else:
        return jsonify({"success": False, "message": "Planogram record not found"}), 404

@planogram_bp.route('/dsplanogram/add', methods=['POST'])
def add_planogram():
    """
    Add a new planogram record with an associated PDF file.
    """
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    planogramname = request.form.get('planogramName')
    dbstatus = request.form.get('dbStatus', 1)
    pdf_file = request.files.get('pdfFile')

    if not (planogramname and pdf_file):
        return jsonify({"success": False, "message": "Planogram name and PDF file are required"}), 400

    pdf_binary = pdf_file.read()

    try:
        # Insert the planogram and get the ID
        insert_query = """
            INSERT INTO NEWCKB.PUBLIC.IX_SPC_PLANOGRAM (PLANOGRAMNAME, DBSTATUS)
            VALUES (%s, %s)
        """
        planogram_id = execute_query(user, password, insert_query, (planogramname, dbstatus), commit=True)
        
        # Fetch the last inserted planogram ID
        planogram_id = execute_query(user, password, "SELECT MAX(DBKEY) FROM NEWCKB.PUBLIC.IX_SPC_PLANOGRAM", fetchone=True)[0]

        # Insert the PDF
        pdf_query = """
            INSERT INTO NEWCKB.PUBLIC.IX_SPC_PLANOGRAM_PDF (DBPlanogramParentKey, PDF)
            VALUES (%s, %s)
        """
        execute_query(user, password, pdf_query, (planogram_id, pdf_binary), commit=True)

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200

@planogram_bp.route('/dsplanogram/update_planogram', methods=['POST'])
def update_planogram_route():
    """
    Update an existing planogram record.
    """
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    dbkey = data.get('dbKey')
    planogramname = data.get('planogramName')
    dbstatus = data.get('dbStatus')

    if not (dbkey and planogramname and dbstatus is not None):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    update_query = """
        UPDATE NEWCKB.PUBLIC.IX_SPC_PLANOGRAM
        SET PLANOGRAMNAME = %s, DBSTATUS = %s
        WHERE DBKEY = %s
    """
    
    try:
        execute_query(user, password, update_query, (planogramname, dbstatus, dbkey), commit=True)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200

@planogram_bp.route('/dsplanogram/delete_planogram', methods=['POST'])
def delete_planogram_route():
    """
    Delete a planogram record.
    """
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    planogram_id = data.get('planogramId')
    if not planogram_id:
        return jsonify({"success": False, "message": "Planogram ID is required"}), 400

    delete_query = """
        DELETE FROM NEWCKB.PUBLIC.IX_SPC_PLANOGRAM
        WHERE DBKEY = %s
    """
    
    try:
        execute_query(user, password, delete_query, (planogram_id,), commit=True)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True}), 200

@planogram_bp.route('/dsplanogram/view_pdf/<int:dbkey>', methods=['GET'])
def view_pdf_dsplanogram(dbkey):
    """
    View a PDF file associated with a planogram.
    """
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    query = """
        SELECT PDF
        FROM NEWCKB.PUBLIC.IX_SPC_PLANOGRAM_PDF
        WHERE DBKEY = %s
    """
    
    try:
        pdf_data = execute_query(user, password, query, (dbkey,), fetchone=True)
        if pdf_data and pdf_data[0]:
            pdf_binary = pdf_data[0]
            return send_file(io.BytesIO(pdf_binary), download_name='planogram.pdf', as_attachment=False)
        else:
            return jsonify({"success": False, "message": "PDF not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@planogram_bp.route('/flplanogram/view_pdf/<int:dbkey>', methods=['GET'])
def view_pdf_flplanogram(dbkey):
    """
    View a PDF file associated with a floorplan.
    """
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    query = """
        SELECT PDF
        FROM NEWCKB.PUBLIC.IX_SPC_PLANOGRAM_PDF
        WHERE DBKEY = %s
    """
    
    try:
        pdf_data = execute_query(user, password, query, (dbkey,), fetchone=True)
        if pdf_data and pdf_data[0]:
            pdf_binary = pdf_data[0]
            return send_file(io.BytesIO(pdf_binary), download_name='planogram.pdf', as_attachment=False)
        else:
            return jsonify({"success": False, "message": "PDF not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@planogram_bp.route('/flplanogram', methods=['GET'])
def flplanogram():
    """
    Display the floorplan and associated planograms.
    """
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')

    if not user or not password:
        return "Error: Missing credentials", 401

    floorplan_id = request.args.get('floorplanId')
    if not floorplan_id:
        return "Error: Floorplan ID is required", 400
    
    try:
        query_planograms = """
            SELECT P.DBKEY, P.PLANOGRAMNAME, P.DBSTATUS, pp.DBKEY AS pdfId
            FROM NEWCKB.PUBLIC.IX_SPC_PLANOGRAM P
            LEFT JOIN NEWCKB.PUBLIC.IX_SPC_PLANOGRAM_PDF pp
            ON P.DBKEY = pp.DBPlanogramParentKey
            JOIN NEWCKB.PUBLIC.IX_FLR_PERFORMANCE FP
            ON P.DBKEY = FP.DBPLANOGRAMPARENTKEY
            WHERE FP.DBFLOORPLANPARENTKEY = %s
        """
        planograms = execute_query(user, password, query_planograms, (floorplan_id,))

        query_all_planograms = """
            SELECT DBKEY, PLANOGRAMNAME, DBSTATUS
            FROM NEWCKB.PUBLIC.IX_SPC_PLANOGRAM
        """
        all_planograms = execute_query(user, password, query_all_planograms)
        
        return render_template('flplanogram.html', planograms=planograms, all_planograms=all_planograms, floorplan_id=floorplan_id)

    except Exception as e:
        return f"Error: {str(e)}", 500

@planogram_bp.route('/flplanogram/add_planogram', methods=['POST'])
def add_planogram_to_floorplan():
    """
    Add a planogram to a floorplan.
    """
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')

    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    floorplan_id = data.get('floorplanId')
    planogram_id = data.get('planogramId')

    if not (floorplan_id and planogram_id):
        return jsonify({"success": False, "message": "Floorplan ID and Planogram ID are required"}), 400

    query = """
        INSERT INTO NEWCKB.PUBLIC.IX_FLR_PERFORMANCE (DBFLOORPLANPARENTKEY, DBPLANOGRAMPARENTKEY)
        VALUES (%s, %s)
    """
    
    try:
        execute_query(user, password, query, (floorplan_id, planogram_id), commit=True)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@planogram_bp.route('/flplanogram/remove_planogram', methods=['POST'])
def remove_planogram_from_floorplan():
    """
    Remove a planogram from a floorplan.
    """
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')

    if not user or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 401

    data = request.get_json()
    floorplan_id = data.get('floorplanId')
    planogram_id = data.get('planogramId')

    if not (floorplan_id and planogram_id):
        return jsonify({"success": False, "message": "Floorplan ID and Planogram ID are required"}), 400

    query = """
        DELETE FROM NEWCKB.PUBLIC.IX_FLR_PERFORMANCE
        WHERE DBFLOORPLANPARENTKEY = %s AND DBPLANOGRAMPARENTKEY = %s
    """
    
    try:
        execute_query(user, password, query, (floorplan_id, planogram_id), commit=True)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
