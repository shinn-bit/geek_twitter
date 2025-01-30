from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db, bcrypt
from app.models import User
from app.forms import RegistrationForm, LoginForm

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()  # LoginFormをインスタンス化

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            flash('ログインに成功しました！', 'success')
            return redirect(url_for('main.home'))
        flash('ログインに失敗しました。メールアドレスとパスワードを確認してください。', 'danger')

    return render_template('login.html', form=form)  # formを渡す

@auth.route('/logout')
@login_required  # ログインしていないとアクセスできない
def logout():
    logout_user()
    flash('ログアウトしました。', 'info')
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=email, password=hashed_password)
        try:
            db.session.add(user)
            db.session.commit()
            print(f"登録成功: username={user.username}, email={user.email}")
            flash('Your account has been created!', 'success')
            return redirect(url_for('auth.login'))
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"登録失敗: {e}")
            flash('登録中にエラーが発生しました。', 'danger')
    print(f"フォームエラー: {form.errors}")
    return render_template('register.html', form=form)

