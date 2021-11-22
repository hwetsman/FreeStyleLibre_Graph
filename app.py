

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def input():
    return render_template('input.html')


@ app.route("/graph")
def graph():
    return "<h1>Graph Goes Here</h1>"


# if __name__ == "__main__":
#     app = Flask(__name__)
