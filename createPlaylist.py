import json
import os
import sys

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

import requests
import youtube_dl

from secrets import Secrets
from playlistInfo import PlaylistInformation

'''
    1) Log onto YouTube
    2) Grab "Music" playlist
    3) Create a new playlist on Spotify
    4) Search for a song
    5) Add the song into the new Spotify playlist
'''

class CreatePlaylist:
    def __init__(self, old_playlist_id, spotify_secrets, playlist_info):
        self.youtube_client = self.__get_youtube_client()
        self.youtube_playlist_id = old_playlist_id

        # Spotify login information
        self.secrets = spotify_secrets

        # New Spotify playlist information
        self.playlist_information = playlist_info
        self.song_titles = []
        self.unsearchable_songs = []


    def __get_youtube_client(self):
        '''
            Log into YouTube and return the client
        '''
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secret.json"

        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()

        youtube_client = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)
        return youtube_client

    def __get_music_playlist(self):
        ''' 
            Grab the "Music" playlist and create a list containing song titles
        '''
        def remove_paren(title):
            curved = "("
            bracket = "["
            opening = None
            closing = None

            if curved not in title and bracket not in title:
                return title
            elif curved in title:
                opening = "("
                closing = ")"
            elif bracket in title:
                opening = "["
                closing = "]"

            opening_ind = title.find(opening)
            closing_ind = title.find(closing)
            new_title = title[:opening_ind] + title[closing_ind + 1:]
            return remove_paren(new_title.strip())
        
        # Max number of results per page is 50. Use the nextPageToken property to get the next set of 50 results.
        request = self.youtube_client.playlistItems().list(
            part="snippet,contentDetails",
            maxResults=50,
            #playlistId="PL8-_Vsx34R12975mckpwienGds1ytI7kI"
            playlistId=self.youtube_playlist_id
        )
        response = request.execute()
        
        last_page = False
        token_key = "nextPageToken"
        while not last_page:
            for item in response["items"]:
                video_title = item["snippet"]["title"]
                self.song_titles.append(remove_paren(video_title))
            if token_key not in response:
                last_page = True
            else:
                # Change the response to the next page
                request = self.youtube_client.playlistItems().list(
                    part="snippet,contentDetails",
                    maxResults=50,
                    pageToken = response["nextPageToken"],
                    #playlistId="PL8-_Vsx34R12975mckpwienGds1ytI7kI"
                    playlistID=self.youtube_playlist_id
                )
                response = request.execute()
        
    def __create_playlist(self):
        '''
            Create a new and empty playlist on Spotify
        '''
        body = {
            "name": self.playlist_information.get_title(),
            "description": self.playlist_information.get_description(),
            "public": self.playlist_information.get_publicy()
        }

        request_body = json.dumps(body) 
    
        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.secrets.get_user_id())
        response = requests.post(query, data=request_body, headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.secrets.get_token())
            })
        response_json = response.json()
        #json_string = json.dumps(response_json, indent=2, sort_keys=True)

        if response.ok:
            print("Successfully created new playlist called '{}'.".format(body["name"]))
            return response_json["id"]
        else:
            print("Failed to create new playlist called '{}'".format(body["name"]))

    def __get_spotify_uri(self, title):
        '''
        Search for a song using the title of a video and return the Spotify URI corresponding to that track.
        '''
        query = "https://api.spotify.com/v1/search?q={}&type=track&market=US&limit=1".format(title)

        response = requests.get(query, headers={
            "Content-type": "application/json",
            "Authorization": "Bearer {}".format(self.secrets.get_token())
        })
        response_json = response.json()
        if "error" in response_json or "tracks" not in response_json or response_json["tracks"]["items"] == []:
            print("Error searching for {} on Spotify".format(title))
            self.unsearchable_songs.append(title)
        else:            
            return response_json["tracks"]["items"][0]["uri"]

     
    def add_songs_to_playlist(self):
        '''
        Create new Spotify playlists and add songs to the playlist.
        '''
        self.__get_music_playlist()
        spotify_playlist_id = self.__create_playlist()
        def add_song(uri):
            query = "https://api.spotify.com/v1/playlists/{}/tracks?uris={}".format(spotify_playlist_id, uri)
            response = requests.post(query, headers={
                "Content-type": "application/json",
                "Authorization": "Bearer {}".format(self.secrets.get_token())
            })

        for title in self.song_titles:
            current_uri = self.__get_spotify_uri(title)
            add_song(current_uri)

# if __name__ == "__main__":
#     new_playlist = CreatePlaylist()
#     new_playlist.add_songs_to_playlist()
#     print(new_playlist.unsearchable_songs)