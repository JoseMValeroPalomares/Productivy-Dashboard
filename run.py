from app import create_app
from config import ProductionConfig

app = create_app(ProductionConfig)
gunicorn_app = app 

