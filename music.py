# Class to hold information about playlists
from db import dbcsv
import pandas

class playlists(object):
	def __init__(self):
		self.dbcsv = dbcsv("playlist.csv")

	def add_entry(self, playlist_name, song_name):
		self.dbcsv.write([playlist_name,song_name])

	def list_playlists(self):
		df = pandas.read_csv(self.dbcsv.path, header=None)
		available_playlists = df[0].unique()
		ret_str = "```PLAYLISTS\n"
		for p in available_playlists:
			ret_str += " - " + p +"\n"
		ret_str += "```"
		return ret_str

	def list_songs_from_playlist(self, playlist_name):
		df = pandas.read_csv(self.dbcsv.path, header=None)
		playlist_df = df[df[0] == playlist_name]
		ret_str = f"```PLAYLIST - {playlist_name}\n"
		for s in playlist_df[1]:
			print (s)
			ret_str += " - "+s+"\n"
		ret_str += "```"
		return ret_str

	def list_songs(self):
		df = pandas.read_csv(self.dbcsv.path, header=None)
		ret_str = "```ALL SONGS\n"
		for entry in df.sort_values(by=[0,1]).values:
			ret_str += entry[0] + " - " + entry[1] + "\n"
		ret_str += "```"
		return ret_str



