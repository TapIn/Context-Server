#!/usr/bin/env python

import web
import json
import requests
import datetime
import time
import random
import re
import operator

google_api_keys = [
    'AIzaSyBkKwgjae-ZilFhVqd653gxW-uX9CVd-TA'
]

foursquare_api_keys = [
    {
        'client_id': 'VWXOENXUE1BFYLEHNLYUQ0OUINOY4KNEMHFYN34UTWW2MCEB',
        'client_secret': 'WLJUSUKWIB1ZC5IIN3G410Q1M4NSPKC5IGXMQE5U3DCXIDYM'
    }
]

urls = (
  '/status', 'Status',
  '/', 'Event'
)

class Location:
    def __init__(self, lat, lon, time):
        self.lat = lat
        self.lon = lon
        self.time = time
        self.content = dict({
                                'hashtags': dict(),
                                2: dict(),
                                3: dict()
                           })
        self.ngram_acceptable = re.compile(r'[^\d\w.]+')

    # Gets the "name" - the top result and a series of guesses
    def get_name(self):
        if (self.get_locale() == 'city'):

            foursquare = self.get_foursquare_info()

            result = []

            # Get the neighborhood name
            if ('headerLocation' in foursquare):
                result.append('in ' + foursquare['headerLocation'])

            # Get the n-gram guesses from Twitter
            for guess in self.get_best_guesses():
                result.append(guess)

            # Get three groups from Foursquare
            if (len(foursquare['groups']) > 0):
                for item in foursquare['groups'][0]['items'][0:min(3, len(foursquare['groups'][0]['items']))]:
                    result.append('from ' + item['venue']['name'])

            if (len(result) > 0):
                return {'name': result[0], 'guesses': result}
            else:
                return {'name': self.get_current_date()}
        else:
            return {'name': self.get_current_date()}

    # Returns the current date as a human-readable string
    def get_current_date(self):
        dt = datetime.datetime.fromtimestamp(float(self.time))
        return dt.strftime('from %h %d at %I%p').replace(' 0', ' ')

    # Returns the best guesses from the available n-grams
    def get_best_guesses(self):
        self.calculate_ngrams_from_tweets()

        sorted_ngrams = sorted(dict(self.content[2].items() + self.content[3].items()).iteritems(), key=operator.itemgetter(1), reverse=True)
        ret = []
        for ngram in sorted_ngrams[0:3]:
            if (ngram[1] > 8):
                ret.append('about ' + ngram[0].title())
        return ret


    # Gets info from foursquare, including venues and city area
    def get_foursquare_info(self):

        key = random.choice(foursquare_api_keys);

        payload = {
            'client_id': key['client_id'],
            'client_secret': key['client_secret'],
            'v': '20120917',
            'll': self.lat + ',' + self.lon
        }

        result_html = requests.get('https://api.foursquare.com/v2/venues/explore', params=payload).text

        result = json.loads(result_html)['response']

        return result


    # Calculates the n-grams from all tweets
    def calculate_ngrams_from_tweets(self):
        for tweet in self.get_tweets_from_location()['results']:
            created_at = datetime.datetime.strptime(tweet['created_at'], '%a, %d %b %Y %H:%M:%S +0000')
            if ((datetime.datetime.fromtimestamp(float(self.time)) - created_at).total_seconds() > (60*60*5)):
                continue
            self.calculate_ngrams_from_tweet(tweet['text'])

    # Calculates the n-grams from a specific tweet
    def calculate_ngrams_from_tweet(self, tweet):
        for sentence in tweet.split('.'):
            self.calculate_ngrams_from_str(sentence)

    # Calculates the 2- and 3-grams of proper nouns from a string
    def calculate_ngrams_from_str(self, str):

        lastLastWord = ''
        lastWord = ''
        for word in str.split(' '):

            if (word == '' or word.upper() == 'RT' or word[0] == '@' or word.title() != word or len(word) < 2):
                lastWord = ''
                lastLastWord = ''
                continue

            san_word = self.ngram_acceptable.sub('', word).lower()
            twoGram = lastWord + ' ' + san_word;
            threeGram = lastLastWord + ' ' + lastWord + ' ' + san_word

            if (word == 'and' or word == 'the' or word == 'we' or word == 'on' or word == 'their' or word == 'than'):
                continue

            if (lastWord != ''):

                if (twoGram in self.content[2]):
                    self.content[2][twoGram] = self.content[2][twoGram] + 1
                else:
                    self.content[2][twoGram] = 1

                if (lastLastWord != ''):
                    if (threeGram in self.content[3]):
                        self.content[3][threeGram] = self.content[3][threeGram] + 1
                    else:
                        self.content[3][threeGram] = 1

            lastLastWord = lastWord
            lastWord = san_word


    # Gets nearby tweets from Twitter
    def get_tweets_from_location(self):
        dt = datetime.datetime.fromtimestamp(float(self.time)) + datetime.timedelta(24)
        payload = {
        'result_type': 'recent',
        'rpp': '100',
        'until': dt.strftime('%Y-%m-%d'),
        'include_entities': 'true',
        'geocode': self.lat + ',' + self.lon + ',' + '1mi'
        }

        result_html = requests.get('http://search.twitter.com/search.json', params=payload).text

        result = json.loads(result_html)

        return result

    # Gets the locale of the request by doing a Google Local query and checking the number of nearby places.
    # Returns either 'residential' (don't give too many details) or 'city'
    def get_locale(self):
        payload = {
            'key': random.choice(google_api_keys),
            'sensor': 'false',
            'location': self.lat + ',' + self.lon,
            'radius': '500'
        }
        result_html = requests.get('https://maps.googleapis.com/maps/api/place/search/json', params=payload).text

        result = json.loads(result_html)

        if (len(result['results']) < 20):
            return 'residential'
        else:
            return 'city'

class Event:
        def GET(self):
            input = web.input()
            loc = Location(input.lat, input.lon, input.time)
            return json.dumps(loc.get_name())

class Status:
        def GET(self):
             return "cats"

if __name__ == "__main__":
    app = web.application(urls, globals())
    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    app.run()
