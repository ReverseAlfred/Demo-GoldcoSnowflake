from flask import Flask, render_template
from auth import auth_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(auth_bp)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
