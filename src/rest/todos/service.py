"""Business logic service layer for todos."""
import logging
from datetime import datetime
from todos.dao import TodoDAO

logger = logging.getLogger(__name__)

MAX_TODO_LENGTH = 200


class TodoService:
    """Service layer for todo business logic."""

    @staticmethod
    def validate_todo_text(text):

        if not text or not isinstance(text, str):
            return False, "Text is required and must be a string"
        
        text = text.strip()
        if not text:
            return False, "Text cannot be empty or whitespace only"
        
        if len(text) > MAX_TODO_LENGTH:
            return False, f"Text must be {MAX_TODO_LENGTH} characters or fewer"
        
        return True, None

    @staticmethod
    def create_todo(text):

        is_valid, error = TodoService.validate_todo_text(text)
        if not is_valid:
            return None, error
        
        todo_data = {
            "text": text.strip(),
            "created_at": datetime.utcnow(),
            "completed": False,
        }
        
        try:
            todo = TodoDAO.create_todo(todo_data)
            logger.info(f"Todo created with id: {todo['id']}")
            return todo, None
        except Exception as e:
            logger.error(f"Error creating todo: {e}")
            return None, "Failed to create todo"

    @staticmethod
    def list_todos(page=1, page_size=10):
        """
        List todos with pagination.

        Args:
            page (int): Page number (1-indexed).
            page_size (int): Number of items per page.

        Returns:
            dict: Pagination metadata and todo list.
        """
        todos, total = TodoDAO.get_todos(page=page, page_size=page_size)
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "todos": todos,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    @staticmethod
    def get_todo(todo_id):
        """
        Get a single todo by id.

        Args:
            todo_id (str): Todo id.

        Returns:
            dict or None: Todo document or None if not found.
        """
        return TodoDAO.get_todo_by_id(todo_id)

    @staticmethod
    def update_todo(todo_id, **fields):
        """
        Update a todo.

        Args:
            todo_id (str): Todo id.
            **fields: Fields to update (e.g., text, completed).

        Returns:
            tuple: (todo_dict, error) or (None, error_message) if not found or update fails.
        """
        # Validate fields if text is being updated
        if "text" in fields:
            is_valid, error = TodoService.validate_todo_text(fields["text"])
            if not is_valid:
                return None, error
            fields["text"] = fields["text"].strip()
        
        try:
            todo = TodoDAO.update_todo(todo_id, fields)
            if todo:
                logger.info(f"Todo {todo_id} updated")
                return todo, None
            else:
                return None, "Todo not found"
        except Exception as e:
            logger.error(f"Error updating todo {todo_id}: {e}")
            return None, "Failed to update todo"

    @staticmethod
    def delete_todo(todo_id):
        """
        Delete a todo.

        Args:
            todo_id (str): Todo id.

        Returns:
            tuple: (success, error_message)
        """
        try:
            if TodoDAO.delete_todo(todo_id):
                logger.info(f"Todo {todo_id} deleted")
                return True, None
            else:
                return False, "Todo not found"
        except Exception as e:
            logger.error(f"Error deleting todo {todo_id}: {e}")
            return False, "Failed to delete todo"

    @staticmethod
    def ensure_db_ready():
        """Ensure database is ready and indexes exist."""
        try:
            TodoDAO.ensure_indexes()
            return True
        except Exception as e:
            logger.error(f"Error preparing database: {e}")
            return False
