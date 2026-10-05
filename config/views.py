from django.db import DatabaseError, connection
from django.http import JsonResponse


def health(request):
    """Liveness + database check, used by Docker and the host's health probe."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except DatabaseError:
        return JsonResponse({"status": "error", "database": "unreachable"}, status=503)
    return JsonResponse({"status": "ok", "database": "ok"})
