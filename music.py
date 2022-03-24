# Class to hold information about playlists
from db import dbcsv
import pandas

class playlists(object):
	def __init__(self):
		self.dbcsv = dbcsv("playlist.csv")

	def add_entry(self, playlist_name, song_name):
		self.dbcsv.write([playlist_name,song_name])

	def list_playlists(self):
		try:
			df = pandas.read_csv(self.dbcsv.path, header=None)
		except:
			return "`No database`"
		try:
			available_playlists = df[0].unique()
		except:
			return "`No playlists`"

		ret_str = "```PLAYLISTS\n"
		for p in available_playlists:
			ret_str += " - " + p +"\n"
		ret_str += "```"
		return ret_str

	def list_songs_from_playlist(self, playlist_name):
		try:
			df = pandas.read_csv(self.dbcsv.path, header=None)
		except:
			return "`No database`"
		try:
			playlist_df = df[df[0] == playlist_name]
		except:
			return "`No playlist with that name`"

		ret_str = f"```PLAYLIST - {playlist_name}\n"
		for s in playlist_df[1]:
			ret_str += " - "+s+"\n"
		ret_str += "```"
		return ret_str

	async def list_songs(self):
		try:
			df = pandas.read_csv(self.dbcsv.path, header=None)
		except:
			return "`No database`" 
		ret_str = "```ALL SONGS\n"
		for entry in df.sort_values(by=[0,1]).values:
			ret_str += entry[0] + " - " + entry[1] + "\n"
		ret_str += "```"
		return ret_str

	def get_random_songs(self, nsongs=10):
		try:
			df = pandas.read_csv(self.dbcsv.path, header=None)
		except:
			return "`No database`" 
		try:
			random_songs = df.sample(int(nsongs))
		except:
			return f"`Provide a number of songs less than {df.shape[0]}`"

		ret_str = ""
		for s in random_songs[1]:
			ret_str += "+play " + s + "\n"
		return ret_str




