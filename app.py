from flask import Flask, redirect,render_template, request,flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newflask.db'
db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    text = db.Column(db.Text, nullable=False)



@app.route("/index")
@app.route('/')
def index():
    return render_template('index.html')

@app.route("/create", methods=['POST',"GET"])
def create():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        
        if not title or not text:
            flash('Title and text cannot be empty')
            return redirect('/create')
        
        post = Post(title=title, text=text)

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

@app.route("/reg")
def registration():
    return render_template('reg.html')


@app.route("/posts")
def posts():
    posts = Post.query.all()
    return render_template('posts.html',posts=posts)


@app.route("/post/<int:post_id>")
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)




@app.route("/about")
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
    
