from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# Moonshot API配置
MOONSHOT_API_KEY = os.getenv('MOONSHOT_API_KEY')
MOONSHOT_API_URL = "https://api.moonshot.cn/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {MOONSHOT_API_KEY}"
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_story():
    data = request.json
    title = data.get('title')
    
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
        
        response = requests.post(MOONSHOT_API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()  # 检查请求是否成功
        result = response.json()
        
        return jsonify({
            'success': True,
            'result': result['choices'][0]['message']['content']
        })
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f"API请求错误: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 