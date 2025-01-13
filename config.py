import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

class Config:
    # Flask配置
    SECRET_KEY = os.urandom(24)
    DEBUG = os.getenv('FLASK_DEBUG', False)

    # Moonshot API配置
    MOONSHOT_API_KEY = os.getenv('MOONSHOT_API_KEY')
    MOONSHOT_API_URL = "https://api.moonshot.cn/v1/chat/completions"

    # CORS配置
    CORS_HEADERS = 'Content-Type' 