#!/usr/bin/python

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import string

URL_FILE_NAME = 'urls.csv'

def loadUrlFile(url_file_name):
	"""
	Loads URLs from a file into a list
	"""
	urls = []
	with open(url_file_name) as url_file:
		for url in url_file:
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
	raw_html = simple_get(url)
	if raw_html is not None:
		html = BeautifulSoup(raw_html, features="html.parser")
		main_table = html.find('table', attrs={'id':'tableMain'})
		doctor_info = {}
		personal_data = parsePersonalData(main_table)
		doctor_info.update(personal_data)
		clinical_practise = parseClinicalPractise(main_table)
		doctor_info.update(clinical_practise)
		return doctor_info
	else:
		return None

def parsePersonalData(main_table):
	personal_data_table = main_table.find('th', text='Personal Data').parent
	personal_data = {}
	for table_row in personal_data_table.find_next_siblings():
		data_list = table_row.find_all('td')
		if len(data_list) == 3:
			key = '(Personal) '+cleanUp(data_list[1].text)
			personal_data[key] = cleanUp(data_list[2].text)
	return personal_data

def parseClinicalPractise(main_table):
	clinical_practise_table = main_table.find('td', text='Clinical Practice(s)').parent
	clinical_practise = {}
	clinical_practise_no = 1
	for table_row in clinical_practise_table.find_next_siblings():
		data_list = table_row.find_all('td')
		if len(data_list) == 3:
			key = '(Clinic '+str(clinical_practise_no)+') '+cleanUp(data_list[1].text)
			if key in clinical_practise:
				clinical_practise_no += 1
				key = '(Clinic '+str(clinical_practise_no)+') '+cleanUp(data_list[1].text)
			clinical_practise[key] = cleanUp(data_list[2].text)
	return clinical_practise

def cleanUp(text):
	words = text.split(' ')
	clean_words = []
	for word in words:
		clean_word = ''.join(char for char in word.strip() if (char in string.printable and char not in ['\r', '\n']))
		if clean_word != '':
			clean_words.append(clean_word)

	clean_text = ' '.join(clean_words)
	return clean_text

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
