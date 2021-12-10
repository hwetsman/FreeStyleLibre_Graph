

from flask import Flask, render_template
import matplotlib.pyplot as plt
import io
import base654

app = Flask(__name__)

# landing page
# To do: build out opportunity to upload data or use sample data,
#   take start and end date limits from the uploaded data and prepopulate
#   calendar choosers for user, give choice of what view to see, if the choice
#   is postprandial allow cut off and populate list of foods from data.
#   In either case allow input of meds by name, start_date and end_date.


@app.route('/', methods=['GET', 'POST'])
def input():
    return render_template('input.html', title='FreeStyle libre Graphing',
                           description='Add daily meds and graph your post prandial glucose')


@ app.route("/graph")
def graph():
    return "<h1>Graph Goes Here</h1>"


# if __name__ == "__main__":
#     app = Flask(__name__)
