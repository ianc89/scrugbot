import sqlite3
from sqlite3 import Error

class dbsql(object):
	def __init__(self, path):
		self.connection = None
		try:
			self.connection = sqlite3.connect(path)
			print (f"Connected to database in {path}")
		except Error as e:
			print (f"Error linking to {path} - {e}")


import csv 

class dbcsv(object):
	def __init__(self, path):
		self.csvfile = open(path, 'a', newline='')

	def write(self, row):
		writer = csv.writer(self.csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(row)
