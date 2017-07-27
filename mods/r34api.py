import urllib.request as urllib
from bs4 import BeautifulSoup
import os

def get_pics_from_page(tag, page_number):
	page_number = str(page_number)
	link = "http://rule34.paheal.net/post/list/{}/{}".format(tag, page_number)
	page = urllib.urlopen(link)
	soup = BeautifulSoup(page, "html.parser")
	all_links = soup.find_all('a')
	images = []
	for link in all_links:
		linka = link.get("href")
		if linka and "_images" in linka:
			images.append(linka)
	return images
	
def get_tag_last_page(tag):
	link = "http://rule34.paheal.net/post/list/{}/1".format(tag)
	page = urllib.urlopen(link)
	soup = BeautifulSoup(page, "html.parser")
	all_links = soup.find_all('a')
	linkb = ""
	for link in all_links:
		linka = link.getText()
		if(linka == "Last"):
			linkb = link.get('href')
	last_page_list_number = linkb[-5:].index("/")
	last_page = linkb[-5:][last_page_list_number+1:]
	return int(last_page)
	
def get_all_images_from_tag(tag):
	all_pages = get_tag_last_page(tag)
	images = []
	for i in range(1, all_pages + 1):
		images.extend(get_pics_from_page(tag, i))
	return images
	
def download_images(links, directory):
	number_of_images = len(lista)
	for link in links:
		name_of_file_point = link[::-1].index("/")
		name_of_file = link[-name_of_file_point:]
		if len(name_of_file) > 233:
			name_of_file = name_of_file[:233]
		urllib.urlretrieve(link, os.path.join(directory, name_of_file))
