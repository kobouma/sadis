from rest_framework.response import Response
from rest_framework import status as drf_status

class ApiResponseMixin:
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({"success": True, "message": "Liste récupérée.", "data": response.data})
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({"success": True, "message": "Détail récupéré.", "data": response.data})
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({"success": True, "message": "Créé.", "data": response.data},
                        status=drf_status.HTTP_201_CREATED)
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({"success": True, "message": "Mis à jour.", "data": response.data})
    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"success": True, "message": "Supprimé."},
                        status=drf_status.HTTP_204_NO_CONTENT)