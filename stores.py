from flask import Blueprint, render_template, request
import snowflake.connector
from config import Config

# Create a Blueprint for the stores
stores_bp = Blueprint('stores', __name__)

# Function to get Snowflake connection
def get_snowflake_connection():
    conn = snowflake.connector.connect(
        user=request.cookies.get(Config.COOKIE_USERNAME_KEY),
        password=request.cookies.get(Config.COOKIE_PASSWORD_KEY),
        account=Config.SNOWFLAKE_ACCOUNT,
        warehouse=Config.SNOWFLAKE_WAREHOUSE,
        database=Config.SNOWFLAKE_DATABASE,
        schema=Config.SNOWFLAKE_SCHEMA
    )
    return conn

def get_stores(filter_value=None):
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        # Query to retrieve store names with optional filtering
        query = "SELECT storename FROM stores"
        if filter_value:
            query += " WHERE LOWER(storename) LIKE %s"
            filter_value = f"%{filter_value.lower()}%"
        
        cursor.execute(query, (filter_value,) if filter_value else None)
        stores = [row[0] for row in cursor.fetchall()]
        
        return stores

    except Exception as e:
        print(f"Error: {e}")
        return []

    finally:
        conn.close()

@stores_bp.route('/dsstores', methods=['GET', 'POST'])
def show_stores():
    filter_value = request.args.get('filter', '')
    try:
        stores = get_stores(filter_value)
        return render_template('dsstores.html', stores=stores, filter=filter_value)
    except Exception as e:
        print(f"Error: {e}")
        return render_template('dsstores.html', error_message='Error retrieving data from Snowflake.')
