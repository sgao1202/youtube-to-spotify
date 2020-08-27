class PlaylistInformation():
    def __init__(self, title, description, is_public):
        self.playlist_title = title
        self.playlist_description = description
        self.playlist_is_public = is_public
    
    def get_title(self):
        return self.playlist_title

    def get_description(self):
        return self.playlist_description
    
    def get_publicy(self):
        return self.playlist_is_public