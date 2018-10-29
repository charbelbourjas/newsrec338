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

LANGUAGES = ['en']
TRACK = ['A raging measles outbreak in Europe']
ARTICLE_URLS = ['https://t.co/j9MBGCUcMX']

# NBCNews: 14173315
FOLLOW = ['14173315']



def main():
	api = twitter.Api(consumer_key=CONSUMER_KEY,
									consumer_secret=CONSUMER_SECRET,
									access_token_key=TOKEN_KEY,
									access_token_secret=TOKEN_SECRET)
	# stream(api)
	timeline(api)

def timeline(api):
	data = api.GetUserTimeline(user_id=14173315, count=200, include_rts=False)
	# data is list
	with open('timeline_output.txt', 'a') as f:
		for twt in data:
			f.write(twt.AsJsonString())
			f.write('\n')


def stream(api):
	with open('tweets_output.txt', 'a') as f:
		# filtering with follow (following ids) will also get Retweeted
		for twt in api.GetStreamFilter(follow=FOLLOW):
			# twt is dict
			# BELOW IS NOT WORKING!!
			try: 
				if twt['retweeted_status']['extended_tweet']['entities']['urls'][0]['url'] in ARTICLE_URLS:
					print('found one')
					f.write(json.dumps(twt))
					f.write('\n')
			except:
				print('error')

# example from python-twitter github:
 	# with open('output.txt', 'a') as f:
 #        # api.GetStreamFilter will return a generator that yields one status
 #        # message (i.e., Tweet) at a time as a JSON dictionary.
 #        for line in api.GetStreamFilter(track=USERS, languages=LANGUAGES):
 #            f.write(json.dumps(line))
 #            f.write('\n')
	

if __name__ == '__main__':
	main()