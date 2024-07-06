from flask import Flask, redirect, render_template, request, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import SignupForm, LoginForm  # Импортируем формы из файла forms.py

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newflask.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('reviews', lazy=True))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    post = db.relationship('Post', backref=db.backref('reviews', lazy=False))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)




@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('signup'))
        new_user = User(username=form.username.data, password=generate_password_hash(form.password.data))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash('Registration successful! You are now logged in.', 'success')
        return redirect(url_for('index'))
    return render_template('signup.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/create", methods=['POST', 'GET'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']

        if not title or not text:
            flash('Title and text cannot be empty')
            return redirect('/create')
       
        # Проверка на уникальность заголовка
        existing_post = Post.query.filter_by(title=title).first()
        if existing_post:
            flash('A post with this title already exists', 'danger')
            return redirect('/create')

        post = Post(title=title, text=text, user_id=current_user.id)

        try:
            db.session.add(post)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding post: {e}')
            return redirect('/create')
    else:
        return render_template('create.html')


@app.route('/posts')
def posts():
    posts = Post.query.all()  # assuming you have a Post model
    return render_template('posts.html', posts=posts)

@app.route("/post/<int:post_id>")
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    reviews = Review.query.filter_by(post_id=post_id).all()
    return render_template('post_detail.html', post=post, reviews=reviews)



@app.route('/review/<int:post_id>')
def review(post_id):
    post = Post.query.get_or_404(post_id)
    reviews = Review.query.filter_by(post_id=post_id).all()
    return render_template('review.html', post=post, reviews=reviews)


@app.route('/review-create/<int:post_id>', methods=['GET', 'POST'])
@login_required
def review_create(post_id):
    if request.method == 'POST':
        title = request.form['title']
        score = int(request.form['score'])

        if not title or score < 0 or score > 10:
            flash('Invalid title or score (must be between 0 and 10)', 'danger')
            return redirect(url_for('review_create', post_id=post_id))
    
        score = min(score, 10)

        review = Review(title=title, score=score, user_id=current_user.id, post_id=post_id)

        try:
            db.session.add(review)
            db.session.commit()
            flash('Review added successfully.', 'success')
            return redirect(url_for('posts'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding review: {e}', 'danger')
            return redirect(url_for('review_create', post_id=post_id))
    else:
        return render_template('review_create.html', post_id=post_id)



@app.route('/Review/<int:review_id>')
def review_detail(review_id):
    review = Review.query.get_or_404(review_id)
    post = review.post
    return render_template("review_detail.html", review=review, post=post)


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/index")
@app.route('/')
def index():
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)