from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user, login_user, logout_user
from app import db, bcrypt
from app.models import User, Post
from app.forms import RegistrationForm, LoginForm, PostForm

main = Blueprint('main', __name__)

# ホームページ（投稿一覧）
@main.route('/')
def home():
    search_form = SearchForm()
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # 既にログインしている場合、ホームにリダイレクト
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)  # ユーザーをログイン状態にする
            flash('You have been logged in!', 'success')
            next_page = request.args.get('next')  # ログイン後にリダイレクトするページ
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', form=form)
# 新規投稿作成
@main.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', form=form)

# 投稿の詳細ページ
@main.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)

# 投稿の編集
@main.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)  # 権限がない場合は403エラーを返す
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('main.post_detail', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('edit_post.html', form=form)

# 投稿の削除
@main.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)  # 権限がない場合は403エラーを返す
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))
@main.route('/search', methods=['POST'])
def search():
    search_form = SearchForm()
    if search_form.validate_on_submit():
        query = search_form.query.data
        # 部分一致検索
        posts = Post.query.filter(
            (Post.title.ilike(f"%{query}%")) | 
            (Post.content.ilike(f"%{query}%"))
        ).all()
        return render_template('search_results.html', posts=posts, query=query)
    return redirect(url_for('main.home'))