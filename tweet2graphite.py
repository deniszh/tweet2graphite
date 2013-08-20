from twython import Twython
from twython import TwythonStreamer

APP_KEY = '15861352-DKZ6c4CD7CzwbtiSD4xXQJ0d6UccVWXxoKFLbmQ9l'
APP_SECRET = ''
OAUTH_TOKEN = '15861352-DKZ6c4CD7CzwbtiSD4xXQJ0d6UccVWXxoKFLbmQ9l'
OAUTH_TOKEN_SECRET = ''

class MyStreamer(TwythonStreamer):
    def on_success(self, data):
        if 'text' in data:
            print data['text'].encode('utf-8')

    def on_error(self, status_code, data):
        print status_code
        self.disconnect()

stream = MyStreamer(APP_KEY, APP_SECRET,
                    OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

stream.statuses.filter(track='marktplaats marktplaats.nl')
