from flask import Flask, redirect, url_for, render_template
from python_twitter_test import *

app = Flask(__name__)
handle = ""

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/results', methods=['GET', 'POST'])
def results():
	return render_template('results.html')

