import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

def load_kaggle_data_to_postgres():
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Configurar credenciais Kaggle
    os.environ["KAGGLE_KEY"] = os.getenv('KAGGLE_KEY')
    os.environ["KAGGLE_USERNAME"] = os.getenv('KAGGLE_USERNAME')
    
    # Baixar dataset do Kaggle
    os.system('kaggle datasets download -d piyushjain16/amazon-product-data')
    os.system('unzip -o amazon-product-data.zip -d ./data/raw')
    
    # Ler o CSV
    dataset_csv_path = '../data/raw/dataset/train.csv'
    df = pd.read_csv(dataset_csv_path)
    
    # Normalizar nomes das colunas (para minúsculas)
    df.columns = [col.lower() for col in df.columns]
    
    # Configurar conexão com PostgreSQL
    db_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'ecommerce'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    # Criar engine SQLAlchemy
    connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    engine = create_engine(connection_string)
    
    # Criar tabela e importar dados
    try:
        print("Conectando ao PostgreSQL...")
        
        print("Importando dados para PostgreSQL...")
        df.to_sql('products', engine, if_exists='replace', index=False)
        
        with engine.connect() as conn:
            conn.execute("CREATE INDEX IF NOT EXISTS idx_product_id ON products(product_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_product_type ON products(product_type_id);")
        
        print(f"Importação concluída. {len(df)} registros importados.")
        
    except Exception as e:
        print(f"Erro ao importar dados: {e}")
        raise
    
    return len(df)

if __name__ == "__main__":
    load_kaggle_data_to_postgres()