import flickrapi
from flickrapi import shorturl 
import tweepy
import time
from bs4 import BeautifulSoup
from random import choice, randint, shuffle, random
import xml.etree.ElementTree as ET
import urllib
import csv

from secret import FLICKR_KEY, FLICKR_SECRET, TWITTER_KEY, TWITTER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
from config import USER_ID, TAGS, MIN_HEIGHT, MIN_WIDTH

from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

photo_list = []
random_page = randint(1, 100)


def apollo():
	csv.register_dialect('pipes', delimiter='|')
	with open('photoData.csv','rb') as f:
		reader = csv.reader(f,dialect='pipes')
		for row in reader:
			#print row[0]
			imageNumbers = row[1]
			check = imageNumbers[0] == "1"
			if check:
				photo_list.append(row)

	p_choice = choice(photo_list)
	imageTime = p_choice[0]
	imageTimeParsed = imageTime[0]+imageTime[1]+imageTime[2]+":"+imageTime[3]+imageTime[4]+":"+imageTime[5]+imageTime[6]
	imageNumber = p_choice[1]
	imageDescription = p_choice[4]
	if len(imageDescription)>114:
		imageDescription = imageDescription[0:111] + "..."

	imageURL = "http://apollo17.org/mission_images/flight/1024/AS17-"+ imageNumber +".jpg"
	apolloURL = "apollo17.org/?t=" + imageTimeParsed

	#save the image
	urllib.urlretrieve(imageURL,'image.jpg')
	text = imageDescription + " " + apolloURL
	return text 


	 

def flickr():
	flickr = flickrapi.FlickrAPI(FLICKR_KEY, FLICKR_SECRET, format='etree')

	photos = flickr.photos_search(
		per_page = 100, 
		page = random_page, 
		user_id = USER_ID,
		tag_mode = 'any',
		extras = 'url_c,description', 
		sort = 'relevance'
	)

	soup = BeautifulSoup(ET.tostring(photos, encoding='utf8', method='xml'), "html.parser")
	possibilities = soup.find_all('photo')
	
	for p in possibilities:
		tag = p.has_attr('url_c')
		description = p.findNext('description').contents[0]
		length = len(description)
		if tag and length<116: #minus away a spacing and 23 character for short url 
			photo_list.append(p)
		

	#print photo_list
	p_shuffle = shuffle(photo_list)
	p_choice = choice(photo_list)


	p_url = p_choice['url_c']
	p_id = p_choice['id']
	p_owner = p_choice['owner']
	p_description = p_choice.findNext('description').contents[0]
	p_weburl = "https://www.flickr.com/photos/" + p_owner + "/" + p_id
	p_shorturl = shorturl.url(p_id)
	print p_shorturl
	urllib.urlretrieve(p_url, "image.jpg")
	text = p_description + " " + p_shorturl
	return text
	#return p_weburl
	    

def twitter():
	auth = tweepy.OAuthHandler(TWITTER_KEY, TWITTER_SECRET)
	auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

	api = tweepy.API(auth)
	status = apollo()
	media = 'image.jpg'
	api.update_with_media(media, status=status)

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
def main():
	apollo()
	print('Looking for pictures')
	#flickr()
	print('Picked a APOLLO image')
	twitter()
	print('Posted the image to Twitter')


sched.start()