from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化扩展
    db.init_app(app)
    CORS(app)
    
    # 注册路由
    from app.routes import api
    app.register_blueprint(api.bp)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app