# Introduction
Management of glucose levels is an increasingly imporant healthcare tool. Recent advances in continuous glucose monitoring have popularlized the use of continuous glucose monitors (CGMs) such as the Abbot FreeStyle Libre. Reading the FreeStyle Libre is managed by the user with a smart phone app or a dedicated device and data is uploaded to the user's account at [Abbott's portal](https://www.libreview.com). Users can download .csv files from the portal. This project is a start at providing an analytic tool for indidviduals to use in the privacy of their own home.

# Data
While it is not usual for a git repo to contain data, I have decided to add a data file to this repo. As not everyone who will want to work on this project will have their own libreview data, a random sample file is necessary for development.

# Meds
The Libreview portal will show the user the acute effects of short acting meds such as insulin. I'd like to offer people a way to see the effects of daily meds on glucose. I want to add the ability to enter a start date and end date for daily meds and a way to graph the regression line of average daily glucose readings for the period during which the meds are taken.

# Usage
The best way to utilize this repo currently is to download the data and scripts into your own environment and run them. `python3 glucose.py` will run the script to show you the average, sd, and raw glucose readings between two hard coded time points. You can change those time points to fit your data if you don't want to use the sample data. It will show the medications below the line graphs as horizontal bars. You can use the smaple meds in the sample data or insert your own meds with start and end dates in the hardcoded meds dictionary in the script.

`python3 food_by_glu.py` will use this same sample data to extract 2 hour post-prandial periods for foods seen more than a hard coded number of times in the dataset and present a quadratic least squares 2 hour track for average glucose level by what medication the person was on when they ate the food.

# Future
As I continue to work on this project, I'll move it to a web format and allow the user to select currently hardcoded cut offs for dates, number of times a food has to appear in the dataset, etc. 

# Contributing
Fee free to fork, clone, put in a pull request or contribute in any way you see fit as long as you are willing to give away what you create here.
