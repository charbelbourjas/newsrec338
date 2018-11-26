# pip install Flask
# pip install python-twitter
# pip install Flask-Session
# pip install numpy
# pip install sklearn
# pip install newspaper3k


from flask import Flask, redirect, url_for, render_template, request, session
from flask_session import Session
import python_twitter_test as ptt
import Article_Recommender as ar

app = Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/results')
def results():
	return render_template('results.html')

@app.route('/handleData', methods=['GET', 'POST'])
def handleData():
	if request.method=='POST':
		handle = request.get_data().decode('utf-8')
		session['handle'] = handle
		return handle
	elif request.method=='GET':
		handle = session.get('handle')
		data = ptt.get_usertweets_articles(handle, ptt.NEWS_SOURCES, ptt.CONSERVATIVE, ptt.CONSERVATIVE, ptt.POOL_METHOD)[0]
		res = ar.recommend(data)
		print(res)
		return str(res)
	else:
		return "Normal"