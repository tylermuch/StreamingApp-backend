from flask import *
import os, json, logging
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.mp3 import EasyMP3
import mutagen

'''
The directory structure:

root
|----artist1
|       |----album1
|               |----song1
|               |----song2
|       |----album2
|               |----song1
|----artist2
|       |----album1
|               |----song1
|               |----song2
|       |----album2
|               |----song1
'''
raise NameError('This must be set to the root of your music directory.')
root = ''

app = Flask(__name__)
app.debug = True

@app.route("/list", methods=['GET'])
def getListArtists():
	artists = getArtists()
	return Response(json.dumps(artists), mimetype='application/json')

@app.route("/list/<artist>", methods=['GET'])
def getListAlbumsForArtist(artist):
	albums = getAlbums(artist)
	return Response(json.dumps(albums), mimetype='application/json')

@app.route("/list/<artist>/<album>", methods=['GET'])
def getListSongsForAlbum(artist, album):
	songs = getSongs(artist, album)
	return Response(json.dumps(songs), mimetype='application/json')


@app.route("/listall", methods=['GET'])
def getListAll():
	listing = []

	# get all artist directories in root folder
	artists = getArtists()

	# generate artist entry
	for artist in artists:
		artistentry = {"artist": artist}
		artistentry["albums"] = []
		artistentry["songs"] = []
		albums = getAlbums(artist)
		# generate album entry
		for album in albums:
			albumentry = {"album": album}
			albumentry["songs"] = []
			songs = getSongs(artist, album)
			# generate song entry
			for song in songs:
				'''
				s = mutagen.File(os.path.join(root, artist, album, song), easy=True)
				try:
					title = s['title']
				except KeyError:
					print "Key 'title' does not exist"
				'''
				title, length, tracknum = getFileInfo(os.path.join(root, artist, album, song))
				#assert not isinstance(title, list)
				songentry = {"title": title or song}
				if length is not None:
					songentry['duration'] = length
				if tracknum is not None:
					songentry['tracknum'] = tracknum
				albumentry["songs"].append(songentry)
			artistentry["albums"].append(albumentry)

		# generate song entries for songs by this artist but that are not listed under an album
		songs = getSongs(artist)
		for song in songs:
			title, length, _ = getFileInfo(os.path.join(root, artist, song))
			songentry = {"title": title or song}
			if length is not None:
				songentry['duration'] = length
			artistentry["songs"].append(songentry)

		listing.append(artistentry)
	return Response(json.dumps(listing), mimetype='application/json')

def getFileInfo(path):
	s = mutagen.File(path, easy=True)
	title = None
	length = None
	tracknum = None
	try:
		title = s['title']
		tracknum = s['tracknumber']
		if (path.endswith(".mp3")):
			mp3 = MP3(path)
			length = mp3.info.length
	except KeyError:
		pass

	# It really doesn't make sense to me for title to be a list but I guess it is...
	# I have never seen it with more than one entry
	# ...same with tracknum I guess
	title = title[0] if title is not None else None
	tracknum = tracknum[0] if tracknum is not None else None
	return title, length, tracknum

def getValidSubdirs(path):
	return [d for d in os.listdir(os.path.join(root, path)) if os.path.isdir(os.path.join(root, path, d)) and not d.startswith('.')]
def getArtists():
	return getValidSubdirs(root)
def getAlbums(artist):
	return getValidSubdirs(os.path.join(root, artist))
def getSongs(artist, album = ''):
	path = os.path.join(root, artist, album)
	return [d for d in os.listdir(path) if not os.path.isdir(os.path.join(path, d)) and not d.startswith('.') and d.endswith('.mp3')]

if __name__ == "__main__":
	app.run('0.0.0.0')
	#mp3info = EasyID3(r"/home/tyler/music/Benjamin Francis Leftwich/Shine (Kygo Remix).mp3")
	#print mp3info.items()
'''
	audio = mutagen.File("test.mp3", easy=True)
	try:
		print audio['artist']
		print audio['title']
		print audio['performer']
		print audio['length']
	except KeyError as e:
		print "Key", e, "does not exist."
'''
