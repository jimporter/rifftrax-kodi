import re
import time
import urllib
import urllib2
from bs4 import BeautifulSoup

SEARCH_FORMAT = 'http://www.rifftrax.com/search/catalog/"{}"/type/video'

class RiffTrax(object):
    def video_search(self, query):
        url = SEARCH_FORMAT.format(urllib.quote(query, ''))
        soup = BeautifulSoup(urllib2.urlopen(url))
        results = (soup.find('ol', class_='search-results')
                       .find_all('span', class_='product-link'))
        return [{'title': i.a.get_text(), 'url': i.a['href']}
                for i in results]

    def video_info(self, url):
        soup = BeautifulSoup(urllib2.urlopen(url))
        title = soup.find(id='page-title').get_text()

        feature_type = 'short'
        formats = (soup.find('div', class_='view-content')
                       .find_all('div', class_='field-commerce-file'))
        for f in formats:
            if re.search('(Download to Burn|Burnable DVD Image)', f.get_text()):
                feature_type = 'feature'
                break

        summary = soup.find('div', class_='field-description').get_text()
        poster = soup.find('div', class_='field-poster').find('a')['href']
        rating = float(soup.find('span', id='riffmeter-average').get_text())
        date = time.strptime(
            soup.find('span', class_='date-display-single').get_text(),
            '%A, %B %d, %Y'
        )

        return {
            'title': title, 'url': url, 'feature_type': feature_type,
            'poster': poster, 'summary': summary, 'date': date, 'rating': rating
        }
