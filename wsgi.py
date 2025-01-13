import os
import sys

# 添加应用目录到Python路径
path = '/home/willdon2024/novel-ai-assistant'
if path not in sys.path:
    sys.path.append(path)

from app import app as application  # noqa

# 设置Moonshot API密钥
os.environ['MOONSHOT_API_KEY'] = 'your-api-key-here'  # 记得替换成实际的API密钥 