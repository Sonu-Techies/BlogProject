import datetime
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import redirect
from flask import session

app = Flask(__name__)
app.secret_key = "super secret key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

db = SQLAlchemy(app)
migrate = Migrate(app,db,render_as_batch=True)


admin_uname = '1234'
admin_pwd = '1234'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)

class UserDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    pwd = db.Column(db.String, nullable=False)

class BlogDB(db.Model):
    bId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    published_date = db.Column(db.DateTime, default=datetime.datetime.now)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    category = db.Column(db.Integer, db.ForeignKey(Category.id), nullable=True)

@app.route('/')
def index():
    if 'user' in session:
        if session['user'] == int(admin_uname):
            return redirect('/admin-dashboard')
        else:
            id = session['user']
            return redirect(f'/user/{id}')
    blog_list = BlogDB.query.order_by(BlogDB.published_date.desc()).all()
    return render_template('index.html', books=blog_list or [])


@app.route('/admin-dashboard')
def adminDashboard():
    if 'user' in session:
        val = session['user']
        if val == int(admin_uname):
            bloglist = BlogDB.query.order_by(BlogDB.published_date.desc()).all()
            return render_template('admin_dashboard.html', books=bloglist or [])
        else:
            return redirect(f'/user/{val}')
    else:
        return redirect('/')


@app.route('/update-blog/<int:id>', methods=['GET', 'POST'])
def updateBlog(id):
    if 'user' in session:
        val = session['user']
        if val == int(admin_uname):
            book = BlogDB.query.filter_by(bId=id).scalar()
            if request.method == 'POST':
                book.title = request.form.get('title')
                book.author = request.form.get('author')
                book.content = request.form.get('content')
                db.session.commit()
                return redirect('/admin-dashboard')
            else:
                return render_template('update_book.html', book=book)
        else:
            return redirect(f'/user/{val}')
    else:
        return redirect('/')
    # add new book


@app.route('/add-book', methods=['POST'])
def addBook():
    if 'user' in session:
        val = session['user']
        if val == int(admin_uname):
            title = request.form.get('blogName')
            author = request.form.get('authorName')
            content = request.form.get('content')
            newblog = BlogDB(title=title, author=author, content=content)
            db.session.add(newblog)
            db.session.commit()
            return redirect('/admin-dashboard')
        else:
            return redirect(f'/user/{val}')
    else:
        return redirect('/')


@app.route('/delete-blog/<int:id>', methods=['POST', 'GET'])
def deleteBlog(id):
    if 'user' in session:
        if session['user'] == int(admin_uname):
            if request.method == 'POST':
                blog_to_delete = BlogDB.query.get_or_404(id)
                try:
                    db.session.delete(blog_to_delete)
                    db.session.commit()
                    return redirect('/admin-dashboard')
                except:
                    return 'There was a problem deleting that task.'
            else:
                return redirect('/admin-dashboard')
        else:
            s_id = session['user']
            return redirect(f'/user/{s_id}')
    else:
        return redirect('/sign-in')


@app.route('/sign-in', methods=['POST', 'GET'])
def signin():
    if 'user' in session:
        if session['user'] == int(admin_uname):
            return redirect('/admin-dashboard')
        else:
            id = session['user']
            return redirect(f'/user/{id}')

    if request.method == 'POST':
        id = int(request.form.get('id'))
        password = int(request.form.get('password'))
        if id == int(admin_uname):
            if password == int(admin_pwd):
                session['user'] = id
                return redirect('/admin-dashboard')
            else:
                return render_template('handle_login.html', loginType=True, errMsg="Invalid Credentials...")
        user = UserDB.query.filter_by(id=id).scalar()
        print(user)
        if user is not None:
            if user.pwd == password:
                session['user'] = id
                return redirect(f'/user/{id}')
            else:
                return render_template('handle_login.html', loginType=True, errMsg="Invalid Credentials...")
        else:
            return render_template('handle_login.html', loginType=True, errMsg="Invalid Credentials...")
    return render_template('handle_login.html', loginType=True, errMsg=False)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if 'user' in session:
        if session['user'] == int(admin_uname):
            return redirect('/admin-dashboard')
        else:
            id = session['user']
            return redirect(f'/user/{id}')

    if request.method == 'POST':
        val = request.form.get('id')
        password = request.form.get('pwd')
        name = request.form.get('uname')
        id = int(val)

        user = UserDB.query.filter((UserDB.id == id) | (UserDB.name == name)).scalar()
        if id == admin_uname or user is not None:
            return render_template('handle_login.html', loginType=False, errMsg="User Already Exists...")
        else:
            newUser = UserDB(id=id, name=name, pwd=password)
            db.session.add(newUser)
            db.session.commit()
            session['user'] = id
            return redirect(f'/user/{id}')
    return render_template('handle_login.html', loginType=False, errMsg=False)

@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
        return redirect('/')
    return redirect('/')


@app.route("/user/<int:id>", methods=['POST'])
def searchBooks(id):
    if 'user' in session:
        books = BlogDB.query.all()
        search = request.form["KeyWord"]
        s_id = session['user']
        user = UserDB.query.filter_by(id=s_id).scalar()
        lbook = BlogDB.query.filter(BlogDB.title.startswith(search)).all()
        return render_template('student.html', booksName=lbook, search=1, user=user)
    else:
        return redirect('/')


@app.route('/user/<int:id>')
def studentDash(id):
    if 'user' in session:
        val = session['user']
        if val == int(admin_uname):
            return redirect('/admin-dashboard')
        if val != id:
            return redirect(f'/user/{val}')
        booklist = BlogDB.query.all().sort(reverse=True)
        user = UserDB.query.filter_by(id=id).scalar()
        if user is None:
            return redirect(f'/user/{val}')
        return render_template('student.html', books=booklist or [], user=user)
    else:
        return redirect('/')


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, port=5555)