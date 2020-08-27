from createPlaylist import CreatePlaylist
from secrets import Secrets
from playlistInfo import PlaylistInformation

def get_input(text):
    user_input = ""
    while user_input is "":
        user_input = input(text + ": ")
    return user_input

def get_spotify_secrets():
    return Secrets(get_input("Enter your Spotify user ID"), get_input("Enter your Spotify OAuth Token"))

def get_playlist_info():
    def get_privacy_setting():
        user_input = ""
        while user_input is "" or (user_input.lower() != "y" and user_input.lower() != "n"):
            user_input = input("Do you want your new Spotify playlist to be public? (Y/y or N/n): ")

        if user_input.lower() == "y":
            return True
        else:
            return False

    return PlaylistInformation(get_input("Enter your new Spotify playlist title"), get_input("Enter your new Spotify playlist description"), get_privacy_setting())

def main():
    new_playlist = CreatePlaylist(get_input("Enter the YouTube playlist ID"), get_spotify_secrets(), get_playlist_info())
    new_playlist.add_songs_to_playlist()

if __name__ == "__main__":
    main()