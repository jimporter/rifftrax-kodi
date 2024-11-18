import unittest
from datetime import date

from resources.lib.rifftrax import RiffTrax


class TestRiffTrax(unittest.TestCase):
    def setUp(self):
        self.riff = RiffTrax()

    def test_search(self):
        data = self.riff.video_search('future force')
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0], {
            'nid': 3341526,
            'title': 'Future Force'
        })

    def test_info(self):
        data = self.riff.video_info(3341526)
        self.assertEqual(data['title'], 'Future Force')
        self.assertEqual(data['url'], 'https://www.rifftrax.com/future-force')
        self.assertEqual(data['feature_type'], 'feature')
        self.assertEqual(data['date'], date(2012, 7, 27))
        self.assertEqual(data['poster'],
                         'https://www.rifftrax.com/sites/default/files/' +
                         'images/posters/FutureForce_Web.jpg')
        self.assertEqual(data['rating'], 9.2)
        self.assertTrue('David Carradine' in data['summary'])
