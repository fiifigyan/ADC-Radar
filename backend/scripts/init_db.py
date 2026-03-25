import os
from dotenv import load_dotenv
from database import notion_handler
from utils.exceptions import DatabaseException
import logging

load_dotenv()
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize Notion database connection"""
    try:
        logger.info("Initializing Notion database...")
        notion_handler.verify_connection()
        logger.info("Notion database initialized successfully")
    except DatabaseException as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during initialization: {e}")
        raise

if __name__ == "__main__":
    initialize_database()
