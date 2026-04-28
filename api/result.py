"""
Vercel Serverless Function - 查询八字分析结果
"""
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import urllib.request
import urllib.error
import ssl

API_BASE_URL = 'https://baziapi.site'

# 创建SSL上下文
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 从URL中提取taskId
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            task_id = query_params.get('taskId', [None])[0]
            
            if not task_id:
                # 尝试从路径中提取
                path_parts = self.path.split('/')
                if len(path_parts) > 0:
                    task_id = path_parts[-1].split('?')[0]
            
            if not task_id:
                raise ValueError('缺少taskId参数')
            
            # 转发到API服务器
            req = urllib.request.Request(
                f'{API_BASE_URL}/api/bazi/result/{task_id}',
                headers={
                    'Accept': 'application/json',
                    'User-Agent': 'Mozilla/5.0'
                },
                method='GET'
            )
            
            with urllib.request.urlopen(req, timeout=60, context=ssl_context) as response:
                response_data = response.read()
                
                # 返回响应
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                self.wfile.write(response_data)
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = json.dumps({
                'success': False,
                'error': f'代理错误: {str(e)}'
            }, ensure_ascii=False).encode('utf-8')
            self.wfile.write(error_response)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
