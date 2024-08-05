from flask import Blueprint, render_template

# Create a Blueprint for dashboard-related routes
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    """
    Render the dashboard template.
    """
    return render_template('dashboard.html')
