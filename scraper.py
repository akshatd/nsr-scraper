#!/usr/bin/python

import csv

URL_FILE_NAME = "urls.csv"

def loadUrlFile(url_file_name):
	urls = []
	with open("urls.csv") as urls_file:
		for url in urls_file:
			urls.append(url)
	return urls

def getDoctorInfo(urls):
	doctor_info = []
	for url in urls:
		doctor_info.append(parseDoctorUrl(url))
	return doctor_info

def parseDoctorUrl(url):
	print(url)
	return url

if __name__ == "__main__":
	print("hello fuckers!!")
	urls = loadUrlFile(URL_FILE_NAME)
	doctor_info = getDoctorInfo(urls)
