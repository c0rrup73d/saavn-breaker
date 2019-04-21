#!//usr/bin/python3
''' 
Author: Yogesh Bhagat

Requirements : BeautifulSoup, lxml, eyed3
''' 

import requests
import json
from bs4 import BeautifulSoup
import argparse
import sys
import eyed3

headers = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/67.0'}
base_url = 'https://www.jiosaavn.com'

def main():
	global args
	parser = argparse.ArgumentParser()
	parser.add_argument('-b',type=int,default='128',help='Bitrate of Song, if Error occurs lower the bitrate (64, 128, 320)')
	parser.add_argument('-u',type=str,help='Song URL', required=True)
	args = parser.parse_args()
	song_info(args.u)
	get_auth_url(args.b)

def get_cookies():
	global fp
	global all_cookies
	
	headers = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/67.0'}
	auth_token_url = 'https://www.jiosaavn.com/stats.php'
	token = requests.post(base_url, headers = headers)
	all_cookies = token.cookies

	fp = all_cookies['B']
	post_data = {'ev':'site:browser:fp','fp':fp}
	'''below request sends cookie B and fp to get cookie fp and ATC ''' 
	auth_token = requests.post(auth_token_url, headers = headers, data = post_data, cookies = all_cookies)
	all_cookies.update(auth_token.cookies)
	# print(all_cookies['B'])
	# print(all_cookies['_fp'])
	# print(all_cookies['ATC'])

def song_info(song):
	get_cookies()
	global song_title
	global song_album
	global song_url
	global info
	source = requests.post(song, headers = headers)
	soup = BeautifulSoup(source.text,'lxml')
	info = soup.find('div', class_='hide song-json').text
	info = json.loads(info)
	song_title = info['title']
	song_album = info['album']
	song_url = info['url']
	print("Title:",song_title)
	print("Album:",song_album)
	# print("URL:",song_url)
	# print(info)
	return song_url
	
def add_tags():
	# print(info)
	img_data = requests.get(info['image_url'])
	audiofile = eyed3.load(downloaded_song)
	audiofile.initTag()
	audiofile.tag.title = info[u'title']
	audiofile.tag.album = info[u'album']
	audiofile.tag.artist = info[u'singers']
	audiofile.tag.images.set(3, img_data.content , "image/jpeg")
	audiofile.tag.save()

def get_auth_url(bitrate):	
	global download_url
	auth_gen_url = 'https://www.jiosaavn.com/api.php'
	post_data = {'url':song_url, '__call':'song.generateAuthToken', '_marker':'false', '_format':'json','bitrate':bitrate} #here instead of song_url we can call function song_info(args.u) as it is returning a song_url
	auth_url_source = requests.post(auth_gen_url,headers = headers, data = post_data, cookies = all_cookies)
	download_url = json.loads(auth_url_source.text)['auth_url']
	download_song()

def download_song():
	global downloaded_song
	print()
	print("Downloading Song:", song_title)
	downloaded_song = song_title+'.mp3'
	song_data = requests.get(download_url,headers = headers)
	if song_data.status_code != 403:
		file = open(downloaded_song,'wb')
		file.write(song_data.content)
		file.close()
		
		add_tags()		
		
		print("Downloading Completed.")
	else:
		print("Error Downloading Song.")
	
if __name__ == '__main__':
    main()