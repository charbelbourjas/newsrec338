# pip install python-twitter
import os
import json
import twitter
import json
import pprint
import sqlite3
from sqlite3 import Error
from datetime import date, datetime
import pygame, sys
from pygame.locals import *
import time
 

# Consumer API Keys
CONSUMER_KEY = 'OfJ4o1ElzOcGuwAtd94amZMnn' # (API key)
CONSUMER_SECRET = 'KNYKEL2oFKZFXq6BQtNAKpXFTBqzI9RrIS8k4KA7MaDSMco5R9' # (API secret key)

# Access token & access token secret
TOKEN_KEY = '1054132964773298181-2a3tCStAeTDpyNw99j4pHoVfPJ9IFI' #(Access token)
TOKEN_SECRET = 'kyWq49CyltVmEVQ9BaF0f80cp3qjtpyaqaI79hgA8F6tK' # (Access token secret)
# Read and write (access level)

# NEWS_SOURCES_URL = [r'nbcnews.com', r'cnn.com', r'usatoday.com']
NEWS_SOURCES = [r'NBCNews', r'USATODAY', r'CNN', r'bbcworld', r'bbcbreaking', r'nytimes', r'abcnews', r'wsj']

# MAX_TIMELINE = 200 # default -- we'll always get as many tweets as we can.
MAX_SOURCES = 100
SINGULAR_SOURCE = 1
MAX_RETWEETERS = 100
CONSERVATIVE = 10
MODERATE = 50

# if 0, get pool through retweets. if 1, get through quering the url
POOL_METHOD = 1

DB_NAME = 'tweet_storage.db'
DB_CONNECTION = None
CURSOR = None
SQL_TABLE = 'CREATE TABLE IF NOT EXISTS retweeter_data (url TEXT, user_tweets TEXT, create_date DATE);'
INSERT_DATA = 'INSERT INTO retweeter_data VALUES (?,?,?)'
PULL_DATA = 'SELECT url, user_tweets FROM retweeter_data ORDER BY create_date DESC LIMIT 200'

	

def html_encode(text):
	html_escape_table = {
		# '&': r"&amp;",
		'"': r"&quot;",
		"'": r"&apos;",
		' ': r"%20",
		':': r"%3A",
		'/': r"%2F",
		'=': r"%3D"
	}
	return "".join(html_escape_table.get(c, c) for c in text)


'''
Builds query in HTML-encoded format that Twitter's Standard Search API requires.
Given a list of news sources' screen names (list of string), returns query (raw string).

Number of results (count) has a maximum of 100, default of 15.
More parameters: https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets
	%3a is ':'
	%20 is '
'''
def build_search_query(news_sources, num_articles):
	qry = r""
	for source in news_sources:
		qry += r'from:' + source + r' OR '
	# get rid of last 'OR ', add part to filter out retweets:
	qry = qry[:-3] + r'-filter:retweets'
	encoded_qry = html_encode(qry)
	# latest tweets + encoded qry + add src (typd or sprv) and count to query
	encoded_qry = r'f=tweets&vertical=news&q=' + encoded_qry + r'&src=typd&count=' + str(num_articles)
	return encoded_qry

def build_article_query(article_url, num_results):
	qry = r"url:" + article_url + " "
	qry += r'-filter:retweets'
	encoded_qry = html_encode(qry)
	encoded_qry = r'f=tweets&vertical=news&q=' + encoded_qry + r'&src=typd&count=' + str(num_results)
	return encoded_qry

'''
Given a screen name (string), return the numeric Twitter id (int)
'''
def id_from_screen_name(api, name):
	return api.GetUser(screen_name=name)._json['id']

'''
Helpers to write the full results from search and timeline to a file
'''
def write_timeline_to_file(userid, timeline):
	file_name = str(user) + "_timeline.txt"
	with open(file_name, 'a') as f:
		for twt in timeine:
			f.write(json.dumps(twt))
			f.write('\n')
	print("writing timline to file complete")
def write_search_to_file(article_tweets):
	file_name = 'tweets_output.txt'
	with open(file_name, 'a') as f: # won't over-write, but will just append
		for twt in res:
			f.write(json.dumps(twt))
			f.write('\n')




'''
Given a user's numeric Twitter id (int), returns 200 (maximum allowed) of their tweets (list of JSON dicts),
Writes it out to a file, with each line being a tweet in JSON, if write_to_file=True.

Returns tuple: (full timeline JSON, string containing all text from tweets)
'''
def timeline(api, userid, write_to_file):
	# not including retweets right now
	res_twts = api.GetUserTimeline(user_id=userid, count=200, include_rts=False)
	res = [twt._json for twt in res_twts]

	# to collect all the text in one string:
	twt_str = ""
	for twt in res:
		twt_str += twt['full_text'] + "\n"

	return twt_str, res

'''
Given a list of news sources' screen names (list of string), returns 100 (maximum allowed) of
(hopefully only) their tweets (list of JSON dicts). Should not include any retweeted, since it is straight from the source.

Returns tuple: (full search JSON, list of JSON mapping from article url to pool)
'''
def search0(api, news_sources, num_articles, pool_size, pool_method, write_to_file):
	qry = build_search_query(news_sources, num_articles) 
	print(qry)
	res_twts = api.GetSearch(raw_query=qry)
	res = [twt._json for twt in res_twts] # tweets of news article

	all_articles_pool = []
	for twt in res:
		if len(twt['entities']['urls']) != 0:
			article_pool = {} #key: url; value: list of user_ids 
			res_pool = api.GetRetweeters(status_id=twt['id'], count=pool_size)
			twt['pool'] = res_pool # could be an empty list
			article_pool['url'] = twt['entities']['urls'][0]['expanded_url']
			article_pool['pool'] = res_pool
			all_articles_pool.append(article_pool)

	article_urls = [article['url'] for article in all_articles_pool]
	return all_articles_pool, article_urls, res

'''
pool_size not used here since we are not calling the API to get retweeter id's for each article.
'''
def search1(api, news_sources, num_articles, pool_size, write_to_file):
	qry = build_search_query(news_sources, num_articles)
	print(qry)
	res_twts = api.GetSearch(raw_query=qry)
	res = [twt._json for twt in res_twts]

	# all_articles_pool = [] don't need to keep a list of retwitters anymore
	all_articles_pooltweets = []
	for twt in res: # for each article
		if len(twt['entities']['urls']) != 0:
			articles_pooltweets = {}
			pooltweets = []

			# get url
			article_url = twt['entities']['urls'][0]['expanded_url']

			# search through Twitter for this url
			qry_article = build_article_query(article_url, num_articles)
			res_twts_article = api.GetSearch(raw_query=qry_article)
			res_article = [twt._json for twt in res_twts_article]

			for twt_person in res_article: # for each person
				if twt_person['user']['verified'] == False:
					user_id = twt_person['user']['id']
					# get their tweets
					str_person_tweets = timeline(api, user_id, write_to_file=False)[0]
					pooltweets.append(str_person_tweets)

			articles_pooltweets['url'] = article_url
			articles_pooltweets['pool_tweets'] = pooltweets
			all_articles_pooltweets.append(articles_pooltweets)
	return all_articles_pooltweets


'''
all_articles_pooltweets is a list.
each element will hold a dict.
the dict will have two keys, 'url' and 'pool_tweets'.
'url' is the url of the news article.
'pool_tweets' is a list, with each element
being the string concatenation of a person in the pool's tweets.
'''
def get_articles_pooltweets(api, news_sources, num_articles, pool_size, pool_method):
	if pool_method == 0:
		res = search0(api, news_sources, num_articles, pool_size, pool_method, write_to_file=False)[0]

		all_articles_pooltweets = []

		# num_retweeters = 0 # delete?
		for article in res:
			articles_pooltweets = {}
			pooltweets = []

			for person in article['pool']:
				str_person_tweets = timeline(api, person, write_to_file=False)[0]
				pooltweets.append(str_person_tweets)
			
			articles_pooltweets['url'] = article['url']
			articles_pooltweets['pool_tweets'] = pooltweets
			all_articles_pooltweets.append(articles_pooltweets)

		return all_articles_pooltweets
	else:
		res = search1(api, news_sources, num_articles, pool_size, write_to_file=False)
		return res

'''
Takes output from get_articles_tweets and turns it into:
(one news article's url, string holding one user's tweets)

returns tuple, each element is the same but the second is in json format.
'''
def format_converter(articles_pooltweets):
	article_tuples = []
	articles_tuples_json = []
	for article in articles_pooltweets:
		for persontweets in article['pool_tweets']:
			res_json = {} # for json
			res_json['article_url'] = article['url']
			res_json['person_tweets'] = persontweets

			article_tuples.append((article['url'], persontweets))
			articles_tuples_json.append(res_json)
	return article_tuples, articles_tuples_json

# res = format_converter(get_articles_tweets())
# with open('asdf.txt', 'a') as f:
# 	f.write(str(res))


def get_usertweets_articles(twitter_handle, news_sources, num_articles, num_retweeters, pool_method):
	api = twitter.Api(consumer_key=CONSUMER_KEY,
						consumer_secret=CONSUMER_SECRET,
						access_token_key=TOKEN_KEY,
						access_token_secret=TOKEN_SECRET,
						tweet_mode='extended')

	user_tweets = timeline(api, id_from_screen_name(api, twitter_handle), write_to_file=False)[0]
	articles_pooltweets = format_converter(get_articles_pooltweets(api, news_sources, num_articles, num_retweeters, pool_method))[1]
	res_json = {}
	res_json['user_tweets'] = user_tweets
	res_json['article_pooltweets'] = articles_pooltweets

	return res_json, user_tweets, articles_pooltweets
	
# res = get_usertweets_articles("aasdfang", NEWS_SOURCES, CONSERVATIVE, CONSERVATIVE, POOL_METHOD)[0]
# with open('ex.txt', 'a') as f:
# 	f.write(json.dumps(res))

def collect_tweets(twitter_handle):
	DB_CONNECTION = None
	try:
		DB_CONNECTION = sqlite3.connect(DB_NAME)
	except Error as e:
		print(e)
	CURSOR = DB_CONNECTION.cursor()
	CURSOR.execute(SQL_TABLE)
	today = date.today()
	res_json = get_usertweets_articles(twitter_handle, NEWS_SOURCES, MODERATE, MODERATE, POOL_METHOD)
	pulled_data = res_json[2]	
	tweet_data = list()
	for i in pulled_data:
		tweet_data.append((i['article_url'],i['person_tweets'],today))
	CURSOR.executemany(INSERT_DATA, tweet_data)
	DB_CONNECTION.commit()
	new_articles_pooltweets = list()
	for row in CURSOR.execute(PULL_DATA):
		d = dict()
		d['article_url'] = row[0]
		d['person_tweets'] = row[1]
		new_articles_pooltweets.append(d)
	res_json[0]['article_pooltweets'] = new_articles_pooltweets
	DB_CONNECTION.close()
	return res_json[0]
	
def long_term_data_pull():
	pygame.init()
	pygame.display.set_mode((100,100))

	while True:
		try:
			collect_tweets("aasdfang")
			print('successful data pull')
		except Error as e:
			print('data pull error. now sleep...')
			time.sleep(1000)	

		for event in pygame.event.get():
			if event.type == QUIT: sys.exit()
			if event.type == KEYDOWN:
				sys.exit()
		pygame.event.pump()



# long_term_data_pull("aasdfang")

#example to get data out of file:
'''
thetweets = []
with open('tweets_output.txt') as f:
	data = f.readlines()
	for l in data:
		thetweets.append(json.loads(l))
print(thetweets[5]['retweeted_by'])
'''