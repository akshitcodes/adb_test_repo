from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json, logging, os
from pymongo import MongoClient
from math import ceil


def _int_param(request, name, default):
    value = request.query_params.get(name)
    if value is None:
        return default
    try:
        n = int(value)
    except (TypeError, ValueError):
        return default
    return max(n, 1)

mongo_uri = 'mongodb://' + os.environ["MONGO_HOST"] + ':' + os.environ["MONGO_PORT"]
db = MongoClient(mongo_uri)['test_db']

class TodoListView(APIView):

    def get(self, request):
        try:
            # pagination
            page = _int_param(request, 'page', 1)
            page_size = _int_param(request, 'page_size', 10)

            total = db.todos.count_documents({})
            skip = (page - 1) * page_size

            todos_cursor = db.todos.find({}, {"_id": 1, "text": 1}).skip(skip).limit(page_size)
            todos = []
            for doc in todos_cursor:
                todos.append({
                    "id": str(doc.get("_id")),
                    "text": doc.get("text", "")
                })

            total_pages = ceil(total / page_size) if page_size else 1

            return Response({
                'results': todos,
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': total_pages,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logging.exception("Error fetching todos")
            return Response({"error": "Unable to fetch todos"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def post(self, request):
        try:
            payload = request.data
            # support both 'text' and 'description' keys
            text = payload.get("text")
            if not text or not str(text).strip():
                return Response({"error": "'text' is required"}, status=status.HTTP_400_BAD_REQUEST)

            text = str(text).strip()
            # enforce max length
            MAX_TODO_LENGTH = 200
            if len(text) > MAX_TODO_LENGTH:
                return Response({"error": f"'text' must be at most {MAX_TODO_LENGTH} characters"}, status=status.HTTP_400_BAD_REQUEST)

            doc = {"text": text}
            result = db.todos.insert_one(doc)
            created = {"id": str(result.inserted_id), "text": doc["text"]}
            return Response(created, status=status.HTTP_201_CREATED)
        except Exception as e:
            logging.exception("Error creating todo")
            return Response({"error": "Unable to create todo"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

