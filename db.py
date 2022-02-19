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
		self.path = path

	def write(self, row):
		csvfile = open(path, 'a', newline='')
		writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(row)
		csvfile.close()
