import socket
import time
import calendar
from pattern.web import Twitter, plaintext
from pattern.nl import sentiment as sentiment_nl
from pattern.en import sentiment as sentiment_en
from pattern.fr import sentiment as sentiment_fr

CARBON_SERVER = '127.0.0.1'
CARBON_PORT = 2003
CARBON_METRIC = 'mp.events.twitter'


def datetime_to_ts(datestring):
    t = time.strptime(datestring, '%a %b %d %H:%M:%S +0000 %Y')
    return calendar.timegm(t)


def text_sentiment(tweet):
    polarity = 0
    subjectivity = 0
    if tweet.language in ("nl", "fr", "en"):
        s = plaintext(tweet.description)
        if tweet.language == "nl":
            (polarity, subjectivity) = sentiment_nl(s)
        if tweet.language == "en":
            (polarity, subjectivity) = sentiment_en(s)
        if tweet.language == "fr":
            (polarity, subjectivity) = sentiment_fr(s)
        if ':)' in s:
            polarity = 1
        if ':(' in s:
            polarity = -1
    return polarity*(1.0 - subjectivity)


def send_msg_to_graphite(metric, value, timestamp):
    message = '%s %s %d\n' % (metric, value, timestamp)
    sock = socket.socket()
    sock.connect(CARBON_SERVER, CARBON_PORT)
    sock.sendall(message)
    sock.close()

term = 'marktplaats'
start = None
count = 100
for tweet in Twitter().search(term, start=start, count=count):
    text = plaintext(tweet.description)
    if term in text: # skip non-relevant results
        weight = 1 + text_sentiment(tweet)
        print tweet.date, text, weight
        print datetime_to_ts(tweet.date), weight