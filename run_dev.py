#!/usr/bin/env python3
"""
Development server runner with OAuth HTTP workaround
"""
import os

# Allow OAuth2 to work with HTTP for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from app import app

if __name__ == '__main__':
    print("Starting development server...")
    print("OAuth HTTP workaround enabled for local development")
    print("Server running at: http://localhost:5050")
    app.run(debug=True, port=5050) 