from flask import Flask
from auth import auth_bp
from dashboard import dashboard_bp
from stores import stores_bp

app = Flask(__name__)
app.config.from_object('config.Config')

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(stores_bp, url_prefix='/stores')

if __name__ == "__main__":
    app.run(debug=True)
