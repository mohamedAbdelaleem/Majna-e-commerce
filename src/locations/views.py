from rest_framework.views import APIView
from rest_framework.response import Response
from stores.models import Governorate
from .serializers import GovernorateSerializer


class GovernorateListView(APIView):

    def get(self, request):
        governorates = Governorate.objects.prefetch_related("cities")
        serializer = GovernorateSerializer(governorates, many=True)
        data = {"governorates": serializer.data}
        return Response(data)