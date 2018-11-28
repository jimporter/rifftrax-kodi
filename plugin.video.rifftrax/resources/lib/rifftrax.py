import re
import time
import urllib
import urllib2
from bs4 import BeautifulSoup

class RiffTrax(object):
    base_url = 'https://www.rifftrax.com'
    search_format = base_url + '/search/catalog/"{}"/type/video'

    def video_search(self, query):
        url = self.search_format.format(urllib.quote_plus(query))
        soup = BeautifulSoup(urllib2.urlopen(url), 'html.parser')
        try:
            results = (soup.find('ol', class_='search-results')
                           .find_all('span', class_='product-link'))
            return [{'title': i.a.get_text(), 'url': i.a['href']}
                    for i in results]
        except:
            return []

    def video_info(self, url):
        if url[0] == '/':
            url = self.base_url + url
        soup = BeautifulSoup(urllib2.urlopen(url), 'html.parser')
        title = soup.find('h1', class_='page-header').get_text()

        feature_type = 'short'
        formats = (soup.find('div', class_='view-commerce-files-in-product')
                       .find('div', class_='view-content')
                       .find_all('div', class_='field-commerce-file'))

        for f in formats:
            if re.search('(Download to Burn|DVD Image|NTSC)', f.get_text()):
                feature_type = 'feature'
                break
        if re.match(r'RiffTrax Live:', title):
            feature_type = 'live'

        summary = soup.find('div', class_='field-description').get_text()
        poster_container = (
            soup.find('div', class_='pane-node-field-poster') or
            soup.find('div', class_='pane-commerce-product-field-poster')
        )
        poster = poster_container.find('a')['href']
        rating = float(soup.find('span', class_='average-rating').find('span')
                           .get_text())
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
