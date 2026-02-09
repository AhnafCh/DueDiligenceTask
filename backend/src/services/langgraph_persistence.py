import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from contextlib import contextmanager
import os

# Path to the LangGraph checkpoint database
CHECKPOINT_DB_PATH = os.path.join(os.getcwd(), "langgraph_checkpoints.db")

class LangGraphPersistence:
    """
    Manages LangGraph checkpointers for state persistence.
    """
    
    @staticmethod
    @contextmanager
    def get_sqlite_checkpointer():
        """
        Provides a SqliteSaver checkpointer.
        Using a context manager to ensure the connection is closed.
        """
        conn = sqlite3.connect(CHECKPOINT_DB_PATH, check_same_thread=False)
        try:
            yield SqliteSaver(conn)
        finally:
            conn.close()

    @staticmethod
    def get_checkpointer():
        """
        Simple getter for the checkpointer.
        Note: The connection should ideally be managed per-request or per-thread.
        """
        conn = sqlite3.connect(CHECKPOINT_DB_PATH, check_same_thread=False)
        return SqliteSaver(conn)
