import os
import secrets
from PIL import Image
from . import main
from .. import db,bcrypt
from ..requests import get_quotes
from ..models import User, Post
from flask import render_template,flash, redirect, url_for, request, current_app, abort
from . forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flask_login import login_user, current_user, logout_user, login_required


@main.route('/')
def index():
    quotes = get_quotes()
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template ('index.html',title = 'Home',posts=posts, quotes=quotes)

@main.route('/register', methods=['GET', 'POST'])
def register():
    quotes = get_quotes()
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your Account has been created {form.username.data}!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form, quotes=quotes)

@main.route('/login', methods=['GET', 'POST'])
def login():
    quotes = get_quotes()
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Check Email and password', 'danger')
    return render_template('login.html', title='Login', form=form, quotes=quotes)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    form_picture.save(picture_path)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)


    return picture_fn

@main.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    quotes = get_quotes()
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your Account has been updated.','success')
        return redirect(url_for('main.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form, quotes=quotes)

@main.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    quotes = get_quotes()
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your Post has been created', 'info')
        return redirect(url_for('main.index'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post', quotes=quotes)



@main.route('/post/<int:post_id>')
def post(post_id):
    quotes = get_quotes()
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title='post.title', post=post, quotes=quotes)

@main.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    quotes = get_quotes()
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your Post has been created', 'info')
        return redirect(url_for('main.post', post_id=post_id))
    elif request.method == 'GET':   
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post', quotes=quotes)

@main.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    # quotes = get_quotes()
    post = Post.query.get_or_404(post_id)
    # if post.author != current_user:
    #     abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post Deleted!', 'info')
    return redirect(url_for('main.index'))