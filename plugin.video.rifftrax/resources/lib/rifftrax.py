import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.request import urlopen


class RiffTrax:
    base_url = 'https://www.rifftrax.com/api/dante/'

    def _request_json(self, path):
        return json.load(urlopen(self.base_url + path))

    def video_search(self, query):
        tokens = [re.compile(i, flags=re.IGNORECASE)
                  for i in re.split(r'\W+', query)]

        results = []
        for i in self._title_list():
            if all(t.search(i['title']) for t in tokens):
                results.append(i)
        return results

    def video_info(self, nid):
        product_data = self._request_json('product_display/{}'.format(nid))
        title = product_data['title']
        date = datetime.fromisoformat(product_data['released']).date()

        source_type = product_data['source']['type']['tid']
        if re.match(r'RiffTrax Live:', title):
            feature_type = 'live'
        elif source_type == 261:
            feature_type = 'feature'
        elif source_type == 266:
            feature_type = 'short'
        else:
            raise ValueError('unrecognized type: {}'
                             .format(product_data['source']['type']))

        vote_data = self._request_json('voting/{}'.format(nid))
        rating = vote_data['average'] / 10

        web_url = product_data['path']
        soup = BeautifulSoup(urlopen(web_url), 'html.parser')
        summary = soup.find('div', class_='field-description').get_text()

        poster_container = (
            soup.find('div', class_='pane-node-field-poster') or
            soup.find('div', class_='pane-commerce-product-field-poster')
        )
        poster = poster_container.find('a')['href']

        return {
            'title': title, 'url': web_url, 'feature_type': feature_type,
            'poster': poster, 'summary': summary, 'date': date,
            'rating': rating,
        }

    def _title_list(self):
        if not hasattr(self, '_title_list_cache'):
            url = self.base_url + 'product_search'
            self._title_list = json.load(urlopen(url))['index']
        return self._title_list
