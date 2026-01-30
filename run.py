#!/usr/bin/env python3
"""
Personal Dashboard - Main Entry Point

Run the dashboard application:
    python run.py

Options:
    --host: Host address (default: 0.0.0.0)
    --port: Port number (default: 5000)
    --config: Configuration mode (development, production, test)
    --debug: Enable debug mode
"""
import os
import sys
import argparse

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.config import Config


def main():
    """Main entry point for the dashboard"""
    parser = argparse.ArgumentParser(description='Personal Dashboard Application')
    parser.add_argument(
        '--host',
        default=None,
        help=f'Host address (default: {Config.HOST})'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help=f'Port number (default: {Config.PORT})'
    )
    parser.add_argument(
        '--config',
        choices=['development', 'production', 'test', 'default'],
        default='default',
        help='Configuration mode (default: default)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    args = parser.parse_args()
    
    # Create app with specified configuration
    app = create_app(args.config)
    
    # Override config with command line arguments
    host = args.host or app.config.get('HOST', '0.0.0.0')
    port = args.port or app.config.get('PORT', 5000)
    debug = args.debug or app.config.get('DEBUG', False)
    
    print("🚀 Starting Personal Dashboard...")
    print(f"📊 Access your dashboard at: http://localhost:{port}")
    print(f"⚙️  Configuration: {args.config}")
    print(f"🐛 Debug mode: {'enabled' if debug else 'disabled'}")
    print()
    
    # Run the application
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
