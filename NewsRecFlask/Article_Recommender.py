
import json
import pprint
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.neighbors import NearestNeighbors
from newspaper import Article

data = None
user_data = None
num_neighbors = 6


def process_data(filepath):
	data = None
	with open(filepath) as f:
	    data = json.load(f)
	text_data = list()
	url_data = list()
	for i in data['article_pooltweets']:
	    text_data.append(i['person_tweets'])
	    url_data.append(i['article_url'])
	return (data['user_tweets'], text_data, url_data)

def process_data2(data_input):
	data = data_input
	text_data = list()
	url_data = list()
	for i in data['article_pooltweets']:
	    text_data.append(i['person_tweets'])
	    url_data.append(i['article_url'])
	return (data['user_tweets'], text_data, url_data)


def get_matches(urls, indices):
	matches = list()
	for i in indices[0]:
		if i!=0:
			matches.append(urls[i-1])
	return list(set(matches))


def get_keywords(urls):
	ls = list()
	for url in urls:
		d = dict()
		d['url'] = url
		article = Article(url, language="en")
		article.download() 
		article.parse() 
		article.nlp()
		d['keywords'] = article.keywords 
		ls.append(d)
	return ls


def recommend(data):
	data = process_data2(data)
	text_data = data[1]
	url_data = data[2]
	user_data = data[0]
	count_vect = CountVectorizer()
	tfidf_transformer = TfidfTransformer()
	X_train_counts = count_vect.fit_transform([user_data]+text_data)
	X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
	clf = NearestNeighbors(num_neighbors, algorithm='auto').fit(X_train_tfidf)
	distances, indices = clf.kneighbors(X_train_tfidf[0])
	output = dict()
	output['data'] = get_keywords(get_matches(url_data, indices))
	return output

# def main():
# 	return 1
	# data = process_data('ex.txt')
	# text_data = data[1]
	# url_data = data[2]
	# user_data = data[0]
	# count_vect = CountVectorizer()
	# tfidf_transformer = TfidfTransformer()
	# X_train_counts = count_vect.fit_transform([user_data]+text_data)
	# X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
	# clf = NearestNeighbors(num_neighbors, algorithm='auto').fit(X_train_tfidf)
	# distances, indices = clf.kneighbors(X_train_tfidf[0])
	# output = dict()
	# output['data'] = get_keywords(get_matches(url_data, indices))
	# with open('recommended_articles.txt', 'w') as outfile:  
	# 	json.dump(output, outfile)


# if __name__ == '__main__':
# 	main()

