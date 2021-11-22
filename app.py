

from flask import Flask

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST']
def input():
    return "<h1>Freestyle Libre Data Reader</h1>"


@ app.route("/graph")
def graph():
    return "<h1>Graph Goes Here</h1>"


# if __name__ == "__main__":
#     app = Flask(__name__)
