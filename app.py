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

def create_app():
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(store_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(planogram_bp)
    app.register_blueprint(cluster_bp)
    app.register_blueprint(floorplan_bp)
    app.register_blueprint(position_bp)
    app.register_blueprint(performance_bp)

    # Route for the home page (login)
    @app.route('/')
    def index():
        return render_template('login.html')

    # Route for the dashboard
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    # Custom 404 error handler
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app

# Run the application
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
