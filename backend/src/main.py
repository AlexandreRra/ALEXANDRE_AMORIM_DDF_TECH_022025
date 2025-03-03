import logging
import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from repositories.data_repository import DataRepository

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
CORS(app)

# Dependency Injection
data_repository = DataRepository()
data_repository.ingest_kaggle_data()

@app.route('/products', methods=['GET'])
def get_products():
    """Get paginated products"""
    products = data_repository.fetch_products()
    
    # Replacing print with proper logging
    app.logger.debug(f"Returning {len(products)} products")  # Debug log
    
    return jsonify({
        "data": products,
        "total": data_repository.count_products()
    })

if __name__ == '__main__':
    app.logger.info("Starting Flask app...")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
