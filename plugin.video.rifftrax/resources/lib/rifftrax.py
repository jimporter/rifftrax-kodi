import re
import time
import urllib
import urllib2
from bs4 import BeautifulSoup

SEARCH_FORMAT = 'http://www.rifftrax.com/search/catalog/"{}"/type/video'

class RiffTrax(object):
    def video_search(self, query):
        url = SEARCH_FORMAT.format(urllib.quote_plus(query))
        soup = BeautifulSoup(urllib2.urlopen(url))
        try:
            results = (soup.find('ol', class_='search-results')
                           .find_all('span', class_='product-link'))
            return [{'title': i.a.get_text(), 'url': i.a['href']}
                    for i in results]
        except:
            return []

    def video_info(self, url):
        soup = BeautifulSoup(urllib2.urlopen(url))
        title = soup.find(id='page-title').get_text()

        feature_type = 'short'
        formats = (soup.find('div', class_='view-commerce-files-in-product')
                       .find('div', class_='view-content')
                       .find_all('div', class_='field-commerce-file'))

        for f in formats:
            if re.search('(Download to Burn|DVD Image)', f.get_text()):
                feature_type = 'feature'
                break
        if re.match(r'RiffTrax Live:', title):
            feature_type = 'live'

        summary = soup.find('div', class_='field-description').get_text()
        poster = soup.find('div', class_='field-poster').find('a')['href']
        rating = float(soup.find('span', id='riffmeter-average').get_text())
        date = self._parse_time(
            soup.find('span', class_='date-display-single').get_text()
        )

        return {
            'title': title, 'url': url, 'feature_type': feature_type,
            'poster': poster, 'summary': summary, 'date': date, 'rating': rating
        }

    def _parse_time(self, t):
        try:
            return time.strptime(t, '%A, %B %d, %Y')
        except:
            return time.strptime(t, '%B %d, %Y')
