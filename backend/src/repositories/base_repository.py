from config.database import SessionLocal, engine

class BaseRepository:
    """Base repository for handling database sessions"""
    
    def __init__(self):
        self.session = SessionLocal()
        self.engine = engine

    def close(self):
        self.session.close()
