import os
import logging
import kaggle
import zipfile
import pandas as pd
import time

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from models.product import Base, Product

class DataRepository:
    """Repository handling data access operations with PostgreSQL"""
    
    def __init__(self):
        # Set up logging
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        load_dotenv()
        self.logger.info("Start postgresql connection")
        
        db_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'mydatabase'),
            'user': os.getenv('DB_USER', 'myuser'),
            'password': os.getenv('DB_PASSWORD', 'mypassword'),
            'port': os.getenv('DB_PORT', '5432')
        }
        connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
        self.engine = create_engine(connection_string)
        
        # Create tables explicitly and ensure it’s committed
        Base.metadata.create_all(self.engine, checkfirst=True)
        
        # Initialize session after table creation
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        self.logger.info("PostgreSQL connection established successfully")

    def ingest_kaggle_data(self):
        """Ingest Kaggle data using SQLAlchemy ORM"""
        self.logger.info("Checking if ingestion is needed...")
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM products"))
            count = result.scalar()
            
            if count > 100000:
                self.logger.info(f"Products table already contains data ({count} records). Skipping ingestion.")
                return
            
        self.logger.info("No data found. Starting Kaggle ingestion...")
        os.environ["KAGGLE_KEY"] = os.getenv('KAGGLE_KEY')
        os.environ["KAGGLE_USERNAME"] = os.getenv('KAGGLE_USERNAME')

        # Define file paths
        zip_path = 'amazon-product-data.zip'
        dataset_csv_path = './data/raw/dataset/train.csv'

        # Download only if zip doesn't exist
        if not os.path.exists(zip_path):
            self.logger.info("Downloading dataset from Kaggle...")
            os.system('kaggle datasets download -d piyushjain16/amazon-product-data')
        else:
            self.logger.info("Zip file already exists, skipping download")

        # Unzip only if CSV doesn't exist
        if not os.path.exists(dataset_csv_path):
            self.logger.info("Unzipping dataset...")
            os.system('unzip -o amazon-product-data.zip -d ./data/raw')
        else:
            self.logger.info("CSV file already exists, skipping extraction")
        
        self.logger.info("Clearing existing products table...")
        with self.engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS products"))
            conn.commit()
            self.logger.info("Products table dropped")
            
        Product.__table__.create(self.engine)
        self.logger.info("Products table created")


        start_time = time.time()
        df = pd.read_csv(dataset_csv_path)  # Reduced for debugging
        self.logger.info(f"Loaded {len(df)} rows in {time.time() - start_time:.2f} seconds")
        
        # Process column names
        df.columns = [col.lower() for col in df.columns]
        
        # Use SQLAlchemy ORM to insert records in chunks
        start_time = time.time()
        try:
            # Create session
            Session = sessionmaker(bind=self.engine)
            session = Session()
            
            # Assuming you have a Product model defined
            Base = declarative_base()
            
            # Insert in batches
            batch_size = 500
            total_inserted = 0
            
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                records = []
                
                for _, row in batch.iterrows():
                    product = Product(**row.to_dict())
                    records.append(product)
                
                session.add_all(records)
                session.commit()
                
                total_inserted += len(batch)
                self.logger.info(f"Inserted batch: {total_inserted}/{len(df)} records")
            
            # Create indexes
            with self.engine.connect() as conn:
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_product_id ON products(product_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_product_type ON products(product_type_id)"))
                conn.commit()
            
            self.logger.info(f"Kaggle data ingestion complete. {total_inserted} records imported in {time.time() - start_time:.2f} seconds")
        
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error importing data: {e}")
            raise
        finally:
            session.close()

    def fetch_products(self, page=1, limit=10):
        """Fetch paginated products"""
        offset = (page - 1) * limit
        products = self.session.query(Product).limit(limit).offset(offset).all()
        return [product.to_dict() for product in products]
    
    def count_products(self):
        """Count total products"""
        return self.session.query(Product).count()
