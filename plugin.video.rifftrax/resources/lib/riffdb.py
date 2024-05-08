import sqlite3


class RiffDB:
    keys = ['filename', 'title', 'url', 'feature_type', 'poster', 'summary',
            'date', 'rating']

    def __init__(self, path):
        self._conn = sqlite3.connect(path)
        self._cursor = self._conn.cursor()
        self._cursor.execute(
            'CREATE TABLE IF NOT EXISTS riffs (filename text PRIMARY KEY, ' +
            'title text, url text, feature_type text, poster text, ' +
            'summary text, date text, rating real)'
        )

    def get(self, filename):
        self._cursor.execute(
            'SELECT * FROM riffs WHERE filename=?', (filename,)
        )
        return dict(zip(RiffDB.keys, self._cursor.fetchone()))

    def has(self, filename):
        self._cursor.execute(
            'SELECT filename FROM riffs WHERE filename=?', (filename,)
        )
        return self._cursor.fetchone() is not None

    def iterate(self, feature_type=None):
        if feature_type:
            self._cursor.execute(
                'SELECT * FROM riffs WHERE feature_type=?', (feature_type,)
            )
        else:
            self._cursor.execute('SELECT * FROM riffs')

        while True:
            row = self._cursor.fetchone()
            if row is None:
                return
            yield dict(zip(RiffDB.keys, row))

    def count(self, feature_type=None):
        if feature_type:
            self._cursor.execute(
                'SELECT COUNT(*) FROM riffs WHERE feature_type=?',
                (feature_type,)
            )
        else:
            self._cursor.execute('SELECT COUNT(*) FROM riffs')
        return self._cursor.fetchone()[0]

    def insert(self, filename, **info):
        self._cursor.execute(
            'INSERT INTO riffs VALUES (?,?,?,?,?,?,?,?)',
            (filename, info.get('title'), info.get('url'),
             info.get('feature_type'), info.get('poster'), info.get('summary'),
             info.get('date'), info.get('rating'))
        )
        self._conn.commit()

    def remove(self, filename):
        self._cursor.execute(
            'DELETE FROM riffs WHERE filename=?', (filename,)
        )
        self._conn.commit()

    def clear(self):
        self._cursor.execute('DROP TABLE riffs')
        self._conn.commit()
