import time
import unittest

from resources.lib.rifftrax import RiffTrax


class TestScraping(unittest.TestCase):
    def setUp(self):
        self.riff = RiffTrax()

    def test_search(self):
        data = self.riff.video_search('future force')
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0], {
            'url': 'https://www.rifftrax.com/future-force',
            'title': u'Future Force'
        })

    def test_info(self):
        data = self.riff.video_info('https://www.rifftrax.com/future-force')
        self.assertEqual(data['title'], 'Future Force')
        self.assertEqual(data['url'], 'https://www.rifftrax.com/future-force')
        self.assertEqual(data['feature_type'], 'feature')
        self.assertEqual(data['date'], time.strptime('2012-7-27', '%Y-%m-%d'))
        self.assertEqual(data['poster'],
                         'https://www.rifftrax.com/sites/default/files/' +
                         'images/posters/FutureForce_Web.jpg')
        self.assertEqual(data['rating'], 9.2)
        self.assertTrue('David Carradine' in data['summary'])
