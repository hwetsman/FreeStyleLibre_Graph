# Introduction
Management of glucose levels is an increasingly important healthcare tool. Recent advances in continuous glucose monitoring have popularized the use of continuous glucose monitors (CGMs) such as the Abbot FreeStyleLibre. Reading the FreeStyleLibre is managed by the user with a smart phone app or a dedicated device and data is uploaded to the user's account at [Abbott's Libreview portal](https://www.libreview.com). Users can download .csv files from the portal. This project is a start at providing an analytic tool for individuals to use in the privacy of their own home.

# Data
While it is not usual for a git repo to contain data, I have decided to add a data file to this repo. As not everyone who will want to work on this project will have their own Libreview data, a random sample file is necessary for development.

# Meds
The Libreview portal will show the user the acute effects of short acting meds such as insulin. I'd like to offer people a way to see the effects of daily meds on glucose. I want to add the ability to enter a start date and end date for daily meds and a way to graph the regression line of average daily glucose readings for the period during which the meds are taken.

# Usage
## glucose.py
The best way to utilize this repo currently is to download the data and scripts into your own environment and run them. Currently, `python3 glucose.py` will run that script to show you the rolling 7-day average, sd, and raw glucose readings between two hard coded time points. You can change those time points to fit your data if you don't want to use the sample data. It will show the medications below the line graphs as horizontal bars. You can use the sample meds in the sample data or insert your own meds with start and end dates in the hardcoded meds dictionary in the script.

## food_by_glu.py
Clone the repo, set up your venv, and run `pip3 install -r requirements.txt` from within the directory where food_by_glu.py resides.
You can use `streamlit run food_by_glu.py` to run this script that will create a visualization of 2 hour post-prandial glucose response by medication. The plot is a quadratic model of the mean glucose at each minute post-prandial for each medication. It takes the start and stop dates of up to two daily meds in order to show comparisons of those two meds. One med of choice could be 'No Med' if the user choses and enters dates when no daily med was taken. This is version 0.1 of the app. It uses Streamlit to generate an interactive browser window.

# Future
As I continue to work on this project, I'll move it to a web format and allow the user to select currently hardcoded cut offs for dates, number of times a food has to appear in the dataset, etc.

# Contributing
Fee free to fork, clone, put in a pull request or contribute in any way you see fit as long as you are willing to give away what you create here.
