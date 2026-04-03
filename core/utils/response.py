from rest_framework.response import Response
from rest_framework import status

def success(data=None, message="Succès", status_code=status.HTTP_200_OK):
    return Response({"success": True, "message": message, "data": data}, status=status_code)

def created(data=None, message="Créé avec succès"):
    return Response({"success": True, "message": message, "data": data}, status=status.HTTP_201_CREATED)

def no_content(message="Supprimé"):
    return Response({"success": True, "message": message}, status=status.HTTP_204_NO_CONTENT)

def error(message="Erreur", status_code=status.HTTP_400_BAD_REQUEST, details=None):
    return Response({"success": False, "error": {"message": message, "details": details}},
                    status=status_code)
