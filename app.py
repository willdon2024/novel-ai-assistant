from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["https://willdon2024.github.io"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-API-KEY"]
    }
})

# 测试用的授权码
VALID_AUTH_CODES = ["TEST001", "TEST002"]

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'auth_codes_count': len(VALID_AUTH_CODES)
    })

@app.route('/verify', methods=['POST'])
def verify():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Missing request data'}), 400
        
        auth_code = data.get('authCode')
        api_key = data.get('apiKey')
        
        if not auth_code or not api_key:
            return jsonify({'success': False, 'message': 'Missing authorization code or API key'}), 400
        
        # 验证授权码
        if auth_code not in VALID_AUTH_CODES:
            return jsonify({'success': False, 'message': 'Invalid authorization code'}), 401
        
        # 测试 Moonshot API 密钥
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        response = requests.post(
            "https://api.moonshot.cn/v1/chat/completions",
            headers=headers,
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "model": "moonshot-v1-8k"
            }
        )
        
        if response.status_code != 200:
            return jsonify({'success': False, 'message': 'Invalid API key'}), 401
            
        return jsonify({'success': True, 'message': 'Verification successful'})
        
    except Exception as e:
        print(f"Verification error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Missing request data'}), 400
            
        title = data.get('title')
        api_key = data.get('apiKey')
        
        if not title or not api_key:
            return jsonify({'success': False, 'message': 'Missing title or API key'}), 400
            
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        prompt = f"""请你作为一个专业的小说策划师，根据小说标题《{title}》，详细输出：
1. 故事背景设定
2. 主要人物关系
3. 重要剧情线索
4. 故事主题
请分点输出，确保内容合理且富有创意。"""
        
        response = requests.post(
            "https://api.moonshot.cn/v1/chat/completions",
            headers=headers,
            json={
                "messages": [{"role": "user", "content": prompt}],
                "model": "moonshot-v1-8k"
            }
        )
        
        if response.status_code != 200:
            return jsonify({'success': False, 'message': 'API request failed'}), 500
            
        content = response.json()['choices'][0]['message']['content']
        return jsonify({'success': True, 'content': content})
        
    except Exception as e:
        print(f"Generation error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 