# pip install python-twitter
import os
import json
import twitter
import json
import pprint


# Consumer API Keys
CONSUMER_KEY = 'OfJ4o1ElzOcGuwAtd94amZMnn' # (API key)
CONSUMER_SECRET = 'KNYKEL2oFKZFXq6BQtNAKpXFTBqzI9RrIS8k4KA7MaDSMco5R9' # (API secret key)

# Access token & access token secret
TOKEN_KEY = '1054132964773298181-2a3tCStAeTDpyNw99j4pHoVfPJ9IFI' #(Access token)
TOKEN_SECRET = 'kyWq49CyltVmEVQ9BaF0f80cp3qjtpyaqaI79hgA8F6tK' # (Access token secret)
# Read and write (access level)

# NEWS_SOURCES_URL = [r'nbcnews.com', r'cnn.com', r'usatoday.com']
NEWS_SOURCES = [r'NBCNews', r'USATODAY', r'CNN']

MAX_TIMELINE = 200
MAX_SEARCH = 100
MAX_RETWEETERS = 100
CONSERATIVE = 10




'''
Builds query in HTML-encoded format that Twitter's Standard Search API requires.
Given a list of news sources' screen names (list of string), returns query (raw string).

Number of results (count) has a maximum of 100, default of 15.
More parameters: https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets
	%3a is ':'
 	%20 is ' '
'''
def build_query(news_sources, count):
	qry = r'q='
	for source in news_sources:
		qry += r'from%3A' + source + r'%20OR%20'

	# get rid of last 'OR ', add part to filter out retweets:
	qry = qry[:-5] + r'-filter%3Aretweets'

	# add src (typd or sprv) and count to query
	qry += r'&src=sprv&count=' + str(count)

	return qry

'''
Given a screen name (string), return the numeric Twitter id (int)
'''
def id_from_screen_name(api, name):
	return api.GetUser(screen_name=name)._json['id']

'''
Given a user's numeric Twitter id (int), returns 200 (maximum allowed) of their tweets (list of JSON dicts),
and writes it out to a file, with each line being a tweet in JSON.
'''
def timeline(api, user):
	res_twts = api.GetUserTimeline(user_id=user, count=CONSERVATIVE, include_rts=False)
	res = [twt._json for twt in res_twts]

	### res contains full json of tweets. what do we really need from it?

	file_name = str(user) + "_timeline.txt"
	with open(file_name, 'a') as f:
		for twt in res:
			f.write(json.dumps(twt))
			f.write('\n')

	return res

'''
Given a list of news sources' screen names (list of string), returns 100 (maximum allowed) of
(hopefully only) their tweets (list of JSON dicts). Should not include any retweeted, since it is straight from the source.
'''
def search(api, news_sources):
	# let's do 10 for now.
	qry = build_query(news_sources, 1) # 1 article
	res_twts = api.GetSearch(raw_query=qry)
	# res is full of Twitter status
	res = [twt._json for twt in res_twts]

	file_name = 'tweets_output.txt'
	with open(file_name, 'a') as f: # won't over-write, but will just append
		for twt in res:
			res_retwters = api.GetRetweeters(status_id=twt['id'], count=CONSERVATIVE)
			twt['retweeted_by'] = res_retwters # could be an empty list
			f.write(json.dumps(twt))
			f.write('\n')

	return res



def main():
	api = twitter.Api(consumer_key=CONSUMER_KEY,
						consumer_secret=CONSUMER_SECRET,
						access_token_key=TOKEN_KEY,
						access_token_secret=TOKEN_SECRET)
	api.CheckRateLimit()

	search(api, NEWS_SOURCES)
	timeline(api, id_from_screen_name(api, "jeffreywaaang"))

if __name__ == '__main__':
	main()





#example to get data out of file:
'''
thetweets = []
with open('tweets_output.txt') as f:
	data = f.readlines()
	for l in data:
		thetweets.append(json.loads(l))
print(thetweets[5]['retweeted_by'])
'''