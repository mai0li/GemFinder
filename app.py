import json
import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search_album', methods=['POST'])
def search_album():
    album_name = request.form.get('album_name')  # Safer access to form data

    if not album_name:
        return jsonify({"error": "Album name is required"}), 400

    # Implement the logic to search for the album by name and return its ID

    authToken = os.environ.get('AUTH_TOKEN')
    clientToken = os.environ.get('CLIENT_TOKEN')
    response = requests.get(
    url='https://api-partner.spotify.com/pathfinder/v1/query',
    params={
        "operationName":"searchAlbums",
        "variables":f"{{\"searchTerm\":\"{album_name}\",\"offset\":0,\"limit\":30,\"numberOfTopResults\":20,\"includeAudiobooks\":true,\"includePreReleases\":false}}",
        "extensions":"{\"persistedQuery\":{\"version\":1,\"sha256Hash\":\"4ddf4d062c3c268954bb113ca2a24c6440e8c832170185388a087ca8608c727c\"}}"
    },
    headers={
        "Host":"api-partner.spotify.com",
        "origin":"https://xpui.app.spotify.com",
        "user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.130 Spotify/1.2.37.701 Safari/537.36",
        "accept":"application/json",
        "accept-language":"en",
        "app-platform":"Linux",
        "authorization":f"Bearer {authToken}", 
        "client-token":f"{clientToken}",
        "content-type":"application/json;charset=UTF-8",
        "sec-ch-ua":"\"Not(A:Brand \";v=\"24 \", \"Chromium \";v=\"122 \"",
        "sec-ch-ua-mobile":"?0",
        "sec-ch-ua-platform":"\"Linux \"",
        "spotify-app-version":"1.2.37.701",
        "sec-fetch-site":"same-site",
        "sec-fetch-mode":"cors",
        "sec-fetch-dest":"empty",
        "referer":"https://xpui.app.spotify.com/"
        },
    )
    probableAlbum = jsonify(response.json()).stream.response.json["data"]["searchV2"]["albumsV2"]["items"][0]
    # here's an example of probableAlbum:
    # {"__typename": "AlbumResponseWrapper", "data": {"__typename": "Album", "artists": {"items": [{"profile": {"name": "Los Hermanos"}, "uri": "spotify:artist:7Brxri4l1ATShikyHXsEr6"}]}, "coverArt": {"extractedColors": {"colorDark": {"hex": "#184860", "isFallback": false}}, "sources": [{"height": 300, "url": "https://i.scdn.co/image/ab67616d00001e02376d029f01458b3e714603b1", "width": 300}, {"height": 64, "url": "https://i.scdn.co/image/ab67616d00004851376d029f01458b3e714603b1", "width": 64}, {"height": 640, "url": "https://i.scdn.co/image/ab67616d0000b273376d029f01458b3e714603b1", "width": 640}]}, "date": {"year": 2003}, "name": "Ventura", "uri": "spotify:album:7KMAiyOVyJLIqWxsWD7Lmd"}}
    # let's extract the album ID, cover art, album name and artist name, so we can call albumInfo later
    albumDetails = {
        'albumId': probableAlbum["data"]["uri"].split(":")[2],
        'albumCover': probableAlbum["data"]["coverArt"]["sources"][0]["url"],
        'albumDate': probableAlbum["data"]["date"]["year"],
        'albumName': probableAlbum["data"]["name"],
        'artistName': probableAlbum["data"]["artists"]["items"][0]["profile"]["name"]
    }

    def get_album_info(albumId):

        authToken = os.environ.get('AUTH_TOKEN')
        clientToken = os.environ.get('CLIENT_TOKEN')

        response = requests.get(
        url='https://api-partner.spotify.com/pathfinder/v1/query',
        params={
            "operationName":"getAlbum",
            "variables":f"{{\"uri\":\"spotify:album:{albumId}\",\"locale\":\"\",\"offset\":0,\"limit\":50}}",
            "extensions":"{\"persistedQuery\":{\"version\":1,\"sha256Hash\":\"469874edcad37b7a379d4f22f0083a49ea3d6ae097916120d9bbe3e36ca79e9d\"}}"
        },
        headers={
            "Host":"api-partner.spotify.com",
            "origin":"https://xpui.app.spotify.com",
            "user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.130 Spotify/1.2.37.701 Safari/537.36",
            "accept":"application/json",
            "accept-language":"en",
            "app-platform":"Linux",
            "authorization":f"Bearer {authToken}",
            "client-token":f"{clientToken}",
            "content-type":"application/json;charset=UTF-8",
            "sec-ch-ua":"\"Not(A:Brand \";v=\"24 \", \"Chromium \";v=\"122 \"",
            "sec-ch-ua-mobile":"?0",
            "sec-ch-ua-platform":"\"Linux \"",
            "spotify-app-version":"1.2.37.701",
            "sec-fetch-site":"same-site",
            "sec-fetch-mode":"cors",
            "sec-fetch-dest":"empty",
            "referer":"https://xpui.app.spotify.com/"
            },
        
        )

        return response.json()

    def transform_album_info(album_info):
        album_tracks = album_info["data"]["albumUnion"]["tracks"]["items"]
        tracks = []
        for track in album_tracks:
            track_name = track["track"]["name"]
            track_streams = track["track"]["playcount"]
            tracks.append({"trackName": track_name, "trackStreams": track_streams})
        # sort the tracks by number of streams
        tracks = sorted(tracks, key=lambda x: int(x["trackStreams"]), reverse=True)

        return tracks
    
    album_info = get_album_info(albumDetails['albumId'])
    tracks = transform_album_info(album_info)
    albumDetails["tracks"] = tracks

    return render_template('album.html', **albumDetails)


if __name__ == "__main__":
    app.run(debug=True)