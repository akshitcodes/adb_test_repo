"""Data Access Object (DAO) for todos."""
import logging
from bson import ObjectId
from rest.db import get_db

logger = logging.getLogger(__name__)

TODOS_COLLECTION = "todos"


def _id_to_str(doc):
    """Convert MongoDB _id to string representation and remove _id field."""
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


class TodoDAO:
    """Data Access Object for todos collection."""

    @staticmethod
    def get_collection():
    
        db = get_db()
        return db[TODOS_COLLECTION]

    @staticmethod
    def create_todo(todo_data):
        """
        Insert a new todo into the database.

        Args:
            todo_data (dict): Todo data (text, created_at, etc.)

        Returns:
            dict: Created todo with id field (string representation of _id).
        """
        collection = TodoDAO.get_collection()
        result = collection.insert_one(todo_data)
        # Fetch the created document from DB to ensure clean JSON-serializable data
        doc = collection.find_one({"_id": result.inserted_id})
        return _id_to_str(doc)

    @staticmethod
    def get_todos(page=1, page_size=10, filter_dict=None):
  
        collection = TodoDAO.get_collection()
        filter_dict = filter_dict or {}
        
        total = collection.count_documents(filter_dict)
        skip = (page - 1) * page_size
        
        cursor = collection.find(filter_dict).skip(skip).limit(page_size)
        todos = [_id_to_str(doc) for doc in cursor]
        
        return todos, total

    @staticmethod
    def get_todo_by_id(todo_id):

        try:
            collection = TodoDAO.get_collection()
            doc = collection.find_one({"_id": ObjectId(todo_id)})
            return _id_to_str(doc) if doc else None
        except Exception as e:
            logger.warning(f"Error retrieving todo {todo_id}: {e}")
            return None

    @staticmethod
    def update_todo(todo_id, update_data):

        try:
            collection = TodoDAO.get_collection()
            result = collection.find_one_and_update(
                {"_id": ObjectId(todo_id)},
                {"$set": update_data},
                return_document=True,
            )
            return _id_to_str(result) if result else None
        except Exception as e:
            logger.warning(f"Error updating todo {todo_id}: {e}")
            return None

    @staticmethod
    def delete_todo(todo_id):
 
        try:
            collection = TodoDAO.get_collection()
            result = collection.delete_one({"_id": ObjectId(todo_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.warning(f"Error deleting todo {todo_id}: {e}")
            return False

    @staticmethod
    def count_todos(filter_dict=None):

        collection = TodoDAO.get_collection()
        filter_dict = filter_dict or {}
        return collection.count_documents(filter_dict)

    @staticmethod
    def ensure_indexes():
        """Create indexes for optimal query performance."""
        collection = TodoDAO.get_collection()
        try:
            # Index on created_at for sorting
            collection.create_index("created_at")
            # Text index on text field for future full-text search
            collection.create_index([("text", "text")])
            logger.info("Indexes created/verified successfully")
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")
