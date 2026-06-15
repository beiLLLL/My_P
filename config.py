"""IELTS Speaking Simulator 配置"""
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'ielts-secret-key-2024')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///ielts.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', '')
    LLM_MODEL = 'deepseek-chat'
