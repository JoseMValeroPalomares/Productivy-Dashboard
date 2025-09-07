from app import create_app
from config import ProductionConfig

app = create_app(ProductionConfig)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)  # '0.0.0.0' escucha en todas las IPs
