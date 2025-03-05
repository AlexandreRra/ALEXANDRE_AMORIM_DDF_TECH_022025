import os
import io
import logging
import pandas as pd
import time
import re
import pyarrow as pa
import pyarrow.parquet as pq

from sqlalchemy import text, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from repositories.base_repository import BaseRepository
from models.product_model import Product

class ProductRepository(BaseRepository):
    """Repository handling data access operations with PostgreSQL"""
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def clean_and_save_to_db(self, parquet_path='./data/processed/amazon_product_data.parquet'):
        """Clean data and save to Postgres"""
        self.logger.info("Clearing existing products table...")
        with self.engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS products"))
            conn.commit()
            self.logger.info("Products table dropped")
            
        self.logger.info("Loading Parquet for cleaning...")
        df = pd.read_parquet(parquet_path)

        text_cols = ['title', 'bullet_points', 'description']
        numeric_cols = ['product_id', 'product_type_id', 'product_length']

        df[text_cols] = df[text_cols].fillna('')
        df[numeric_cols] = df[numeric_cols].fillna({'product_length': df['product_length'].mean(), 'product_id': 0, 'product_type_id': 0})

        def clean_text(text):
            if not text: return ''
            text = str(text)
            text = re.sub(r'<.*?>', '', text)
            text = re.sub(r'[^\w\s.,;:!?-]', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            return text.strip()

        for col in text_cols:
            df[col] = df[col].apply(clean_text)

        df['empty_cols'] = df[text_cols].apply(
            lambda row: ','.join(col for col in text_cols if not row[col]), axis=1
        )
        df['description'] = df.apply(
            lambda row: row['bullet_points'] if not row['description'] else row['description'], axis=1
        )
        df['description'] = df.apply(
            lambda row: row['title'] if not row['description'] and not row['bullet_points'] else row['description'], axis=1
        )

        df[text_cols] = df[text_cols].apply(lambda x: x.str.lower())

        self.logger.info("Saving cleaned data to Postgres...")
        with self.engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS products"))
            conn.commit()
        Product.__table__.create(self.engine)

        batch_size = 10000
        start_time = time.time()
        with sessionmaker(bind=self.engine)() as session:
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i + batch_size]
                records = [Product(**row.to_dict()) for _, row in batch.iterrows()]
                session.add_all(records)
                session.commit()
                self.logger.info(f"Inserted {i + len(batch)}/{len(df)} records")
        
        with self.engine.connect() as conn:
            conn.execute(text("CREATE INDEX idx_product_id ON products(product_id)"))
            conn.execute(text("CREATE INDEX idx_product_type ON products(product_type_id)"))
            conn.commit()
        
        self.logger.info(f"Cleaned data saved to DB in {time.time() - start_time:.2f}s")

    def save_raw_kaggle_data(self):
        """Ingest Kaggle data and save as Parquet with metadata"""
        with self.engine.connect() as conn:
            table_exists = conn.execute(
                text("SELECT EXISTS (SELECT FROM pg_tables WHERE tablename = 'products')")
            ).scalar()
            
            if table_exists:
                result = conn.execute(text("SELECT COUNT(*) FROM products"))
                count = result.scalar()
                if count > 100000:
                    self.logger.info(f"Products table already contains data ({count} records). Skipping ingestion.")
                    return
            else:
                self.logger.info("Products table does not exist. Proceeding with ingestion.")
        self.logger.info("Checking existing data...")
        parquet_path = './data/processed/amazon_product_data.parquet'
        os.makedirs(os.path.dirname(parquet_path), exist_ok=True)
        if os.path.exists(parquet_path):
            self.logger.info("Parquet file exists. Skipping ingestion.")
            self.clean_and_save_to_db(parquet_path)
            return

        self.logger.info("Starting Kaggle ingestion...")
        zip_path = 'amazon-product-data.zip'
        csv_path = './data/raw/dataset/train.csv'

        if not os.path.exists(zip_path):
            self.logger.info("Downloading from Kaggle...")
            os.environ["KAGGLE_KEY"] = os.getenv('KAGGLE_KEY')
            os.environ["KAGGLE_USERNAME"] = os.getenv('KAGGLE_USERNAME')
            os.system('kaggle datasets download -d piyushjain16/amazon-product-data')
            
        if not os.path.exists(csv_path):
            self.logger.info("Unzipping dataset...")
            os.system(f'unzip -o {zip_path} -d ./data/raw')

        start_time = time.time()
        df = pd.read_csv(csv_path)
        df.columns = [col.lower() for col in df.columns]
        self.logger.info(f"Loaded {len(df)} rows in {time.time() - start_time:.2f}s")

        timestamp = pd.Timestamp.now().isoformat()
        metadata = {
            'source_file': csv_path,
            'landing_file': parquet_path,
            'rows': df.shape[0],
            'columns': df.shape[1],
            'column_names': df.columns.tolist(),
            'timestamp': timestamp,
            'null_counts': df.isnull().sum().to_dict()
        }

        os.makedirs(os.path.dirname(parquet_path), exist_ok=True)
        table = pa.Table.from_pandas(df)
        pq.write_table(table, parquet_path)
        self.logger.info(f"Saved to {parquet_path} in {time.time() - start_time:.2f}s")
        self.clean_and_save_to_db(parquet_path)
        
    
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

        zip_path = 'amazon-product-data.zip'
        dataset_csv_path = './data/raw/dataset/train.csv'

        if not os.path.exists(zip_path):
            self.logger.info("Downloading dataset from Kaggle...")
            os.system('kaggle datasets download -d piyushjain16/amazon-product-data')
        else:
            self.logger.info("Zip file already exists, skipping download")

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
        df = pd.read_csv(dataset_csv_path)
        self.logger.info(f"Loaded {len(df)} rows in {time.time() - start_time:.2f} seconds")
        
        df.columns = [col.lower() for col in df.columns]
        
        start_time = time.time()
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            
            Base = declarative_base()
            
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

    def product_distribution(self):
        """Query top 20 product distribution from the database."""
        try:
            distribution = (
                self.session.query(
                    Product.product_type_id,
                    func.count(Product.product_id).label('count')
                )
                .group_by(Product.product_type_id)
                .order_by(func.count(Product.product_id).desc())
                .limit(20)
                .all()
            )

            result = [{'product_type_id': row[0], 'count': row[1]} for row in distribution]
            self.logger.debug(f"Returning distribution for {len(result)} product types (top 20)")
            return {'data': result}
        
        except Exception as e:
            self.logger.error(f"Error fetching product distribution: {str(e)}")
            raise

    def product_scatter_distribution(self):
        """Query data for scatter plot: product_length vs product_type_id"""
        try:
            distribution = (
                self.session.query(
                    Product.product_length,
                    Product.product_type_id
                )
                .filter(Product.product_length.isnot(None), Product.product_type_id.isnot(None))
                .limit(500)
                .all()
            )

            result = [{'product_length': row[0], 'product_type_id': row[1]} for row in distribution]
            self.logger.debug(f"Returning scatter data for {len(result)} products")
            return {'data': result}
        
        except Exception as e:
            self.logger.error(f"Error in get_scatter_distribution: {str(e)}")
            raise

    def empty_columns_distribution(self):
        """Query distribution of empty columns for pie chart using SQL aggregation."""
        try:
            no_empty_subquery = (
                self.session.query(
                    func.count(Product.product_id).label('count')
                )
                .filter(
                    (Product.empty_cols.is_(None)) | (Product.empty_cols == "")
                )
                .scalar()
            )
            no_empty_count = no_empty_subquery if no_empty_subquery is not None else 0

            empty_counts = (
                self.session.query(
                    func.trim(func.regexp_split_to_table(Product.empty_cols, ',')).label('category'),
                    func.count(Product.product_id).label('count')
                )
                .filter(Product.empty_cols.isnot(None), Product.empty_cols != "")
                .group_by(text('category'))
                .all()
            )

            result = [
                {'category': row.category.strip(), 'count': row.count}
                for row in empty_counts if row.category and row.category.strip()
            ]
            result.append({'category': 'no_empty_data', 'count': no_empty_count})

            self.logger.debug(f"Returning empty columns distribution for {len(result)} categories")
            return {'data': result}
        
        except Exception as e:
            self.logger.error(f"Error fetching empty columns distribution: {str(e)}")
            raise

    def get_products_by_empty_category(self, category: str, page: int = 1, page_size: int = 50):
        """Fetch products based on the specified empty column category with pagination."""
        try:
            query = self.session.query(Product)

            if category == 'no_empty_data':
                query = query.filter((Product.empty_cols.is_(None)) | (Product.empty_cols == ""))
            else:
                query = query.filter(Product.empty_cols.contains(category))

            total = query.count()
            products = query.offset((page - 1) * page_size).limit(page_size).all()

            result = [
                {
                    'product_id': product.product_id,
                    'title': product.title,
                    'bullet_points': product.bullet_points,
                    'description': product.description,
                    'product_type_id': product.product_type_id,
                    'product_length': product.product_length,
                    'empty_cols': product.empty_cols if product.empty_cols else "no_empty_data"
                } for product in products
            ]

            self.logger.debug(f"Returning {len(result)} products for empty category '{category}' (page {page}, {page_size} per page, total {total})")
            return {'data': result, 'total': total}
        
        except Exception as e:
            self.logger.error(f"Error fetching products by empty category: {str(e)}")
            raise

    def get_temporal_trend(self):
        try:
            trend = (
                self.session.query(
                    Product.product_type_id,
                    func.count(Product.product_type_id).label('count')
                )
                .group_by(Product.product_type_id)
                .order_by(Product.product_type_id)
                .all()
            )
            
            result = [{'product_type_id': row.product_type_id, 'count': row.count} for row in trend]
            self.logger.debug(f"Raw trend data: {trend}")
            self.logger.debug(f"Returning trend for {len(result)} product types")
            return {'data': result}
        
        except Exception as e:
            self.logger.error(f"Error fetching trend: {str(e)}")
            raise
        
    def get_density_heatmap(self):
        """
        Query density heatmap data (product_length vs product_type_id binned) with dynamic min/max values.
        """
        try:
            min_length, max_length = self.session.query(
                func.min(Product.product_length), func.max(Product.product_length)
            ).first()

            if min_length is None or max_length is None or min_length == max_length:
                self.logger.warning("Invalid min/max values for product_length.")
                return {'data': []} 

            num_bins = 10

            heatmap = (
                self.session.query(
                    func.WIDTH_BUCKET(Product.product_length, min_length, max_length, num_bins).label('length_bucket'),
                    Product.product_type_id,
                    func.count(Product.product_id).label('count')
                )
                .filter(Product.product_length.isnot(None), Product.product_type_id.isnot(None))
                .group_by('length_bucket', Product.product_type_id)
                .all()
            )

            result = [{'length_bucket': row.length_bucket, 'product_type_id': row.product_type_id, 'count': row.count} for row in heatmap]
            self.logger.debug(f"Returning density heatmap for {len(result)} bins")
            return {'data': result}

        except Exception as e:
            self.logger.error(f"Error fetching density heatmap: {str(e)}")
            raise

    def fetch_products(self, page=1, limit=10):
        """Fetch paginated products"""
        offset = (page - 1) * limit
        products = self.session.query(Product).limit(limit).offset(offset).all()
        return {
            'data': [product.to_dict() for product in products],
            'total': self.session.query(Product).count()
        }
