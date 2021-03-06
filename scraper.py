#!/usr/bin/python

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import string
from unicodedata import normalize
from csv import DictWriter
from time import sleep
import progressbar
import argparse
import sys

HTTP_REQUEST_WAIT = 0.1

# QUAL_ROWS = 5
QUAL_COLUMNS = 3

# Qualification ROWS
QUAL_ROW_HEADING = 0
QUAL_ROW_BASIC_HEADING = 1
QUAL_ROW_BASIC_DATA = 2
QUAL_ROW_SPECIALIST_HEADING = 3
QUAL_ROW_SPECIALIST_DATA = 4

progressbar_widgets=[
	' [', progressbar.Timer(), '] ',
	progressbar.Percentage(),
	progressbar.Bar(),
	' (', progressbar.ETA(), ') ',
]

def loadUrlFile(url_file_name):
	"""
	Loads URLs from a file into a list
	"""
	print("\nLoading URLs from " + url_file_name + "...", end = ' ')
	urls = []
	try:
		with open(url_file_name) as url_file:
			for url in url_file:
				url_stripped = url.strip()
				if url_stripped != '':
					urls.append(url.strip())
	except FileNotFoundError:
		print("The file " + url_file_name + " does not exist!")
		sys.exit(-1)
	print("done")
	return urls

def getDoctorData(urls):
	"""
	Gets doctor data from a list of URLs
	"""
	print("\nParsing doctor data from the URLs")
	doctor_data_list = []
	for url in progressbar.progressbar(urls, widgets=progressbar_widgets):
		sleep(HTTP_REQUEST_WAIT)
		doctor_data = parseDoctorUrl(url)
		if doctor_data is not None:
			doctor_data_list.append(doctor_data)
	return doctor_data_list

def parseDoctorUrl(url):
	"""
	Parses a single URL that points to a doctor's NSR webpage
	"""
	raw_html = simple_get(url)
	if raw_html is not None:
		html = BeautifulSoup(raw_html, features="html.parser")
		main_table = html.find('table', attrs={'id':'tableMain'})
		doctor_data = {}
		personal_data = parsePersonalData(main_table)
		doctor_data.update(personal_data)
		clinical_practise = parseClinicalPractise(main_table)
		doctor_data.update(clinical_practise)
		qualifications = parseQualifications(main_table)
		doctor_data.update(qualifications)
		return doctor_data
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
		len(qualifications_list[QUAL_ROW_BASIC_DATA]) !=3 or \
		len(qualifications_list[QUAL_ROW_SPECIALIST_DATA]) != 3:
		return {}

	qualifications = {}
	# get info for both the degrees
	for column in range(QUAL_COLUMNS):
		basic_key = ' '.join([qualifications_list[QUAL_ROW_HEADING][column].text, qualifications_list[QUAL_ROW_BASIC_HEADING][0].text])
		basic_value = qualifications_list[QUAL_ROW_BASIC_DATA][column].text
		qualifications[cleanUp(basic_key)] = cleanUp(basic_value)
		specialist_key = ' '.join([qualifications_list[QUAL_ROW_HEADING][column].text, qualifications_list[QUAL_ROW_SPECIALIST_HEADING][0].text])
		specialist_value = qualifications_list[QUAL_ROW_SPECIALIST_DATA][column].text
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

def saveDictListToCsv(list_of_dicts, output_filename):
	"""
	Save a list of dictionaries to a file
	"""
	print("\nSaving to " + output_filename + "...", end = ' ')
	fieldnames = set()
	for d in list_of_dicts:
		fieldnames.update(d.keys())

	with open(output_filename, 'w') as output_file:
		writer = DictWriter(output_file, fieldnames=sorted(fieldnames))
		writer.writeheader()
		writer.writerows(list_of_dicts)
	
	print("done")

if __name__ == "__main__":
	print("Welcome to this NSR scraper!!")
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input", help="Input URL file", type=str, default="urls.csv")
	parser.add_argument("-o", "--output", help="Outut CSV file", type=str, default="doctors.csv")
	arguments = parser.parse_args()

	urls = loadUrlFile(arguments.input)
	doctor_data = getDoctorData(urls)
	saveDictListToCsv(doctor_data, arguments.output)
