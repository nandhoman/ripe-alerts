from typing import Type

from anomaly_detection_reworked.detection_method import DetectionMethod


class AnomalyDetection:

    def __init__(self) -> None:
        pass

    def add_detection_method(self, method: Type[DetectionMethod]) -> None:
        # add to methods list
        # check if correctly implemented
        pass

    def start(self):
        pass

    def stop(self):
        pass

