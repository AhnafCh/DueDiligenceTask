import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = str(Path(__file__).parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

import sqlite3
import pytest
from src.services.langgraph_persistence import LangGraphPersistence, CHECKPOINT_DB_PATH

def test_checkpoint_db_creation():
    """Verify the checkpoint database is created."""
    if os.path.exists(CHECKPOINT_DB_PATH):
        os.remove(CHECKPOINT_DB_PATH)
    
    with LangGraphPersistence.get_sqlite_checkpointer() as saver:
        assert os.path.exists(CHECKPOINT_DB_PATH)
        assert saver is not None

def test_sqlite_saver_functionality():
    """Verify basic SqliteSaver interactions."""
    with LangGraphPersistence.get_sqlite_checkpointer() as saver:
        # Instead of just checking tables, let's try to interact with it.
        # If it's a valid LangGraph saver, it should have a 'get' method.
        # We'll use a dummy config.
        config = {"configurable": {"thread_id": "test_thread"}}
        
        # This shouldn't crash. If it's the first time, it might return None
        # but the internal tables should be initialized.
        checkpoint = saver.get(config)
        
        # Now check tables.
        conn = sqlite3.connect(CHECKPOINT_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Detected tables after access: {tables}")
        
        assert len(tables) > 0, "No tables created even after saver access"
        conn.close()

def test_multiple_connections():
    """Verify that multiple checkpointer instances can be created."""
    with LangGraphPersistence.get_sqlite_checkpointer() as saver1:
        with LangGraphPersistence.get_sqlite_checkpointer() as saver2:
            assert saver1 is not saver2
