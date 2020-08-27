
class Secrets():
    def __init__(self, spotify_user_id, spotify_token):
        self.__spotify_user_id = spotify_user_id
        self.__spotify_token = spotify_token

    def get_user_id(self):
        return self.__spotify_user_id
    
    def get_token(self):
        return self.__spotify_token