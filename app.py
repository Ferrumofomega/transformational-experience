#!/usr/bin/env python
"""
app.py 

This repository contains a simpler Flask app that runs on Heroku.
The app takes as input and displays a Bokeh plot of a simple quiz question.

Link to the finished app: https://transformational-experience.herokuapp.com

The project was completed for the purpose of showing how to tie together some important concepts and
technologies, including Git, Flask, JSON, Pandas, Requests, Heroku, and Bokeh for visualization.
  
# INPUTS 
# -----------------------------------------------------------------------------|
 
  
# OUTPUTS 
# -----------------------------------------------------------------------------| 

  
# NOTES 
# -----------------------------------------------------------------------------|
to debug locally:
http://127.0.0.1:33507

 
Written 12/08/2015
By Sam Zimmerman
"""

# # Module Imports
# -----------------------------------------------------|
from flask import Flask, render_template, request, redirect
import requests
import numpy as np
import pandas as pd
import bokeh
from bokeh.plotting import figure
from bokeh.io import show
from bokeh.embed import components
import boto
import pandas

from s3_util import download_file_from_s3_bucket
from s3_util import s3_conn

bv = bokeh.__version__

# # app Flask
# -----------------------------------------------------|
app = Flask(__name__)
app.vars = {}

file_name = 'quiz_1.csv'
bucket_name = 'transformational-experience'


@app.route('/')
def main():
    return redirect('/index')


@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        # request was a POST
        app.vars['transformational'] = request.form['transformational'].upper()
        app.vars['name'] = request.form['name']
        try:
            app.vars['tag'] = 'The User Selected %s' % app.vars['transformational']
        except ValueError:
            app.vars['tag'] = 'Response not recognized'
        return redirect('/graph')


@app.route('/graph', methods=['GET', 'POST'])
def graph():
    # # Request data from S3 and get into pandas
    # # --------------------------------------------|
    csv = download_file_from_s3_bucket(file_name, bucket_name, s3_conn)
    df = pandas.read_csv(csv)
    df = df.loc[len(df)] = [app.vars['name'], app.vars['transformational']]

    #
    # # Make Bokeh plot and insert using components
    # # ------------------- ------------------------|
    # p = figure(plot_width=450, plot_height=450, title=app.vars['ticker'], x_axis_type="datetime")
    # if 'Range' in app.vars['select']:
    #     tmpx = np.array([df.Date, df.Date[::-1]]).flatten()
    #     tmpy = np.array([df.High, df.Low[::-1]]).flatten()
    #     p.patch(tmpx, tmpy, alpha=0.3, color="gray", legend='Range (High/Low)')
    # if 'Open' in app.vars['select']:
    #     p.line(df.Date, df.Open, line_width=2, legend='Opening price')
    # if 'Close' in app.vars['select']:
    #     p.line(df.Date, df.Close, line_width=2, line_color="#FB8072", legend='Closing price')
    # p.legend.orientation = "top_left"
    #
    # # axis labels
    # p.xaxis.axis_label = "Date"
    # p.xaxis.axis_label_text_font_style = 'bold'
    # p.xaxis.axis_label_text_font_size = '16pt'
    # p.xaxis.major_label_orientation = np.pi / 4
    # p.xaxis.major_label_text_font_size = '14pt'
    # p.xaxis.bounds = (df.Date.iloc[-1], df.Date.iloc[0])
    # p.yaxis.axis_label = "Price ($)"
    # p.yaxis.axis_label_text_font_style = 'bold'
    # p.yaxis.axis_label_text_font_size = '16pt'
    # p.yaxis.major_label_text_font_size = '12pt'
    #
    # # render graph template
    # # ------------------- ------------------------|
    # script, div = components(p)
    # return render_template('graph.html', bv=bv, transformational=app.vars['transformational'],
    #                        ttag=app.vars['desc'], yrtag=app.vars['tag'],
    #                        script=script, div=div)


@app.errorhandler(500)
def error_handler(e):
    return render_template('error.html', transformational=app.vars['transformational'], name=app.vars['name'])


if __name__ == '__main__':
    app.run(port=33507, debug=False)
