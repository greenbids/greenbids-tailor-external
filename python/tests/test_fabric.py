import unittest

from greenbids.tailor.core import fabric


class TestFabrics(unittest.TestCase):

    def test_should_report_if_all_inputs_are_training(self):
        trainable = fabric.Fabric(
            prediction=fabric.Prediction(exploration_rate=1, training_rate=1)
        )
        non_trainable = fabric.Fabric(
            prediction=fabric.Prediction(exploration_rate=0, training_rate=0)
        )

        with self.subTest("Empty should not be reported: [] => False"):
            self.assertFalse(fabric.should_report([]))
        with self.subTest("Any non-training should not be reported: [T, F] => False"):
            self.assertFalse(fabric.should_report([trainable, non_trainable]))
        with self.subTest("All training should be reported: [T, T] => T"):
            self.assertTrue(fabric.should_report([trainable, trainable]))
