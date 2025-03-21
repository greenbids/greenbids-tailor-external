import subprocess
import unittest
import unittest.mock
import os

from greenbids.tailor.core import models


class TestModelLoad(unittest.TestCase):

    def setUp(self):
        self.module_path = __file__.replace(".py", "_resources/my_test_model")
        self._install()

    def tearDown(self):
        self._uninstall()

    def _install(self):
        print(subprocess.check_output(["pip", "install", self.module_path]).decode())

    def _uninstall(self):
        print(
            subprocess.check_output(
                ["pip", "uninstall", "--yes", "greenbids-tailor-models-test"]
            ).decode()
        )

    def test_should_invalidate_import_cache(self):
        with unittest.mock.patch(f"{models.__name__}._download"):
            m = models.load("test")
            self.assertEqual(m.VERSION, "0.1.0", "First install failure")

            pyproject = f"{self.module_path}/pyproject.toml"
            os.rename(pyproject, f"{pyproject}~")
            try:
                with open(f"{pyproject}~", "r") as src:
                    with open(pyproject, "w") as dst:
                        for line in src:
                            if line == 'version = "0.1.0"\n':
                                dst.write('version = "0.2.0"\n')
                            else:
                                dst.write(line)

                self._install()
                m = models.load("test")
                self.assertEqual(m.VERSION, "0.2.0", "Updated version not loaded")
            finally:
                os.rename(f"{pyproject}~", pyproject)
