from django.db import IntegrityError
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .monitors import Measurement
from .monitor_manager import MonitorManager
from .services import get_measurements

monitor_manager = MonitorManager()


class CreateMonitor(APIView):

    def post(self, request):
        measurement_id = request.data.get('measurement_id')
        type = request.data.get('type')
        monitor_manager.create_monitor(Measurement(measurement_id, type))
        return Response(f"Measurement {measurement_id} is being monitored", status=status.HTTP_200_OK)


class MonitorProcess(APIView):

    def post(self, request):
        asns = request.data.get('asns')
        for asn in asns:
            measurements = get_measurements(asn)
            for measurement in measurements:
                monitor_manager.create_monitor(measurement)
        return Response(f"Monitoring Process started for the following asns: {asns}", status=status.HTTP_201_CREATED)


class Feedback(APIView):

    def post(self, request):
        monitor_id = request.data.get('id')
        monitor_manager.monitors[monitor_id].restart()
        return Response("Feedback has been processed", status=status.HTTP_200_OK)


class Measurement(APIView):
    def get(self, request):
        return Response([measurement.measurement_id for measurement in get_measurements(208800)], status=status.HTTP_200_OK)

