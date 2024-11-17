import re
import time
from bs4 import BeautifulSoup
from urllib.parse import quote_plus as url_quote_plus
from urllib.request import urlopen


class RiffTrax:
    base_url = 'https://www.rifftrax.com'
    search_format = base_url + '/catalog/media-type/video?search="{}"'

    def video_search(self, query):
        url = self.search_format.format(url_quote_plus(query))
        soup = BeautifulSoup(urlopen(url), 'html.parser')
        try:
            results = (soup.find('section', id='block-system-main')
                           .find('div', class_='view-content')
                           .find_all('div', class_='product-grid'))
            return [{'title': i.get_text().strip(),
                     'url': self.base_url + i.a['href']}
                    for i in results]
        except Exception:
            return []

    def video_info(self, url):
        if url[0] == '/':
            url = self.base_url + url
        soup = BeautifulSoup(urlopen(url), 'html.parser')
        title = soup.find(id='page-title').get_text()

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
            'poster': poster, 'summary': summary, 'date': date,
            'rating': rating,
        }

    def _parse_time(self, t):
        try:
            return time.strptime(t, '%A, %B %d, %Y')
        except Exception:
            return time.strptime(t, '%B %d, %Y')
