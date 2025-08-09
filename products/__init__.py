# filepath: shopping-website/products/__init__.py

from flask import Blueprint

products_bp = Blueprint('products', __name__)

from . import data  # Importing data to make sure product data is loaded
