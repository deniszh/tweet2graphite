tweet2graphite
==============

Simple script which will search tweets for specific term, calculate words sentiment and put results to predefined graphite metric.

Tweet weight will be calculated as zero_weight +/- tweet sentiment.
Tweet sentiment is calculated as polarity*(1.0 - subjectivity).
Polarity and subjectivity calculated by magnificent Pattern module http://www.clips.ua.ac.be/pages/pattern for Dutch and English tweets (1 < polarity < -1, 0 < subjectivity < 1).
Last tweet timestamp will be put in last_ts_file (yep, I know, it will work only for small amount of tweets, maybe I'll create tweet stream version of this if needed).
Do not run this script too often - or Twitter will block you (150 req for 15 min MAX for now).

For config see config.ini
Put it in ~/.t2g/config.ini

```
zero_weight = 1
do_sentiments = True
search_term = marktplaats
results_count = 100
carbon_server = 127.0.0.1
carbon_port = 2003
carbon_metric = mp.events.twitter
last_ts_file = ~/.t2g/last_ts
```