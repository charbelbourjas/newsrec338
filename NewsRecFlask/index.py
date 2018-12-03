# pip install Flask
# pip install python-twitter
# pip install Flask-Session
# pip install numpy
# pip install sklearn
# pip install newspaper3k


from flask import Flask, redirect, url_for, render_template, request, session, jsonify
from flask_session import Session
import db_handling as ptt
import Article_Recommender as ar
import json

app = Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/articles', methods=['GET', 'POST'])
def articles():
	if request.method=='POST':
		#handle = jsonify(request['handle'])
		handle = request.form.get('handle')
		# session['handle'] = handle
		print(handle)
		data = ptt.collect_tweets(handle)
		res = ar.recommend(data) # res is json
		res = str(res).replace("'", '"')
		res = json.loads(res)
		print(res)
		url0 = str(res['data'][0]['url'])
		url1 = str(res['data'][1]['url'])
		url2 = str(res['data'][2]['url'])
		url3 = str(res['data'][3]['url'])
		print(url0)
		print(url1)
		print(url2)
		print(url3)
		return render_template('article.html', url0=url0, url1=url1, url2=url2, url3=url3)
	else:
		return "Normal"
