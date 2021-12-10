

from flask import Flask, render_template
import matplotlib.pyplot as plt
import io
import base654

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def input():
    return render_template('input.html', title='FreeStyle libre Graphing',
                           description='Add daily meds and graph your post prandial glucose')


@ app.route("/graph")
def graph():
    return "<h1>Graph Goes Here</h1>"


# if __name__ == "__main__":
#     app = Flask(__name__)
