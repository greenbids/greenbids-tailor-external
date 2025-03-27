import datetime
import tempfile
import time
import unittest
import unittest.mock

from greenbids.tailor.core.app import resources
from greenbids.tailor.core.settings import settings


class TestResources(unittest.TestCase):

    def test_should_return_in_memory_dump(self):
        res = resources.AppResources()
        res._gb_model = unittest.mock.Mock(dump=lambda fp: fp.write(b"foo"))
        buf = res._get_model_dump()
        self.assertIsNotNone(buf)
        assert buf is not None
        self.assertEqual(buf.getvalue(), b"foo")

    def test_should_return_latest_file_dump(self):
        res = resources.AppResources()
        res._gb_model = unittest.mock.Mock(dump=lambda fp: fp.write(b"first"))
        with tempfile.TemporaryDirectory() as tmpdir:
            settings.data_directory = tmpdir
            first_file = res.save_model()
            self.assertTrue(
                str(first_file).startswith(tmpdir),
                "Model not saved in the data directory",
            )
            time.sleep(1)

            res._gb_model = unittest.mock.Mock(dump=lambda fp: fp.write(b"latest"))
            latest_file = res.save_model()
            self.assertGreater(str(latest_file), str(first_file))

            res._gb_model = None
            buf = res._get_model_dump()
            self.assertIsNotNone(buf)
            assert buf is not None
            self.assertEqual(buf.getvalue(), b"latest")

    def test_should_refresh_none_model(self):
        with unittest.mock.patch(f"{resources.__name__}.models") as models_mock:
            resources.AppResources().refresh_model()
            models_mock.load.assert_called_once()

    def test_should_not_refresh_loaded_model(self):
        with unittest.mock.patch(f"{resources.__name__}.models") as models_mock:
            res = resources.AppResources()
            res._gb_model = unittest.mock.Mock()

            res.refresh_model()
            models_mock.load.assert_not_called()

    def test_should_refresh_once_from_command(self):
        with unittest.mock.patch(f"{resources.__name__}.models") as models_mock:
            res = resources.AppResources()
            res._gb_model = unittest.mock.Mock()

            res.refresh_model()
            models_mock.load.assert_not_called()

            with unittest.mock.patch(f"{resources.__name__}.requests") as rqsts_mock:
                rqsts_mock.get().json.return_value = {
                    "ts": datetime.datetime.now(datetime.timezone.utc).isoformat()
                }

                res.refresh_model()
                models_mock.load.assert_called_once()
                models_mock.load.reset_mock()

                res.refresh_model()
                models_mock.load.assert_not_called()
