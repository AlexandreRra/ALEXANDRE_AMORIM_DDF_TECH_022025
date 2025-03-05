import pytz
from flask import Blueprint, request, current_app
from controllers.product_controller import product_controller
from datetime import datetime

router = Blueprint('router', __name__)

router.register_blueprint(product_controller.get_blueprint(), url_prefix='/products')

@router.before_request
def log_request_info():
    brazil_tz = pytz.timezone('America/Sao_Paulo')
    brazil_time = datetime.now(brazil_tz).strftime('%Y-%m-%d %H:%M:%S')

    current_app.logger.info(f"\n[{brazil_time}] Received a {request.method} request on {request.path}")
    current_app.logger.info(f"Headers: {request.headers.get('User-Agent')}")
    current_app.logger.info(f"Body: {request.get_json(silent=True)}")
    current_app.logger.info(f"Query: {request.args}")
