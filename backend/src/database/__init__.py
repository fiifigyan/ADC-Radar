"""
Database module for Africa Digital Consultancy Radar
"""

from src.database.local_db import LocalDatabase
from src.database.notion_db import NotionDatabase

__all__ = [
    'LocalDatabase',
    'NotionDatabase'
]

# Optional: Create database factory function
def get_database(db_type='local', **kwargs):
    """
    Factory function to get database instance
    
    Args:
        db_type: 'local' or 'notion'
        **kwargs: Database-specific parameters
    
    Returns:
        Database instance
    """
    if db_type == 'local':
        return LocalDatabase(**kwargs)
    elif db_type == 'notion':
        return NotionDatabase(**kwargs)
    else:
        raise ValueError(f"Unknown database type: {db_type}")