import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.request import urlopen


class RiffTrax:
    base_url = 'https://www.rifftrax.com/api/dante/'

    def video_search(self, query):
        tokens = [re.compile(i, flags=re.IGNORECASE)
                  for i in re.split(r'\W+', query)]

        results = []
        for i in self._title_list():
            if all(t.search(i['title']) for t in tokens):
                results.append(i)
        return results

    def video_info(self, nid):
        api_url = self.base_url + 'product_display/{}'.format(nid)
        data = json.load(urlopen(api_url))

        title = data['title']
        url = data['path']
        date = datetime.fromisoformat(data['released']).date()

        source_type = data['source']['type']['tid']
        if re.match(r'RiffTrax Live:', title):
            feature_type = 'live'
        elif source_type == 261:
            feature_type = 'feature'
        elif source_type == 266:
            feature_type = 'short'
        else:
            raise ValueError('unrecognized type: {}'
                             .format(data['source']['type']))

        soup = BeautifulSoup(urlopen(url), 'html.parser')
        summary = soup.find('div', class_='field-description').get_text()
        rating = float(soup.find('span', class_='average-rating').find('span')
                           .get_text())

        poster_container = (
            soup.find('div', class_='pane-node-field-poster') or
            soup.find('div', class_='pane-commerce-product-field-poster')
        )
        poster = poster_container.find('a')['href']

        return {
            'title': title, 'url': url, 'feature_type': feature_type,
            'poster': poster, 'summary': summary, 'date': date,
            'rating': rating,
        }

    def _title_list(self):
        if not hasattr(self, '_title_list_cache'):
            url = self.base_url + 'product_search'
            self._title_list = json.load(urlopen(url))['index']
        return self._title_list
