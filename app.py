from flask import Flask
from models import reset_logs_with_timestamp
from routes import init_routes

app = Flask(__name__, template_folder="templates", static_folder="static"   )
app.secret_key = "secret_key_for_session_management"

# 로그 초기화
reset_logs_with_timestamp()

# 라우트 초기화
init_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
