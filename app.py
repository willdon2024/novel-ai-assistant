from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json
from dotenv import load_dotenv
from functools import wraps

# 加载环境变量
load_dotenv()

app = Flask(__name__)
# 允许所有来源的跨域请求，包括 GitHub Pages 和本地开发环境
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://willdon2024.github.io",
            "http://localhost:5000",
            "http://127.0.0.1:5000"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-API-KEY"]
    }
})

# 授权码列表（实际应用中应该使用数据库或更安全的存储方式）
VALID_AUTH_CODES = {
    "TEST001": "测试用户1",
    "TEST002": "测试用户2",
    # 添加更多授权码
}

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_code = request.headers.get('Authorization')
        api_key = request.headers.get('X-API-KEY')

        if not auth_code or not api_key:
            return jsonify({
                'success': False,
                'error': '缺少授权信息'
            }), 401

        if auth_code not in VALID_AUTH_CODES:
            return jsonify({
                'success': False,
                'error': '无效的授权码'
            }), 401

        # 将验证信息添加到请求上下文
        request.auth_info = {
            'user_name': VALID_AUTH_CODES[auth_code],
            'auth_code': auth_code,
            'api_key': api_key
        }
        
        return f(*args, **kwargs)
    return decorated

@app.route('/verify', methods=['POST', 'OPTIONS'])
def verify_auth():
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.json
        auth_code = data.get('authCode')
        api_key = data.get('apiKey')

        if not auth_code or not api_key:
            return jsonify({
                'success': False,
                'error': '请提供授权码和API密钥'
            }), 400

        # 验证授权码
        if auth_code not in VALID_AUTH_CODES:
            return jsonify({
                'success': False,
                'error': '无效的授权码'
            }), 401

        # 验证API密钥（调用Moonshot API进行验证）
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            response = requests.get("https://api.moonshot.cn/v1/models", headers=headers)
            response.raise_for_status()
            
            return jsonify({
                'success': True,
                'user_name': VALID_AUTH_CODES[auth_code]
            })
        except requests.exceptions.RequestException as e:
            print(f"API密钥验证失败: {str(e)}")  # 添加日志
            return jsonify({
                'success': False,
                'error': 'API密钥验证失败，请确保输入了正确的Moonshot API密钥'
            }), 401
    except Exception as e:
        print(f"验证过程出错: {str(e)}")  # 添加日志
        return jsonify({
            'success': False,
            'error': f'验证过程出错: {str(e)}'
        }), 500

@app.route('/generate', methods=['POST', 'OPTIONS'])
@require_auth
def generate_story():
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        return '', 204

    data = request.json
    title = data.get('title')
    
    if not title:
        return jsonify({
            'success': False,
            'error': '请提供小说标题'
        }), 400
    
    try:
        # 使用Moonshot API生成故事内容
        prompt = f"""基于小说标题"{title}"，请生成以下内容：
        1. 故事背景
        2. 主要情节线索
        3. 主要人物关系
        请分别详细描述这三个方面。"""
        
        payload = {
            "model": "moonshot-v1-8k",
            "messages": [
                {"role": "system", "content": "你是一个专业的小说策划师，善于构思故事框架和人物关系。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        print(f"用户 '{request.auth_info['user_name']}' 正在为标题 '{title}' 生成故事...")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {request.auth_info['api_key']}"
        }
        
        response = requests.post(
            "https://api.moonshot.cn/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        return jsonify({
            'success': True,
            'result': result['choices'][0]['message']['content']
        })
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'API请求超时，请稍后重试'
        }), 504
    except requests.exceptions.RequestException as e:
        print(f"API请求错误: {str(e)}")  # 添加日志
        return jsonify({
            'success': False,
            'error': f"API请求错误: {str(e)}"
        }), 500
    except Exception as e:
        print(f"生成故事时出错: {str(e)}")  # 添加日志
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'auth_codes_count': len(VALID_AUTH_CODES)
    })

@app.route('/')
def home():
    return jsonify({
        'status': 'healthy',
        'message': 'Novel AI Assistant API is running'
    })

# Vercel 需要的入口
app.debug = False

# 为 PythonAnywhere 添加 WSGI 应用配置
application = app

if __name__ == '__main__':
    if not VALID_AUTH_CODES:
        print("警告: 未设置任何有效的授权码")
    
    app.run(debug=False) 