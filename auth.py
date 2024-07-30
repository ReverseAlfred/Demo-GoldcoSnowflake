from flask import Blueprint, request, redirect, url_for, make_response, render_template
import snowflake.connector

# Create a Blueprint for authentication
auth_bp = Blueprint('auth', __name__)

# Function to verify Snowflake connection
def verify_snowflake_connection(username, password):
    try:
        conn = snowflake.connector.connect(
            user=username,
            password=password,
            account='XIQTUJZ-DA41181',
            warehouse='ckb_wh',
            database='ckb',
            schema='public'
        )
        conn.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verify Snowflake connection
        if verify_snowflake_connection(username, password):
            # Set cookies
            resp = make_response(redirect(url_for('dashboard.dsstore')))
            resp.set_cookie('username', username)
            resp.set_cookie('password', password)
            return resp
        else:
            # Return error message
            return render_template('login.html', error_message='Login failed. Please check your credentials.')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    resp = make_response(redirect(url_for('auth.login')))
    resp.delete_cookie('username')
    resp.delete_cookie('password')
    return resp
