import urllib 
from flask import Flask, render_template, flash, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

# Flask Instance
app = Flask(__name__)
parm = urllib.parse.quote_plus("Driver={SQL Server};Server=IANAIO;Database=Users;Trusted_Connection=yes;")
app.config['SECRET_KEY'] = "doStuffHere"
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % parm
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

# Create Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    color = db.Column(db.String(20))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return '<Name %r>' % self.name

# Create Form Layout
class Registration(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email ", validators=[DataRequired()])
    color = StringField("Colour")
    submit = SubmitField("Submit")

# Define Routes
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

@app.route('/demo')
def demo():
    data = "This is <strong>Bold</strong> text"
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
            user = Users(name=name, email=form.email.data, color=form.color.data)
            db.session.add(user)
            db.session.commit()
            flash("Success")                
        else:
            flash(form.name.data + " already registered")
        form.name.data = ''
        form.email.data = ''
        form.color.data = ''
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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Main App
if __name__ == "__main__":
    app.run(debug=True)