import logging

from flask import Blueprint, jsonify, request
from flasgger import swag_from
from repositories.product_repository import ProductRepository

class ProductController:
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
        self.logger = logging.getLogger(__name__)
        self.blueprint = Blueprint('products', __name__)
        self._initialize_routes()

    def _initialize_routes(self):
        @self.blueprint.route('', methods=['GET'])
        @swag_from({
            'responses': {
                200: {
                    'description': 'List of all products',
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'data': {'type': 'array', 'items': {'type': 'object'}},
                            'total': {'type': 'integer'}
                        }
                    }
                }
            }
        })
        def get_products():
            try:
                result = self.product_repository.fetch_products()
                return jsonify({
                    'success': True,
                    'data': result['data'],
                    'total': result['total']
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500
                
            
        @self.blueprint.route('/distribution', methods=['GET'])
        @swag_from({
            'responses': {
                200: {
                    'description': 'List of top 20 product distributions by product type with counts.',
                    'schema': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'product_type_id': {
                                    'type': 'integer',
                                    'description': 'The ID of the product type.'
                                },
                                'count': {
                                    'type': 'integer',
                                    'description': 'The count of products for this product type.'
                                }
                            },
                            'required': ['product_type_id', 'count']
                        }
                    }
                },
                500: {
                    'description': 'Internal Server Error during fetching product distribution data.',
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string', 'example': 'An error occurred while processing the request.'}
                        }
                    }
                }
            }
        })
        def get_products_distribution():
            """Fetch product distribution by type."""
            try:
                result = self.product_repository.product_distribution()
                return jsonify(result['data']), 200
            except Exception as e:
                self.logger.error(f"Error in get_products_distribution: {str(e)}")
                return jsonify({"message": str(e)}), 500
            
        @self.blueprint.route('/scatter-distribution', methods=['GET'])
        @swag_from({
            'responses': {
                200: {
                    'description': 'List of product lengths and types for scatter plot.',
                    'schema': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'product_length': {
                                    'type': 'number',
                                    'description': 'The length of the product.'
                                },
                                'product_type_id': {
                                    'type': 'integer',
                                    'description': 'The ID of the product type.'
                                }
                            },
                            'required': ['product_length', 'product_type_id']
                        }
                    }
                },
                500: {
                    'description': 'Internal Server Error during fetching scatter plot data.',
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string', 'example': 'An error occurred while processing the request.'}
                        }
                    }
                }
            }
        })
        def get_scatter_distribution():
            """Fetch data for scatter plot: product_length vs product_type_id."""
            try:
                result = self.product_repository.product_scatter_distribution()
                return jsonify(result['data']), 200
            except Exception as e:
                self.logger.error(f"Error fetching product distribution: {str(e)}")
                return jsonify({"message": str(e)}), 500
            
        @self.blueprint.route('/empty-columns', methods=['GET'])
        @swag_from({
            'responses': {
                200: {
                    'description': 'Distribution of empty columns for pie chart.',
                    'schema': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'category': {
                                    'type': 'string',
                                    'description': 'The empty column category (e.g., "description", "bullet_points", "no_empty_data")'
                                },
                                'count': {
                                    'type': 'integer',
                                    'description': 'The number of products in this category.'
                                }
                            },
                            'required': ['category', 'count']
                        }
                    }
                },
                500: {
                    'description': 'Internal Server Error during fetching empty columns data.',
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string', 'example': 'An error occurred while processing the request.'}
                        }
                    }
                }
            }
        })
        def get_empty_columns_distribution():
            """Fetch distribution of empty columns for pie chart."""
            try:
                result = self.product_repository.empty_columns_distribution()
                return jsonify(result['data']), 200
            except Exception as e:
                self.logger.error(f"Error in get_empty_columns_distribution: {str(e)}")
                return jsonify({"message": str(e)}), 500

        @self.blueprint.route('/products-by-empty', methods=['GET'])
        @swag_from({
            'responses': {
                200: {
                    'description': 'List of products for a specific empty column category.',
                    'schema': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'product_id': {'type': 'string', 'description': 'The product ID'},
                                'title': {'type': 'string', 'description': 'The product title'},
                                'bullet_points': {'type': 'string', 'description': 'The product bullet points'},
                                'description': {'type': 'string', 'description': 'The product description'},
                                'product_type_id': {'type': 'integer', 'description': 'The product type ID'},
                                'product_length': {'type': 'number', 'description': 'The product length'},
                                'empty_cols': {'type': 'string', 'description': 'Comma-separated list of empty columns'}
                            }
                        }
                    }
                },
                500: {
                    'description': 'Internal Server Error during fetching products by empty category.',
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string', 'example': 'An error occurred while processing the request.'}
                        }
                    }
                }
            }
        })
        def get_products_by_empty():
            """Fetch products based on the selected empty column category with pagination."""
            try:
                empty_category = request.args.get('category', 'no_empty_data')
                page = int(request.args.get('page', 1))
                page_size = int(request.args.get('pageSize', 50))
                result = self.product_repository.get_products_by_empty_category(empty_category, page, page_size)
                return jsonify(result), 200
            except ValueError as ve:
                self.logger.error(f"Invalid pagination parameters: {str(ve)}")
                return jsonify({"message": "Invalid page or pageSize parameters"}), 400
            except Exception as e:
                self.logger.error(f"Error in get_products_by_empty: {str(e)}")
                return jsonify({"message": str(e)}), 500
            
        @self.blueprint.route('/temporal-trend', methods=['GET'])
        @swag_from({
            'responses': {
                200: {
                    'description': 'Temporal trend of products by creation/update date.',
                    'schema': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'day': {'type': 'string', 'format': 'date-time', 'description': 'The day of product creation/update'},
                                'count': {'type': 'integer', 'description': 'Number of products on that day'}
                            },
                            'required': ['day', 'count']
                        }
                    }
                },
                500: {
                    'description': 'Internal Server Error during fetching temporal trend data.',
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string', 'example': 'An error occurred while processing the request.'}
                        }
                    }
                }
            }
        })
        def get_temporal_trend():
            """Fetch temporal trend of products for line chart."""
            try:
                result = self.product_repository.get_temporal_trend()
                return jsonify(result['data']), 200
            except Exception as e:
                self.logger.error(f"Error in get_temporal_trend: {str(e)}")
                return jsonify({"message": str(e)}), 500
            
        @self.blueprint.route('/density-heatmap', methods=['GET'])
        @swag_from({
            'responses': {
                200: {
                    'description': 'Density heatmap data for product_length vs product_type_id.',
                    'schema': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'length_bucket': {'type': 'integer', 'description': 'Binned product length'},
                                'product_type_id': {'type': 'integer', 'description': 'The ID of the product type'},
                                'count': {'type': 'integer', 'description': 'Number of products in this bin'}
                            },
                            'required': ['length_bucket', 'product_type_id', 'count']
                        }
                    }
                },
                500: {
                    'description': 'Internal Server Error during fetching density heatmap data.',
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string', 'example': 'An error occurred while processing the request.'}
                        }
                    }
                }
            }
        })
        def get_density_heatmap():
            """Fetch temporal trend of products for line chart."""
            try:
                result = self.product_repository.get_density_heatmap()
                return jsonify(result['data']), 200
            except Exception as e:
                self.logger.error(f"Error in get_temporal_trend: {str(e)}")
                return jsonify({"message": str(e)}), 500

    def get_blueprint(self):
        return self.blueprint

product_repository = ProductRepository()
product_controller = ProductController(product_repository)