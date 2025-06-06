import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

# Setup Flask
app = Flask(__name__)

# Setup Spotify API
sp = Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
))

# Setup YouTube API
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Function to get tracks from Spotify playlist
def get_track_list(playlist_url):
    playlist_id = playlist_url.split("/")[-1].split("?")[0]
    results = sp.playlist_tracks(playlist_id)
    return [f"{item['track']['name']} {item['track']['artists'][0]['name']}" for item in results['items']]

# Function to get first YouTube video link
def get_first_youtube_link(query):
    request = youtube.search().list(
        q=query + " audio",
        part='snippet',
        maxResults=1,
        type='video'
    )
    response = request.execute()
    if response['items']:
        video_id = response['items'][0]['id']['videoId']
        return f"https://www.youtube.com/watch?v={video_id}"
    else:
        return None

# Flask route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        playlist_url = request.form['url']
        tracks = get_track_list(playlist_url)

        track_links = []
        for track in tracks:
            link = get_first_youtube_link(track)
            track_links.append({'track': track, 'link': link})

        return render_template('index.html', track_links=track_links)

    return render_template('index.html', track_links=None)

# Run app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
