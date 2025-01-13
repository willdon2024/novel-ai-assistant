from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json

app = Flask(__name__)
CORS(app)

# 授权码列表
VALID_AUTH_CODES = {
    "TEST001": "测试用户1",
    "TEST002": "测试用户2",
}

@app.route('/')
def home():
    return jsonify({
        'status': 'healthy',
        'message': 'Novel AI Assistant API is running'
    })

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'auth_codes_count': len(VALID_AUTH_CODES)
    })

if __name__ == '__main__':
    app.run() 