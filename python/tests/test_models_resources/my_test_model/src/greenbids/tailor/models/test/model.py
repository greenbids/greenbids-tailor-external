from greenbids.tailor.core import fabric, models
from . import _version


class Model(models.Model):
    VERSION = _version.VERSION

    def get_buyers_probabilities(
        self,
        fabrics: list[fabric.Fabric],
    ) -> list[fabric.Fabric]:
        return fabrics

    def report_buyers_status(self, fabrics: list[fabric.Fabric]) -> list[fabric.Fabric]:
        return fabrics
