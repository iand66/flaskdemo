from typing import ContextManager
import urllib 
from flask import Flask, render_template, flash, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Flask Instance
app = Flask(__name__)
parm = urllib.parse.quote_plus('Driver={SQL Server};Server=IANAIO;Database=Users;Trusted_Connection=yes;')
app.config['SECRET_KEY'] = 'doStuffHere'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc:///?odbc_connect=%s' % parm
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

# Create Database Models
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    color = db.Column(db.String(20))
    pass_hash = db.Column(db.String(128))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def password(self):
        raise AttributeError('Password not readable')

    @password.setter
    def password(self, password):
        self.pass_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pass_hash, password)

    def __repr__(self) -> str:
        return '<Name %r>' % self.name

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    author = db.Column(db.String(50))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(100))

# Create Form Layouts
class Registration(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email ', validators=[DataRequired()])
    color = StringField('Colour')
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords not Equal')])
    confirm = PasswordField('Confirmation',validators=[DataRequired()])
    submit = SubmitField('Submit')

class NameForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    author = StringField('Author', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Define Routes
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET','POST'])
def login():
    name = None
    password = None
    success = False
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        password = form.password.data
        user = Users.query.filter_by(name=form.name.data).first()
        if user is None:
            flash('Unknown username')
            return redirect('/')
        else:
            success = check_password_hash(user.pass_hash,password)
            return render_template('login.html', name=name, password=password, hashed=user.pass_hash, success=success)
    form.name.data = ''
    form.password.data = ''
    return render_template('user.html', form=form)

@app.route('/date')
def get_date():
    return {'Date':date.today()}

@app.route('/demo')
def demo():
    data = 'This is <strong>Bold</strong> text'
    pizza = ['Pepperoni', 'Cheese', 'Mushroom']
    return render_template('demo.html', data=data, pizza=pizza)

@app.route('/username', methods=['GET','POST'])
def username():
    name = None
    form = Registration()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            name = form.name.data
            user = Users(name=name, email=form.email.data, color=form.color.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Success')                
        else:
            flash(form.name.data + ' already registered')
        form.name.data = ''
        form.email.data = ''
        form.color.data = ''
        form.password.data = ''
    userList = Users.query.order_by(Users.date_created)
    return render_template('registration.html', name=name, form=form, users=userList)

@app.route('/username/update/<int:id>', methods=['GET','POST'])
def update(id):
    form = Registration()
    user = Users.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.color = request.form['color']
        try:
            db.session.commit()
            flash(user.name + ' updated')
            return redirect('/')
        except:
            flash('Something went wrong')
            return redirect('/')
    return render_template('update.html', form=form, name=user)

@app.route('/username/delete/<int:id>')
def delete(id):
    user = Users.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash(user.name + ' deleted')
        return redirect('/')
    except:
        flash('Something went wrong!')
        return redirect('/')

@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
        
        # Clear Form Data
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''
        
        # Update Database
        db.session.add(post)
        db.session.commit()
        
        # Notify User
        flash('Posted Successfully')

        # Render webPage
    return render_template('add_post.html', form=form)

@app.route('/posts')
def posts():
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)

@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Main App
if __name__ == '__main__':
    app.run(debug=True)