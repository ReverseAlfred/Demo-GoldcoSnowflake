from flask import Blueprint, request, redirect, url_for, make_response, render_template
import snowflake.connector
from config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return "Username and password are required.", 400

        try:
            # Connect to Snowflake to validate credentials
            conn = snowflake.connector.connect(
                user=username,
                password=password,
                account=Config.SNOWFLAKE_ACCOUNT,
                warehouse=Config.SNOWFLAKE_WAREHOUSE,
                database=Config.SNOWFLAKE_DATABASE,
                schema=Config.SNOWFLAKE_SCHEMA
            )
            conn.close()

            # Set cookies with login data
            resp = make_response(redirect(url_for('dashboard.dashboard')))
            resp.set_cookie('snowflake_username', username)
            resp.set_cookie('snowflake_password', password)

            return resp

        except snowflake.connector.errors.DatabaseError:
            return "Login failed. Please check your credentials and try again.", 400

    return render_template('login.html')
