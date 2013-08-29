import time
import calendar
import os
import sys
import ConfigParser
from socket import socket
from pattern.web import Twitter, plaintext
from pattern.nl import sentiment as sentiment_nl
from pattern.en import sentiment as sentiment_en

CONFIG_FILE = '~/.t2g/config.ini'

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
        if ':)' in s:
            polarity = 1
        if ':(' in s:
            polarity = -1
    return polarity*(1.0 - subjectivity)


def send_msg_to_graphite(CARBON_SERVER, CARBON_PORT, metric, value, timestamp):
    sock = socket()
    try:
        sock.connect((CARBON_SERVER, CARBON_PORT))
    except:
        print("Couldn't connect to Graphite, is carbon-relay running?")
        return
    message = '%s %s %d\n' % (metric, value, timestamp)
    try:
        sock.sendall(message)
        sock.close()
    except Exception as out:
        print("Updating graphite failed: %s" % out)
        return


if __name__ == "__main__":
    # read config
    search_term = None
    start = None
    results_count = 100
    CARBON_SERVER = '127.0.0.1'
    CARBON_PORT = 2003
    CARBON_METRIC = 'mp.events.twitter'
    weight = 1
    do_sentiments = True
    last_ts = 0

    try:
        config = ConfigParser.RawConfigParser()
        config.readfp(open(os.path.expanduser(CONFIG_FILE)))

        search_term = config.get("tweet2graphite", "search_term")
        CARBON_SERVER = config.get("tweet2graphite", "carbon_server")
        CARBON_PORT = config.get("tweet2graphite", "carbon_port")
        CARBON_METRIC = config.get("tweet2graphite", "carbon_metric")
        last_ts_file = config.get("tweet2graphite", "last_ts_file")
        results_count = config.get("tweet2graphite", "results_count")
        zero_weight = config.get("tweet2graphite", "zero_weight")
        do_sentiments = config.get("tweet2graphite", "do_sentiments")
    except IOError, e:
        print "Config %s not found" % CONFIG_FILE
        sys.exit(1)

    # read last start position from file
    try:
        last_ts_file = os.path.expanduser(last_ts_file)
        with open(last_ts_file, "r") as myfile:
            last_ts = int(myfile.read().replace('\n', ''))
        myfile.close()
    except IOError, e:
        pass
    #print "Last TS=", last_ts

    print search_term, start, results_count
    max_ts = last_ts
    for tweet in Twitter().search(search_term, start=start, count=results_count):
        text = plaintext(tweet.description)
        ts = datetime_to_ts(tweet.date)
        print ts, text
        if ts >= last_ts:  # skip old results
            weight = float(zero_weight)
            if do_sentiments:
                weight = weight + text_sentiment(tweet)

            #print tweet.date, text, weight
            #print ts, weight
            send_msg_to_graphite(CARBON_SERVER, CARBON_PORT, CARBON_METRIC, weight, ts)
            if ts > max_ts:
                max_ts = ts

    # save last_ts to file
    try:
        with open(last_ts_file, "w+") as myfile:
            print >> myfile, max_ts
        myfile.close()
    except IOError, e:
        print "Can't save last_ts to file %s" % last_ts_file
        sys.exit(1)