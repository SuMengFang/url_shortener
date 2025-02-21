from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import hashlib
import datetime
import validators
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 設定 Rate Limiting，防止濫用
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5 per minute"]  # 每個 IP 每分鐘最多 5 次請求
)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(2048), unique=True, nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)

    def to_json(self):
        return {
            "short_url": f"{request.host_url}r/{self.short_code}",
            "expiration_date": self.expiration_date.strftime("%Y-%m-%d %H:%M:%S"),
            "success": True
        }

with app.app_context():
    db.create_all()

@app.errorhandler(429)
def ratelimit_error(e):
    return jsonify({"success": False, "reason": "Too many requests. Try again later."}), 429

@app.route('/urls', methods=['POST'])
@limiter.limit("3 per minute")  # 限制請求速率
def shorten_url():
    data = request.get_json()

    # 確保請求有 JSON 內容
    if not data:
        return jsonify({"success": False, "reason": "Missing JSON payload"}), 400
    
    # 確保 `original_url` 存在
    if "original_url" not in data:
        return jsonify({"success": False, "reason": "Missing required parameter: original_url"}), 400

    original_url = data.get("original_url", "").strip()

    # 確保 `original_url` 不是空字串
    if not original_url:
        return jsonify({"success": False, "reason": "Original URL cannot be empty"}), 400

    # 驗證 URL 格式
    if not validators.url(original_url):
        return jsonify({"success": False, "reason": "Invalid URL format"}), 400

    # 檢查長度
    if len(original_url) > 2048:
        return jsonify({"success": False, "reason": "URL exceeds maximum length of 2048 characters"}), 400
    
    # 檢查資料苦是否已存在 `original_url`
    existing_entry = URL.query.filter_by(original_url=original_url).first()
    if existing_entry:
        return jsonify(existing_entry.to_json()), 200

    # 產生短網址代碼
    short_code = hashlib.md5(original_url.encode()).hexdigest()[:8]

    # 設定過期時間 (30 天)
    expiration_date = datetime.datetime.utcnow() + datetime.timedelta(days=30)

    try:
        # 存入資料庫
        new_url = URL(original_url=original_url, short_code=short_code, expiration_date=expiration_date)
        db.session.add(new_url)
        db.session.commit()

        return jsonify(new_url.to_json()), 201
    except IntegrityError:
        return jsonify({"success": False, "reason": "Short URL already exists"}), 409

@app.route('/r/<short_code>', methods=['GET'])
def redirect_short_url(short_code):
    # 確保 `short_code` 存在，且符合格式
    if not short_code or not re.match(r'^[a-zA-Z0-9]{8}$', short_code):
        return jsonify({"success": False, "reason": "Invalid short URL format"}), 400

    url_entry = URL.query.filter_by(short_code=short_code).first()

    # 查找 `short_code` 是否存在於資料庫
    if not url_entry:
        return jsonify({"success": False, "reason": "URL not found"}), 404

    # 檢查短網址是否過期
    if url_entry.expiration_date < datetime.datetime.utcnow():
        return jsonify({"success": False, "reason": "URL expired"}), 410

    return redirect(url_entry.original_url, code=302)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
