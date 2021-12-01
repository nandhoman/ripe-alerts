from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import AlertConfiguration, Anomaly
from .serializers import AnomalySerializer
from django.core.exceptions import ObjectDoesNotExist



class AlertConfigurationList(APIView):
    """List of alert configurations"""

    def get(self, request):
        """ get all AlertConfigurations belonging to user"""
        user = request.user
        try:
            print(user.ripe_api_token.ripe_api_token)
        except ObjectDoesNotExist:
            print("has no ripe token")

        return AlertConfiguration.objects.all()

    def post(self, request):
        """ Add new alert configurations"""

        return Response(data=None, status=status.HTTP_201_CREATED)


class AlertList(APIView):
    def get(self, request):
        all_anomalies = int(request.query_params.get('all_anomalies', 1))
        if all_anomalies == 1:
            anomalies = Anomaly.objects.raw(
                """SELECT anomaly_id, is_alert, description, feedback 
                    FROM alert_configuration_anomaly as a
                    JOIN alert_configuration_alertconfiguration as b ON b.alert_configuration_id = a.alert_configuration_id
                    WHERE b.user_id = %s
                """, [request.user.id])
        else:
            anomalies = Anomaly.objects.raw(
                """SELECT anomaly_id, is_alert, description, feedback 
                    FROM alert_configuration_anomaly as a
                    JOIN alert_configuration_alertconfiguration as b ON b.alert_configuration_id = a.alert_configuration_id
                    WHERE b.user_id = %s AND a.is_alert = true
                """, [request.user.id])

        anomalies_serialized = AnomalySerializer(anomalies, many=True)
        return Response(anomalies_serialized.data, status=status.HTTP_200_OK)

