import os
from flask import Blueprint, render_template, request
import snowflake.connector
from config import Config

store_bp = Blueprint('store', __name__)

def get_snowflake_connection(user, password):
    # Establish a connection to Snowflake using provided credentials and config
    conn = snowflake.connector.connect(
        user=user,
        password=password,
        account=Config.SNOWFLAKE_ACCOUNT,
        warehouse=Config.SNOWFLAKE_WAREHOUSE,
        database=Config.SNOWFLAKE_DATABASE,
        schema=Config.SNOWFLAKE_SCHEMA
    )
    return conn

@store_bp.route('/dsstore')
def dsstore():
    user = request.cookies.get('snowflake_username')
    password = request.cookies.get('snowflake_password')
    
    if not user or not password:
        return "Error: Missing credentials", 401

    try:
        conn = get_snowflake_connection(user, password)
        cursor = conn.cursor()
        cursor.execute("SELECT STOREID, STORENAME FROM CKB.PUBLIC.STORES")
        stores = cursor.fetchall()
    except Exception as e:
        return f"Error: {str(e)}", 500
    finally:
        conn.close()

    return render_template('dsstore.html', stores=stores)
