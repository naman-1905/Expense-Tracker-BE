from flask import Flask
from routes.history import history_bp

app = Flask(__name__)
app.register_blueprint(history_bp, url_prefix="/history")

if __name__ == "__main__":
    app.run(port=5002, debug=True)
