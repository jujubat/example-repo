#!/usr/bin/env python
"""Minimal Flask test to verify port binding works"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/api/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    print("Starting minimal test server on 127.0.0.1:8000...")
    app.run(host='127.0.0.1', port=8000, debug=False, use_reloader=False, threaded=False)
