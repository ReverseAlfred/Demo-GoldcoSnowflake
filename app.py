from flask import Flask, render_template
from auth import auth_bp
from dashboard import dashboard_bp
from store import store_bp
from product import product_bp
from planogram import planogram_bp
from cluster import cluster_bp
from floorplan import floorplan_bp
from position import position_bp
from performance import performance_bp

# Create Flask application instance
app = Flask(__name__)

# Register blueprints
app.register_blueprint(auth_bp)       # Handles authentication-related routes
app.register_blueprint(dashboard_bp)  # Handles dashboard-related routes
app.register_blueprint(store_bp)      # Handles store-related routes
app.register_blueprint(product_bp)    # Handles product-related routes
app.register_blueprint(planogram_bp)    # Handles product-related routes
app.register_blueprint(cluster_bp)    # Handles product-related routes
app.register_blueprint(floorplan_bp)    # Handles product-related routes
app.register_blueprint(position_bp)    # Handles product-related routes
app.register_blueprint(performance_bp)    # Handles product-related routes

# Route for the home page (login)
@app.route('/')
def index():
    return render_template('login.html')

# Route for the dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
