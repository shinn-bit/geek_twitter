from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user, login_user, logout_user
from app import db, bcrypt
from app.models import User, Post
from app.forms import RegistrationForm, LoginForm, PostForm, SearchForm
from flask import g
from flask_wtf import FlaskForm
from wtforms import SubmitField
from app.forms import DeleteForm

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)

# ホームページ（投稿一覧 + 検索フォーム + 投稿フォーム）
@main.route('/', methods=['GET', 'POST'])
@login_required
def home():
    post_form = PostForm()
    search_form = SearchForm()
    delete_form = DeleteForm() 

    # 投稿フォームの処理
    if post_form.validate_on_submit():
        post = Post(title=post_form.title.data, content=post_form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('投稿が作成されました！', 'success')
        return redirect(url_for('main.home'))

    # 投稿一覧の取得
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('home.html', posts=posts, post_form=post_form, search_form=search_form, delete_form=delete_form)

# ログイン
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            flash('ログインに成功しました！', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        flash('メールアドレスまたはパスワードが間違っています。', 'danger')
    return render_template('login.html', form=form)

# ログアウト
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('ログアウトしました。', 'info')
    return redirect(url_for('auth.login'))
#投稿
@main.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('投稿が作成されました！', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', form=form)

# 投稿の詳細ページ
@main.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    form = DeleteForm()  # 削除フォームを作成

    if form.validate_on_submit():  # フォームが正しく送信された場合
        if post.author != current_user:
            abort(403)
        db.session.delete(post)
        db.session.commit()
        flash('投稿が削除されました！', 'success')
        return redirect(url_for('main.home'))

    return render_template('post_detail.html', post=post, form=form)
# 投稿の編集
@main.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    
    form = PostForm()
    delete_form = DeleteForm()  # 削除用フォームを追加

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('投稿が更新されました！', 'success')
        return redirect(url_for('main.post_detail', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template('edit_post.html', form=form, delete_form=delete_form)

class DeleteForm(FlaskForm):
    submit = SubmitField('削除')
# 投稿の削除
@main.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = DeleteForm()
    if not form.validate_on_submit():  # CSRFトークンを検証
        flash('無効なリクエストです。', 'danger')
        return redirect(url_for('main.post_detail', post_id=post_id))

    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('投稿が削除されました！', 'success')
    return redirect(url_for('main.home'))
# 検索機能
@main.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    search_form = SearchForm()
    if search_form.validate_on_submit():
        query = search_form.query.data
        posts = Post.query.filter(
            (Post.title.ilike(f"%{query}%")) | 
            (Post.content.ilike(f"%{query}%"))
        ).order_by(Post.timestamp.desc()).all()
        return render_template('search_results.html', posts=posts, query=query, search_form=search_form)
    flash('有効な検索クエリを入力してください。', 'warning')
    return redirect(url_for('main.home'))
