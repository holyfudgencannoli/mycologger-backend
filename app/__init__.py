from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager, JWTManager
from config import Config
from .db import Base, engine
from .routes import app_bp, BLACKLIST
from .routes.users_routes import users_bp
from .routes.authentication_routes import auth_bp
from .routes.purchase_logs_routes import purchase_logs_bp


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:8081", "http://localhost"]}}, supports_credentials=True)
    jwt = JWTManager(app)


    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return jti in BLACKLIST
    
    app.register_blueprint(app_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    # app.register_blueprint(fields_bp, url_prefix='/api/fields')
    # app.register_blueprint(inventories_bp, url_prefix='/api/inventories')
    # app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(purchase_logs_bp, url_prefix='/api/purchase-logs')
    # app.register_blueprint(raw_materials_bp, url_prefix='/api/raw-materials')
    # app.register_blueprint(specimens_bp, url_prefix='/api/specimens')
    # app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    # app.register_blueprint(usage_logs_bp, url_prefix='/api/usage-logs')
    # app.register_blueprint(vendors_bp, url_prefix='/api/vendors')
    # app.register_blueprint(recipes_bp, url_prefix='/api/recipes')
    # app.register_blueprint(receipts_bp, url_prefix='/api/receipts')
    app.register_blueprint(users_bp, url_prefix='/api/users')

    Base.metadata.create_all(bind=engine)

    return app


