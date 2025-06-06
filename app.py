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
    return [f"{item['track']['name']} - {item['track']['artists'][0]['name']}" for item in results['items']]

# Improved function to get first YouTube video link
def get_first_youtube_link(query, track_name=None, artist_name=None):
    search_query = f"{query} official audio OR official video"

    request = youtube.search().list(
        q=search_query,
        part='snippet',
        maxResults=3,  # Fetch top 3 to pick best match
        type='video'
    )
    response = request.execute()

    if response['items']:
        # Try to match a video with both track name and artist in title
        for item in response['items']:
            video_title = item['snippet']['title'].lower()
            if track_name and artist_name:
                if track_name.lower() in video_title and artist_name.lower() in video_title:
                    video_id = item['id']['videoId']
                    return f"https://www.youtube.com/watch?v={video_id}"

        # If no perfect match, fallback to first result
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
            # Split track into name and artist
            if ' - ' in track:
                track_name, artist_name = track.split(' - ', 1)
            else:
                # fallback split on first space if needed
                parts = track.split(' ')
                track_name = parts[0]
                artist_name = ' '.join(parts[1:]) if len(parts) > 1 else ''

            link = get_first_youtube_link(track, track_name, artist_name)
            track_links.append({'track': track, 'link': link})

        return render_template('index.html', track_links=track_links)

    return render_template('index.html', track_links=None)

# Run app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
