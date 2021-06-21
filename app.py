from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = "doStuffHere"

class NameForm(FlaskForm):
    name = StringField("Enter Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

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
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Success")
        
    return render_template('name.html', name=name, form=form)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run()