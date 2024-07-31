from flask import Flask, redirect, url_for
from auth import auth_bp
from dashboard import dashboard_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change to a secure key

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True)
