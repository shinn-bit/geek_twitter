from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'user'  # テーブル名を指定
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # ユーザーと投稿のリレーションシップ
    posts = db.relationship('Post', back_populates='author', lazy=True)

    def set_password(self, password):
        """
        パスワードをハッシュ化して保存する。
        """
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """
        入力されたパスワードが保存されたハッシュと一致するかを確認する。
        """
        return check_password_hash(self.password, password)


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # タイムスタンプを追加
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # 投稿とユーザーのリレーションシップ
    author = db.relationship('User', back_populates='posts', lazy=True)
