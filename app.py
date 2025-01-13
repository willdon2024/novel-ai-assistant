from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json
from functools import wraps

app = Flask(__name__)
CORS(app)

# 授权码列表
VALID_AUTH_CODES = {
    "TEST001": "测试用户1",
    "TEST002": "测试用户2",
}

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_code = request.headers.get('X-Auth-Code')
        api_key = request.headers.get('X-API-Key')
        
        if not auth_code or not api_key:
            return jsonify({'error': 'Missing authorization code or API key'}), 401
        
        if auth_code not in VALID_AUTH_CODES:
            return jsonify({'error': 'Invalid authorization code'}), 401
            
        return f(*args, **kwargs)
    return decorated

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

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    auth_code = data.get('authCode')
    api_key = data.get('apiKey')
    
    if not auth_code or not api_key:
        return jsonify({'error': 'Missing authorization code or API key'}), 400
        
    if auth_code not in VALID_AUTH_CODES:
        return jsonify({'error': 'Invalid authorization code'}), 401
        
    return jsonify({
        'status': 'success',
        'user': VALID_AUTH_CODES[auth_code]
    })

@app.route('/generate', methods=['POST'])
@require_auth
def generate():
    try:
        data = request.get_json()
        title = data.get('title')
        
        if not title:
            return jsonify({'error': 'Missing title'}), 400
            
        api_key = request.headers.get('X-API-Key')
        
        # 构建 Moonshot API 请求
        moonshot_url = "https://api.moonshot.cn/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        prompt = f"""请你作为一个专业的小说策划师，根据小说标题「{title}」，详细输出：
1. 故事背景
2. 主要人物及其关系
3. 重要线索和伏笔
4. 故事梗概

请确保内容合理且有创意。"""

        payload = {
            "model": "moonshot-v1-8k",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }

        response = requests.post(moonshot_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        story_content = result['choices'][0]['message']['content']
        
        return jsonify({
            'status': 'success',
            'content': story_content
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'API request failed: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run() 