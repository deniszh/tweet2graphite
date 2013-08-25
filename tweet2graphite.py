import socket
from pattern.web import Twitter, plaintext
from pattern.nl  import sentiment as sentiment_nl
from pattern.en  import sentiment as sentiment_en
from pattern.fr  import sentiment as sentiment_fr

CARBON_SERVER = '127.0.0.1'
CARBON_PORT = 2003

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
    return polarity*(1.0 - subjectivity)

def send_msg_to_graphite(metric, value, timestamp):
    message = '%s %s %d\n' % (metric, value, timestamp)
    sock = socket.socket()
    sock.connect(CARBON_SERVER, CARBON_PORT)
    sock.sendall(message)
    sock.close()

term = 'marktplaats'
for tweet in Twitter().search(term):
    text = plaintext(tweet.description)
    if term in text: # skip non-relevant results
        weight = 1 + text_sentiment(tweet)
        print tweet.date, text, weight