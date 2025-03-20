import datetime
import unittest
import unittest.mock

from greenbids.tailor.core.app import resources


class TestResources(unittest.TestCase):

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
