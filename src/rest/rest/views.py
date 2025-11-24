"""REST API views for todos."""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from todos.service import TodoService
from rest.db import get_mongo_client

logger = logging.getLogger(__name__)


def _int_param(request, name, default):
    value = request.query_params.get(name)
    if value is None:
        return default
    try:
        n = int(value)
    except (TypeError, ValueError):
        return default
    return max(n, 1)


class TodoListView(APIView):

    def get(self, request):
        try:
            page = _int_param(request, 'page', 1)
            page_size = _int_param(request, 'page_size', 10)

            result = TodoService.list_todos(page=page, page_size=page_size)
            
            return Response({
                'results': result['todos'],
                'page': result['page'],
                'page_size': result['page_size'],
                'total': result['total'],
                'total_pages': result['total_pages'],
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Error fetching todos")
            return Response(
                {"error": "Unable to fetch todos"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Create a new todo."""
        try:
            text = request.data.get("text")
            todo, error = TodoService.create_todo(text)
            
            if error:
                return Response(
                    {"error": error},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(todo, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception("Error creating todo")
            return Response(
                {"error": "Unable to create todo"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthView(APIView):
    """Health check endpoint for monitoring."""

    def get(self, request):
        """Check if service is healthy."""
        try:
            mongo_client = get_mongo_client()
            if mongo_client.health_check():
                return Response({'status': 'ok'}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'status': 'error'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
        except Exception:
            logger.exception('Health check failed')
            return Response(
                {'status': 'error'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

