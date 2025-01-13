from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json
from functools import wraps

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Auth-Code", "X-API-Key"]
    }
})

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

@app.route('/verify', methods=['POST'])
def verify():
    try:
        print("收到验证请求")  # 调试日志
        data = request.get_json()
        print(f"请求数据: {data}")  # 调试日志
        
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
            
        auth_code = data.get('authCode')
        api_key = data.get('apiKey')
        print(f"授权码: {auth_code}")  # 调试日志
        
        if not auth_code or not api_key:
            return jsonify({'success': False, 'error': 'Missing authorization code or API key'}), 400
            
        if auth_code not in VALID_AUTH_CODES:
            return jsonify({'success': False, 'error': 'Invalid authorization code'}), 401
            
        # 测试 Moonshot API 密钥
        try:
            test_url = "https://api.moonshot.cn/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            test_response = requests.post(
                test_url,
                headers=headers,
                json={
                    "model": "moonshot-v1-8k",
                    "messages": [{"role": "user", "content": "test"}],
                }
            )
            test_response.raise_for_status()
        except Exception as e:
            print(f"Moonshot API 测试失败: {str(e)}")  # 调试日志
            return jsonify({'success': False, 'error': 'Invalid Moonshot API key'}), 401
            
        print("验证成功")  # 调试日志
        return jsonify({
            'success': True,
            'user': VALID_AUTH_CODES[auth_code]
        })
    except Exception as e:
        print(f"发生错误: {str(e)}")  # 调试日志
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        title = data.get('title')
        auth_code = request.headers.get('Authorization')
        api_key = request.headers.get('X-API-KEY')
        
        if not title:
            return jsonify({'success': False, 'error': 'Missing title'}), 400
            
        if not auth_code or not api_key:
            return jsonify({'success': False, 'error': 'Missing authorization'}), 401
            
        if auth_code not in VALID_AUTH_CODES:
            return jsonify({'success': False, 'error': 'Invalid authorization code'}), 401
            
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
            'success': True,
            'result': story_content
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': f'API request failed: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run() 