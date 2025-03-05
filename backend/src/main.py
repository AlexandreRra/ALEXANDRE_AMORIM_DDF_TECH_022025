import logging
import os
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from dotenv import load_dotenv
from routes import router
from repositories.product_repository import ProductRepository

load_dotenv()
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
CORS(app)

Swagger(app)

app.register_blueprint(router)

product_repository = ProductRepository()
product_repository.save_raw_kaggle_data()

if __name__ == '__main__':
    app.logger.info("Starting Flask app...")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)