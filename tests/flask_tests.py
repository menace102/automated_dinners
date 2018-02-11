import os
import unittest
import tempfile
import automated_dinners

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, automated_dinners.app.config['DATABASE'] = tempfile.mkstemp()
        automated_dinners.app.testing = True
        self.app = automated_dinners.app.test_client()
        with automated_dinners.app.app_context():
            automated_dinners.run_app.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(automated_dinners.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data

if __name__ == '__main__':
    unittest.main()