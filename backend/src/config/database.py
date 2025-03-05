import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

logger = logging.getLogger(__name__)

if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logger.info("Initializing PostgreSQL connection")

db_params = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'mydatabase'),
    'user': os.getenv('DB_USER', 'myuser'),
    'password': os.getenv('DB_PASSWORD', 'mypassword'),
    'port': os.getenv('DB_PORT', '5432')
}

connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
engine = create_engine(connection_string, pool_pre_ping=True)

SessionLocal = scoped_session(sessionmaker(bind=engine))

logger.info("PostgreSQL connection initialized successfully")
