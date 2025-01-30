from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf import CSRFProtect
# 拡張機能の初期化
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SESSION_COOKIE_SECURE'] = False  # HTTPSのみでなくてもCookieを送信
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:shinn1107@localhost:5432/geektwitter'
    csrf.init_app(app)
    # 拡張機能を初期化
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # ログイン設定
    login_manager.login_view = 'auth.login'  # 未ログイン時のリダイレクト先
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        """
        ログインユーザーをデータベースから取得する。
        """
        from app.models import User  # 遅延インポートで循環参照を回避
        return User.query.get(int(user_id))

    # Blueprint登録
    from app.routes import main  # 投稿関連のBlueprint
    app.register_blueprint(main, url_prefix='/')

    from app.auth import auth  # 認証関連のBlueprint
    app.register_blueprint(auth, url_prefix='/auth')

    return app
