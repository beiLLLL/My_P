
"""IELTS Sim 数据库"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class ExamRecord(db.Model):
    __tablename__ = 'exam_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    examiner = db.Column(db.String(50), default='kobe')
    difficulty = db.Column(db.String(20), default='medium')
    messages = db.Column(db.Text, default='[]')  # JSON 对话记录
    score = db.Column(db.String(20), default='')
    feedback = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
