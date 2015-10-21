#!flask/bin/python

from flask import Flask

app = Flask(__name__)

@app.template_filter('adate')
def adate(value, format='%b %d, %Y'):
    # value is a datetime object
    # returns date as Oct 3, 2015
    return value.strftime(format)
