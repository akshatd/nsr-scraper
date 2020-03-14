#!/usr/bin/python

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import string
from unicodedata import normalize

URL_FILE_NAME = 'test.csv'

# QUAL_ROWS = 5
QUAL_COLUMNS = 3

# Qualification ROWS
QUAL_ROW_HEADING = 0
QUAL_ROW_BASIC_HEADING = 1
QUAL_ROW_BASIC_INFO = 2
QUAL_ROW_SPECIALIST_HEADING = 3
QUAL_ROW_SPECIALIST_INFO = 4

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
		qualifications = parseQualifications(main_table)
		doctor_info.update(qualifications)
		return doctor_info
	else:
		return None

def parsePersonalData(main_table):
	"""
	Parses the personal data section of a doctor
	"""
	personal_data_table = main_table.find('th', text='Personal Data').parent
	personal_data = {}
	for table_row in personal_data_table.find_next_siblings():
		data_list = table_row.find_all('td')
		if len(data_list) == 3:
			key = '(Personal) '+cleanUp(data_list[1].text)
			personal_data[key] = cleanUp(data_list[2].text)
	return personal_data

def parseClinicalPractise(main_table):
	"""
	Parses the clinical practise section of a doctor
	"""
	clinical_practise_tables = []
	for table in main_table.find_all('td', text='Clinical Practice(s)'):
		clinical_practise_tables.append(table.parent)
	
	clinical_practise = {}
	clinical_practise_no = 1
	for table in clinical_practise_tables:
		for table_row in table.find_next_siblings():
			data_list = table_row.find_all('td')
			if len(data_list) == 3:
				key = '(Clinic '+str(clinical_practise_no)+') '+cleanUp(data_list[1].text)
				clinical_practise[key] = cleanUp(data_list[2].text)
		clinical_practise_no += 1
	return clinical_practise

def parseQualifications(main_table):
	"""
	Parses the qualifications section of a doctor
	"""
	qualifications_table = main_table.find('td', text='Qualifications').parent
	# Qualifications' table is inside the heading's sibling, so get inside and find the rows
	qualifications_rows = qualifications_table.find_next_siblings()[0].find_all('tr')
	# Put rowwise data in the list
	qualifications_list = []
	for table_row in qualifications_rows:
		qualifications_list.append(table_row.find_all('td'))

	# check lengths of the important rows
	if len(qualifications_list[QUAL_ROW_HEADING]) != 3 or \
		len(qualifications_list[QUAL_ROW_BASIC_INFO]) !=3 or \
		len(qualifications_list[QUAL_ROW_SPECIALIST_INFO]) != 3:
		return {}

	qualifications = {}
	# get info for both the degrees
	for column in range(QUAL_COLUMNS):
		basic_key = ' '.join([qualifications_list[QUAL_ROW_HEADING][column].text, qualifications_list[QUAL_ROW_BASIC_HEADING][0].text])
		basic_value = qualifications_list[QUAL_ROW_BASIC_INFO][column].text
		qualifications[cleanUp(basic_key)] = cleanUp(basic_value)
		specialist_key = ' '.join([qualifications_list[QUAL_ROW_HEADING][column].text, qualifications_list[QUAL_ROW_SPECIALIST_HEADING][0].text])
		specialist_value = qualifications_list[QUAL_ROW_SPECIALIST_INFO][column].text
		qualifications[cleanUp(specialist_key)] = cleanUp(specialist_value)
	return qualifications

def cleanUp(text):
	"""
	Cleans up the HTML text to make it easily readable and printable
	"""
	# handle a case where & becomes &AMP, probably due to the HTML parser chosen for BeautifulSoup
	text = text.replace('&AMP', '&')
	# convert all random whitespace to spaces
	for ch in string.whitespace:
		text = text.replace(ch, ' ')
	# normalise unicode to get rid of weird characters like \xa0
	words = normalize("NFKD", text).split(' ')
	clean_words = []
	for word in words:
		clean_word = ''.join(char for char in word.strip() if char in string.printable)
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
	doctors_info = getDoctorInfo(urls)
	print(doctors_info)