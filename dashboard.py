from flask import Blueprint, render_template, request, redirect, url_for
import snowflake.connector

# Create a Blueprint for the dashboard
dashboard_bp = Blueprint('dashboard', __name__)

# Function to get Snowflake connection
def get_snowflake_connection():
    conn = snowflake.connector.connect(
        user=request.cookies.get('username'),
        password=request.cookies.get('password'),
        account='XIQTUJZ-DA41181',
        warehouse='ckb_wh',
        database='ckb',
        schema='public'
    )
    return conn

@dashboard_bp.route('/')
def dashboard():
    # Check if user is logged in
    if not request.cookies.get('username') or not request.cookies.get('password'):
        return redirect(url_for('auth.login'))

    return render_template('dashboard.html')

@dashboard_bp.route('/dsstore')
def dsstore():
    # Check if user is logged in
    if not request.cookies.get('username') or not request.cookies.get('password'):
        return redirect(url_for('auth.login'))

    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()

        # Query to retrieve store names
        cursor.execute("SELECT storename FROM stores")
        stores = [row[0] for row in cursor.fetchall()]

        return render_template('dsstores.html', stores=stores)

    except Exception as e:
        print(f"Error: {e}")
        return "Error retrieving data from Snowflake."

    finally:
        conn.close()

@dashboard_bp.route('/dsplanogram')
def dsplanogram():
    return render_template('dsplanogram.html')

@dashboard_bp.route('/dsfloorplan')
def dsfloorplan():
    return render_template('dsfloorplan.html')

@dashboard_bp.route('/dsproduct')
def dsproduct():
    return render_template('dsproduct.html')

@dashboard_bp.route('/dsother')
def dsother():
    return render_template('dsother.html')
