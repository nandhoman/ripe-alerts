from typing import List

from ripe.atlas.cousteau import AtlasStream

from anomaly_detection_reworked.detection_method import DetectionMethod
from anomaly_detection_reworked.event_logger import EventLogger
from anomaly_detection_reworked.measurement_type import MeasurementType


class MeasurementResultStream:

    def __init__(self, measurement_ids: List[int], detection_methods: DetectionMethod):
        self.measurement_id_to_measurement_type: dict[int, MeasurementType] = {}  # Int represents a Measurement ID.
        self.measurement_type_to_detection_method: dict[MeasurementType, List[DetectionMethod]] = {}

        if len(measurement_ids) == 0:
            raise ValueError("At least one measurement ID is required to start up the Streaming API.")
        self.stream = AtlasStream()
        self.logger = EventLogger()
        self.detection_methods = detection_methods

        self.stream.connect()
        # Bind functions we want to run with every result message received
        self.stream.socketIO.on("connect", self.logger.on_connect)
        self.stream.socketIO.on("disconnect", self.logger.on_disconnect)
        self.stream.socketIO.on("reconnect", self.logger.on_reconnect)
        self.stream.socketIO.on("error", self.logger.on_error)
        self.stream.socketIO.on("close", self.logger.on_close)
        self.stream.socketIO.on("connect_error", self.logger.on_connect_error)
        self.stream.socketIO.on("atlas_error", self.logger.on_atlas_error)
        self.stream.socketIO.on("atlas_unsubscribed", self.logger.on_atlas_unsubscribe)
        self.stream.bind_channel("atlas_result", self.on_result_response)

        try:
            # Start the stream, and add one measurement ID (we can't start with multiple IDs)
            stream_parameters = {"msm": measurement_ids[0]}
            self.stream.start_stream(stream_type="result", **stream_parameters)
            for measurement_id in measurement_ids[1:]:  # Subscribe to stream with other IDs, and skip the first one.
                stream_parameters = {"msm": measurement_id}
                self.stream.subscribe(stream_type="result", **stream_parameters)

            self.stream.timeout(seconds=None)  # Run forever
        except KeyboardInterrupt:
            self.logger.on_disconnect(None)

    def on_result_response(self, *args):
        """
        Method that will be called every time we receive a new result.
        Args is a tuple, so you should use args[0] to access the real message.
        """
        result = args[0]
        print(len(args))
        msm_id = result['msm_id']
        detection_methods = self.get_corresponding_detection_methods(msm_id)
        for method in detection_methods:
            method.on_result_response(result)

    def get_corresponding_detection_methods(self, measurement_id: int) -> List[DetectionMethod]:
        """
        Method that will retrieve the corresponding Detection Methods based of the Measurement ID.
        Each Measurement ID has a Measurement Type.
        Each Detection Method has a Measurement Type. By using a dictionary I am able to solve this.
        Measurement ID <-> MeasurementType <-> Detection Method.
        """
        measurement_type: MeasurementType = self.measurement_id_to_measurement_type[measurement_id]
        methods: List[DetectionMethod] = self.measurement_type_to_detection_method[measurement_type]
        return methods

    # def get_detection_methods_containing_msm_type(self, measurement_type: MeasurementType) -> List[DetectionMethod]:
    #     pass
        # for method in detection_methods:
        #     if method
