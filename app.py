"""IELTS Speaking Simulator — AI 雅思口语模拟"""
from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models import db, User

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access the exam.'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# 蓝图
from routes.auth import auth_bp
from routes.exam import exam_bp

app.register_blueprint(auth_bp)
app.register_blueprint(exam_bp)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True, use_reloader=False)


# 生产环境自动建表（PythonAnywhere 等 WSGI 部署不会触发 __main__）
with app.app_context():
    db.create_all()
