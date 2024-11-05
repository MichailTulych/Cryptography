from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Post, db
from encryptor import encrypt, decrypt, key_schedule
import click

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

key = b'a1b2c3d4e5f6g7h8'  # Ваш 16-байтный ключ
S = key_schedule(key)  # Генерация ключа для шифрования


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Основные маршруты и функции (оставьте все как раньше)


@app.context_processor
def utility_processor():
    return dict(decrypt=decrypt)


@app.route('/')
def home():
    if current_user.is_authenticated:
        posts = Post.query.filter_by(user_id=current_user.id).all()

        for post in posts:
            try:
                # Попытка расшифровать и декодировать контент
                decrypted_content = decrypt(post.content, S)
                # Декодируем только если успешно расшифровали
                post.content = decrypted_content.decode('utf-8')
            except UnicodeDecodeError as e:
                # Если возникла ошибка, вывести сообщение в лог
                print(f"Ошибка декодирования для поста {post.id}: {e}")
                post.content = "Ошибка: не удалось расшифровать контент."
    else:
        posts = []

    return render_template('home.html', posts=posts)



@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        encrypted_content = encrypt(content.encode('utf-8'), S)
        new_post = Post(title=title, content=encrypted_content,
                        user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('create_post.html')


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash("You can't edit this post")
        return redirect(url_for('home'))
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = encrypt(request.form.get('content').encode('utf-8'), S)
        db.session.commit()
        return redirect(url_for('home'))

    # Передача расшифрованного содержания
    decrypted_content = decrypt(post.content, S).decode('utf-8')
    return render_template('edit_post.html', post=post, decrypted_content=decrypted_content)


@app.route('/delete_post/<int:post_id>')
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id == current_user.id:
        db.session.delete(post)
        db.session.commit()
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = generate_password_hash(
            request.form.get('password'), method='pbkdf2:sha256'
        )
        email = request.form.get('email')
        new_user = User(username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
