import tempfile
import unittest
from contextlib import contextmanager

from resources.lib.riffdb import RiffDB


class TestRiffDB(unittest.TestCase):
    sample_riff = {
        'filename': 'riff.mp4', 'title': 'my riff', 'url': 'example.com',
        'feature_type': 'short', 'poster': 'example.com',
        'summary': 'a good riff', 'date': '2010-01-02', 'rating': 9.8,
    }

    @staticmethod
    @contextmanager
    def riffdb():
        with tempfile.NamedTemporaryFile() as f:
            yield RiffDB(f.name)

    def test_empty(self):
        with self.riffdb() as db:
            with self.assertRaises(LookupError):
                self.assertEqual(db.get('riff.mp4'))

    def test_empty_has(self):
        with self.riffdb() as db:
            self.assertFalse(db.has('riff.mp4'))

    def test_empty_iterate(self):
        with self.riffdb() as db:
            self.assertListEqual(list(db.iterate()), [])

    def test_empty_count(self):
        with self.riffdb() as db:
            self.assertEqual(db.count(), 0)

    def test_get(self):
        with self.riffdb() as db:
            db.insert(**self.sample_riff)
            self.assertDictEqual(db.get('riff.mp4'), self.sample_riff)

    def test_has(self):
        with self.riffdb() as db:
            db.insert(**self.sample_riff)
            self.assertTrue(db.has('riff.mp4'))

    def test_iterate(self):
        with self.riffdb() as db:
            db.insert(**self.sample_riff)
            self.assertListEqual(list(db.iterate()), [self.sample_riff])
            self.assertListEqual(list(db.iterate('feature')), [])

    def test_count(self):
        with self.riffdb() as db:
            db.insert(**self.sample_riff)
            self.assertEqual(db.count(), 1)
            self.assertEqual(db.count('feature'), 0)
