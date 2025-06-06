import os
import shutil
from flask import Flask, render_template, request, send_file
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from yt_dlp import YoutubeDL
import zipfile

load_dotenv()

app = Flask(__name__)
sp = Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
))

DOWNLOAD_FOLDER = 'downloads'
ZIP_FILE = 'songs.zip'

def get_track_list(album_url):
    results = sp.album_tracks(album_url)
    return [f"{track['name']} {track['artists'][0]['name']}" for track in results['items']]

def download_mp3s(tracks):
    if os.path.exists(DOWNLOAD_FOLDER):
        shutil.rmtree(DOWNLOAD_FOLDER)
    os.makedirs(DOWNLOAD_FOLDER)

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
    }

    with YoutubeDL(ydl_opts) as ydl:
        for track in tracks:
            print(f"Downloading: {track}")
            ydl.download([f"ytsearch1:{track}"])

def zip_songs():
    if os.path.exists(ZIP_FILE):
        os.remove(ZIP_FILE)

    with zipfile.ZipFile(ZIP_FILE, 'w') as zipf:
        for file in os.listdir(DOWNLOAD_FOLDER):
            if file.endswith('.mp3'):
                zipf.write(os.path.join(DOWNLOAD_FOLDER, file), arcname=file)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        album_url = request.form['url']
        tracks = get_track_list(album_url)
        download_mp3s(tracks)
        zip_songs()
        return send_file(ZIP_FILE, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

