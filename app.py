from flask import Flask, send_from_directory
from flask_cors import CORS
import os
from config import PORT, DEBUG
from models import init_db
from routes.redirect import redirect_bp
from routes.api_auth import auth_bp
from routes.api_links import links_bp
from routes.api_stats import stats_bp

app = Flask(__name__, static_folder='frontend/dist')
CORS(app)

# 初始化数据库
init_db()

# 注册蓝图
app.register_blueprint(redirect_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(links_bp)
app.register_blueprint(stats_bp)

# 静态文件服务（开发时前端热更新，生产时托管构建产物）
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend', 'dist')

@app.route('/')
def index():
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/<path:path>')
def static_file(path):
    file_path = os.path.join(STATIC_DIR, path)
    if os.path.isfile(file_path):
        return send_from_directory(STATIC_DIR, path)
    return send_from_directory(STATIC_DIR, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
