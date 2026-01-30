"""
Personal Dashboard Application Factory.
"""
from flask import Flask
from flask_cors import CORS

from .config import config, Config
from .routes import api_bp
from .utils import setup_logger


def create_app(config_name: str = 'default') -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        config_name: Configuration to use ('development', 'production', 'test', 'default')
    
    Returns:
        Configured Flask application
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Setup logging
    logger = setup_logger(
        __name__,
        log_file=app.config.get('LOG_FILE'),
        level=app.config.get('LOG_LEVEL', 'INFO')
    )
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    # Log configuration warnings
    warnings = Config.validate()
    if warnings:
        logger.warning("Configuration warnings:")
        for warning in warnings:
            logger.warning(f"  - {warning}")
    
    logger.info(f"Application created with {config_name} configuration")
    
    return app
