# https://docs.python.org/3/howto/urllib2.html


import urllib.request, json
from html.parser import HTMLParser
from pprint import pprint

class MyHTMLParser( HTMLParser ):
    def __init__(self):
        super().__init__()
        self.data = []
        self.current_data = {}
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag

    def handle_data(self, data):
        if self.current_tag == 'td':
            self.current_data[len(self.current_data)] = data

    def handle_endtag(self, tag):
        if tag == 'tr':
            self.data.append(self.current_data)
            self.current_data = {}
        self.current_tag = None

_TARGET_URL = "https://sundowner.colorado.edu/weather/atoc1/"
trgtHTML    = None
htmlPrsr    = MyHTMLParser()

with urllib.request.urlopen( _TARGET_URL ) as response:
    trgtHTML = response.read().decode().replace('\n','')
    htmlPrsr.feed( trgtHTML )
    trgtDict = json.loads( json.dumps( htmlPrsr.data ) )
    pprint( trgtDict )
    # for k in trgtDict.keys():
    #     print( k )
    # trgtDict = htmlPrsr.
    # trgtHTML = [elem.decode().strip().replace('\n','') for elem in response.readlines()]
    # trgtHTML = [line for line in trgtHTML if len( line )]
    # for line in trgtHTML:
    #     print( line )