from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run()