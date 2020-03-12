#!/usr/bin/python

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

URL_FILE_NAME = "urls.csv"


def loadUrlFile(url_file_name):
	"""
	Loads URLs from a file into a list
	"""
	urls = []
	with open("urls.csv") as urls_file:
		for url in urls_file:
			urls.append(url.strip())
	return urls

def getDoctorInfo(urls):
	"""
	Gets the doctor information from a list of URLs
	"""
	doctor_info_list = []
	for url in urls:
		doctor_info = parseDoctorUrl(url)
		if doctor_info is not None:
			doctor_info_list.append(doctor_info)
	return doctor_info_list

def parseDoctorUrl(url):
	"""
	Parses a single URL that points to a doctor's NSR webpage
	"""
	print(url)
	raw_html = simple_get(url)
	if raw_html is not None:
		html = BeautifulSoup(raw_html, features="html.parser")
		return html
	else:
		return None

def simple_get(url):
	"""
	Attempts to get the content at `url` by making an HTTP GET request.
	If the content-type of response is some kind of HTML/XML, return the
	text content, otherwise return None.
	"""
	try:
		with closing(get(url, stream=True)) as resp:
			if is_good_response(resp):
				return resp.content
			else:
				return None

	except RequestException as e:
		log_error('Error during requests to {0} : {1}'.format(url, str(e)))
		return None


def is_good_response(resp):
	"""
	Returns True if the response seems to be HTML, False otherwise.
	"""
	content_type = resp.headers['Content-Type'].lower()
	return (resp.status_code == 200 
			and content_type is not None 
			and content_type.find('html') > -1)


def log_error(e):
	"""
	It is always a good idea to log errors. 
	This function just prints them, but you can
	make it do anything.
	"""
	print(e)


if __name__ == "__main__":
	print("hello fuckers!!")
	urls = loadUrlFile(URL_FILE_NAME)
	doctor_info = getDoctorInfo(urls)
